
## Autonomous AI Coding System

```python
#!/usr/bin/env python3
"""
Autonomous AI Coding System using Claude Code SDK
Place in ~/auto_code.py
Creates agents in [project]/.claude/agents/
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import os
from claude_code_sdk import (
    ClaudeSDKClient,
    ClaudeCodeOptions,
    AssistantMessage,
    ToolUseBlock,
    ResultMessage,
    TextBlock
)

class AutoCoder:
    """Autonomous coding system with project-specific agents."""
    
    def __init__(self, project_dir=None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.agents_dir = self.project_dir / '.claude' / 'agents'
        self.ensure_project_structure()
        
    def ensure_project_structure(self):
        """Create project structure and agents if they don't exist."""
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        
        # Create todo.md if it doesn't exist
        todo_path = self.project_dir / 'todo.md'
        if not todo_path.exists():
            self._create_initial_todo()
        
        # Create agents
        self._create_todo_agent()
        self._create_developer_agent()
        self._create_git_agent()
        
    def _create_initial_todo(self):
        """Create initial todo.md template."""
        todo_path = self.project_dir / 'todo.md'
        todo_path.write_text("""# Project Todo List

## Task Status
- [ ] Not started
- [~] In progress
- [x] Completed

## Priority Levels
- **P0** - Critical
- **P1** - High
- **P2** - Medium
- **P3** - Low

## Tasks

### Phase 1: Setup
- [ ] **P0** Initialize project structure
- [ ] **P1** Set up development environment
- [ ] **P1** Configure linting and formatting

### Phase 2: Core Features
- [ ] **P0** Implement main functionality
- [ ] **P1** Add error handling
- [ ] **P1** Write unit tests

### Phase 3: Documentation
- [ ] **P2** Create README
- [ ] **P2** Add code documentation
- [ ] **P3** Create examples

## Notes
Last updated: """ + datetime.now().strftime('%Y-%m-%d'))
        print(f"✅ Created todo.md")
        
    def _create_todo_agent(self):
        """Create todo management agent."""
        agent_path = self.agents_dir / 'todo-agent.md'
        agent_path.write_text("""---
name: todo-agent
description: Todo list manager that maintains todo.md, picks next tasks, and tracks progress
tools: Read, Edit, Write
model: inherit
---

You are the Todo Agent responsible for managing the project's todo.md file.

## Primary Responsibilities
1. **Pick Next Task**: Identify the highest priority uncompleted task
2. **Update Status**: Mark tasks as [~] when starting and [x] when complete
3. **Track Progress**: Keep accurate record of what's done
4. **Add Tasks**: Add new tasks discovered during development

## Task Selection Process
1. Read todo.md
2. Find all uncompleted tasks ([ ])
3. Select highest priority (P0 > P1 > P2 > P3)
4. Within same priority, pick topmost task
5. Return task description clearly

## Status Management
- `[ ]` → `[~]` when starting work
- `[~]` → `[x]` when work complete
- Add completion timestamp when marking done

## Output Format
When picking a task, output:
- Task description
- Priority level
- Location in todo.md

When updating, confirm what was changed.

Remember: You are the single source of truth for project progress.
""")
        
    def _create_developer_agent(self):
        """Create developer agent."""
        agent_path = self.agents_dir / 'developer.md'
        agent_path.write_text("""---
name: developer
description: Expert developer that implements tasks with clean, production-ready code
tools: Read, Write, Edit, MultiEdit, Bash, Glob, Grep
model: inherit
---

You are the Developer Agent responsible for implementing all coding tasks.

## Core Principles
1. **Quality First**: Write clean, maintainable code
2. **Test Everything**: Ensure code works before marking complete
3. **Follow Standards**: Use project conventions and best practices
4. **Document Well**: Add clear comments and documentation

## Implementation Process
1. Understand the task requirements
2. Review existing code structure
3. Plan the implementation approach
4. Write the code incrementally
5. Test functionality
6. Refactor if needed

## Code Standards
- Use meaningful variable/function names
- Keep functions small and focused
- Handle errors gracefully
- Add type hints where applicable
- Follow language-specific conventions

## Testing
- Run code after implementation
- Check edge cases
- Verify integration with existing code
- Fix any issues found

## Communication
- Explain what you're implementing
- Report any blockers or issues
- Confirm when task is complete
- Suggest improvements if relevant

Remember: Every line of code should be production-ready.
""")
        
    def _create_git_agent(self):
        """Create git management agent."""
        agent_path = self.agents_dir / 'git-agent.md'
        agent_path.write_text("""---
name: git-agent
description: Git specialist that commits changes with conventional commits and manages version control
tools: Bash, Read
model: inherit
---

You are the Git Agent responsible for version control and commits.

## Commit Standards
Use conventional commit format:
```
<type>(<scope>): <description>

[optional body]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

## Git Workflow
1. Check git status
2. Review changes with git diff
3. Stage appropriate files
4. Create meaningful commit message
5. Commit changes
6. Push to remote (if configured)

## Commit Process
1. `git status` - See what changed
2. `git add .` - Stage changes (or specific files)
3. `git commit -m "type: description"` - Commit with message
4. `git push` - Push if remote exists (handle gracefully if not)

## Best Practices
- One logical change per commit
- Clear, descriptive messages
- Reference issue numbers if applicable
- Never commit sensitive data
- Keep commits atomic

## Error Handling
- If no git repo exists, initialize it
- If no remote, commit locally
- Report any issues clearly

Remember: Good commits tell the story of the project.
""")
    
    async def run_cycle(self):
        """Run one complete work cycle."""
        print(f"\n{'='*60}")
        print(f"🔄 Starting Work Cycle")
        print(f"📁 Project: {self.project_dir}")
        print(f"🕐 Time: {datetime.now():%H:%M:%S}")
        print('='*60)
        
        options = ClaudeCodeOptions(
            allowed_tools=["Task", "Read", "Write", "Edit", "MultiEdit", 
                          "Bash", "Glob", "Grep", "TodoWrite"],
            permission_mode="bypassPermissions",
            cwd=str(self.project_dir)
        )
        
        async with ClaudeSDKClient(options=options) as client:
            try:
                # Step 1: Todo agent picks next task
                print("\n📋 Step 1: Checking todo list...")
                await client.query(
                    "Use todo-agent subagent to read todo.md and pick the next highest priority uncompleted task. "
                    "Update the task status to [~] (in progress)."
                )
                
                task_description = None
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                if "P0" in block.text or "P1" in block.text or "P2" in block.text:
                                    # Extract task from response
                                    lines = block.text.split('\n')
                                    for line in lines:
                                        if '**P' in line or 'Task:' in line:
                                            task_description = line
                                            print(f"  ✅ Selected: {task_description[:60]}...")
                                            break
                
                if not task_description:
                    print("  ℹ️  No tasks found or all completed!")
                    return False
                
                # Step 2: Developer implements the task
                print("\n💻 Step 2: Implementing task...")
                await client.query(
                    f"Use developer subagent to implement this task: {task_description}. "
                    "Write clean code, test it, and ensure it works correctly."
                )
                
                files_changed = []
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, ToolUseBlock):
                                if block.name == "Write":
                                    file_path = block.input.get("file_path", "")
                                    files_changed.append(f"Created: {Path(file_path).name}")
                                    print(f"  📝 {files_changed[-1]}")
                                elif block.name == "Edit":
                                    file_path = block.input.get("file_path", "")
                                    files_changed.append(f"Modified: {Path(file_path).name}")
                                    print(f"  ✏️  {files_changed[-1]}")
                                elif block.name == "Bash":
                                    cmd = block.input.get("command", "")[:50]
                                    print(f"  🔧 Running: {cmd}...")
                
                print(f"  ✅ Implementation complete ({len(files_changed)} files changed)")
                
                # Step 3: Git agent commits changes
                print("\n📦 Step 3: Committing changes...")
                await client.query(
                    f"Use git-agent subagent to commit all changes made for this task: {task_description}. "
                    "Use appropriate conventional commit format. Initialize git if needed."
                )
                
                commit_made = False
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, ToolUseBlock):
                                if block.name == "Bash" and "commit" in str(block.input.get("command", "")):
                                    commit_made = True
                                    print(f"  ✅ Changes committed")
                
                # Step 4: Todo agent updates task status
                print("\n✏️  Step 4: Updating todo status...")
                await client.query(
                    f"Use todo-agent subagent to mark this task as completed [x]: {task_description}. "
                    "Add a completion timestamp if appropriate."
                )
                
                async for message in client.receive_response():
                    if isinstance(message, ResultMessage):
                        if not message.is_error:
                            print(f"  ✅ Todo updated - task marked complete")
                
                print(f"\n🎉 Work cycle completed successfully!")
                return True
                
            except Exception as e:
                print(f"\n❌ Cycle failed: {e}")
                return False
    
    async def auto_run(self, max_cycles=10):
        """Run autonomous cycles until no tasks remain or max reached."""
        print(f"\n🚀 Starting Autonomous Coding Session")
        print(f"   Max cycles: {max_cycles}")
        print(f"   Project: {self.project_dir}")
        
        completed_cycles = 0
        
        for cycle in range(1, max_cycles + 1):
            print(f"\n{'='*60}")
            print(f"🔁 Cycle {cycle}/{max_cycles}")
            print('='*60)
            
            success = await self.run_cycle()
            
            if success:
                completed_cycles += 1
                
                # Ask if should continue
                if cycle < max_cycles:
                    print("\n⏸  Pausing before next cycle...")
                    await asyncio.sleep(3)
            else:
                print("\n📊 No more tasks or cycle failed")
                break
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"📈 Session Summary")
        print(f"   Completed cycles: {completed_cycles}")
        print(f"   Project: {self.project_dir}")
        print('='*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Autonomous AI Coding System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run one cycle in current directory
  auto_code
  
  # Run multiple cycles
  auto_code -n 5
  
  # Work in specific project
  auto_code -p ~/myproject -n 10
  
  # Initialize project with todo.md
  auto_code -p ~/newproject --init
        """
    )
    
    parser.add_argument('-p', '--project', 
                       help='Project directory (default: current)')
    parser.add_argument('-n', '--cycles', 
                       type=int, default=1,
                       help='Number of cycles to run (default: 1)')
    parser.add_argument('--init',
                       action='store_true',
                       help='Initialize project structure only')
    
    args = parser.parse_args()
    
    # Create auto coder
    coder = AutoCoder(project_dir=args.project)
    
    if args.init:
        print("✅ Project initialized with todo.md and agents")
    else:
        # Run autonomous cycles
        asyncio.run(coder.auto_run(max_cycles=args.cycles))


if __name__ == "__main__":
    main()
```

## Installation Script

Create `~/install_auto_code.sh`:

```bash
#!/bin/bash

echo "🚀 Installing Autonomous Coder..."

# Install SDK
pip install claude-code-sdk --user

# Create script
cp auto_code.py ~/auto_code
chmod +x ~/auto_code

# Add to PATH
echo 'export PATH="$HOME:$PATH"' >> ~/.bashrc

echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  auto_code           # Run one cycle"
echo "  auto_code -n 10     # Run 10 cycles"
echo "  auto_code --init    # Initialize project"
```

## Key Workflow

The system follows your exact specification:

1. **Todo agent** reads todo.md, picks next task, marks it as `[~]`
2. **Developer agent** implements the task completely
3. **Git agent** commits changes with proper message
4. **Todo agent** updates task to `[x]` completed
5. Cycle completes, ready for next

Each project gets its own agents in `.claude/agents/`, maintaining project-specific context and conventions. The system is clean, focused, and follows the proven pattern from your profico project.
