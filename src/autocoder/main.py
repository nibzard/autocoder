#!/usr/bin/env python3
"""
Autocoder - Autonomous coding tool using Claude Code Python SDK
"""

import asyncio
import sys
import os
import shutil
import logging
import time
from pathlib import Path
from datetime import datetime

try:
    from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions, AssistantMessage, TextBlock, ResultMessage
except ImportError:
    print("❌ Claude Code Python SDK not found. Please install it:")
    print("   pip install claude-code-sdk")
    sys.exit(1)

from .config import AutocoderConfig


class Autocoder:
    """Autonomous coding system with project-specific agents."""
    
    def __init__(self, project_dir=None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.agents_dir = self.project_dir / '.claude' / 'agents'
        self.config = AutocoderConfig(self.project_dir)
        self.setup_logging()
        self.ensure_project_structure()
        
    def setup_logging(self):
        """Setup logging to ~/.autocoder/logs/"""
        home_dir = Path.home()
        log_dir = home_dir / '.autocoder' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"autocoder-{datetime.now().strftime('%Y-%m-%d')}.log"
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='a'
        )
        
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
        todo_content = f"""# Project Todo List

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
Last updated: {datetime.now().strftime('%Y-%m-%d')}
"""
        todo_path.write_text(todo_content)
        print(f"✅ Created todo.md")
        
    def _create_todo_agent(self):
        """Create todo management agent."""
        agent_path = self.agents_dir / 'todo-agent.md'
        if agent_path.exists():
            return
            
        agent_content = """---
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
"""
        agent_path.write_text(agent_content)
        print(f"✅ Created todo-agent.md")
        
    def _create_developer_agent(self):
        """Create developer agent."""
        agent_path = self.agents_dir / 'developer.md'
        if agent_path.exists():
            return
            
        agent_content = """---
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
"""
        agent_path.write_text(agent_content)
        print(f"✅ Created developer.md")
        
    def _create_git_agent(self):
        """Create git management agent."""
        agent_path = self.agents_dir / 'git-agent.md'
        if agent_path.exists():
            return
            
        agent_content = """---
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
"""
        agent_path.write_text(agent_content)
        print(f"✅ Created git-agent.md")
    
    async def run_cycle(self):
        """Run one complete work cycle."""
        print(f"\n{'='*60}")
        print(f"🔄 Starting Work Cycle")
        print(f"📁 Project: {self.project_dir}")
        print(f"🕐 Time: {datetime.now():%H:%M:%S}")
        
        # Display API configuration
        api_info = self.config.get_api_info()
        if api_info['custom']:
            print(f"🌐 API: {api_info['provider']} ({api_info['endpoint']})")
            if 'model' in api_info:
                print(f"🤖 Model: {api_info['model']}")
        else:
            print(f"🌐 API: {api_info['provider']}")
        
        print('='*60)
        
        try:
            # Configure options for Claude Code SDK
            options = ClaudeCodeOptions(
                cwd=str(self.project_dir),
                allowed_tools=["Task", "Read", "Write", "Edit", "MultiEdit", "Bash", "Glob", "Grep"],
                permission_mode="acceptEdits"
            )
            
            # Use ClaudeSDKClient for conversation continuity
            async with ClaudeSDKClient(options=options) as client:
                # Step 1: Todo agent picks next task
                print("\n📋 Step 1: Checking todo list...")
                print("  🔍 Analyzing todo.md...")
                step1_start = time.time()
                await client.query(
                    "Use todo-agent subagent to review the status of todo.md, pick the next uncompleted task with highest priority, and mark it as [~] in progress."
                )
                
                print("  ⚙️  Processing response...")
                # Check result using SDK's built-in status
                task_selected = False
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        # Log full response for user to check later
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                logging.info(f"Step 1 Response: {block.text}")
                    elif isinstance(message, ResultMessage):
                        task_selected = not message.is_error
                        step1_time = time.time() - step1_start
                        if task_selected:
                            print(f"  ✅ Task selected ({step1_time:.1f}s)")
                        else:
                            print(f"  ℹ️  No tasks found or all completed! ({step1_time:.1f}s)")
                        logging.info(f"Step 1 result: success={task_selected}, duration={step1_time:.1f}s")
                        break
                
                if not task_selected:
                    return False
                
                # Step 2: Implement the task
                print("\n💻 Step 2: Implementing task...")
                step2_start = time.time()
                await client.query(
                    "Implement the task that was just selected from todo.md. Write clean code, test it, and ensure it works correctly."
                )
                
                # Wait for implementation to complete
                async for message in client.receive_response():
                    if isinstance(message, ResultMessage):
                        step2_time = time.time() - step2_start
                        if message.is_error:
                            print(f"  ❌ Implementation failed ({step2_time:.1f}s)")
                            logging.error(f"Step 2 failed: {message.result}")
                            return False
                        else:
                            print(f"  ✅ Implementation complete ({step2_time:.1f}s)")
                            logging.info(f"Step 2 success: duration={step2_time:.1f}s")
                        break
                
                # Step 3: Git agent commits changes
                print("\n📦 Step 3: Committing changes...")
                step3_start = time.time()
                await client.query(
                    "Use git-agent subagent to commit all changes made for the implemented task. Use appropriate conventional commit format."
                )
                
                # Wait for commit to complete
                async for message in client.receive_response():
                    if isinstance(message, ResultMessage):
                        step3_time = time.time() - step3_start
                        if message.is_error:
                            print(f"  ❌ Commit failed ({step3_time:.1f}s)")
                            logging.error(f"Step 3 failed: {message.result}")
                            return False
                        else:
                            print(f"  ✅ Changes committed ({step3_time:.1f}s)")
                            logging.info(f"Step 3 success: duration={step3_time:.1f}s")
                        break
                
                # Step 4: Todo agent updates task status
                print("\n✏️  Step 4: Updating todo status...")
                step4_start = time.time()
                await client.query(
                    "Use todo-agent subagent to mark the just-implemented task as completed in todo.md. Use the appropriate completion format for this project."
                )
                
                # Wait for todo update to complete
                async for message in client.receive_response():
                    if isinstance(message, ResultMessage):
                        step4_time = time.time() - step4_start
                        if message.is_error:
                            print(f"  ❌ Todo update failed ({step4_time:.1f}s)")
                            logging.error(f"Step 4 failed: {message.result}")
                            return False
                        else:
                            print(f"  ✅ Todo updated ({step4_time:.1f}s)")
                            logging.info(f"Step 4 success: duration={step4_time:.1f}s")
                        break
                
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
        
        # Show log file location
        log_file = Path.home() / '.autocoder' / 'logs' / f"autocoder-{datetime.now().strftime('%Y-%m-%d')}.log"
        print(f"   Logs: {log_file}")
        
        # Show API configuration once at the start
        api_info = self.config.get_api_info()
        if api_info['custom']:
            print(f"   Using: {api_info['provider']} via {api_info['endpoint']}")
            if 'model' in api_info:
                print(f"   Model: {api_info['model']}")
        else:
            print(f"   Using: {api_info['provider']} (default)")
        print()
        
        completed_cycles = 0
        
        for cycle in range(1, max_cycles + 1):
            print(f"\n{'='*60}")
            print(f"🔁 Cycle {cycle}/{max_cycles}")
            print('='*60)
            
            success = await self.run_cycle()
            
            if success:
                completed_cycles += 1
                
                # Pause before next cycle
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
  autocoder
  
  # Run multiple cycles
  autocoder -n 5
  
  # Work in specific project
  autocoder -p ~/myproject -n 10
  
  # Initialize project with todo.md
  autocoder -p ~/newproject --init
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
    coder = Autocoder(project_dir=args.project)
    
    if args.init:
        # Show configuration even during init
        api_info = coder.config.get_api_info()
        if api_info['custom']:
            print(f"🌐 Detected API: {api_info['provider']} ({api_info['endpoint']})")
            if 'model' in api_info:
                print(f"🤖 Model: {api_info['model']}")
        print("✅ Project initialized with todo.md and agents")
    else:
        # Run autonomous cycles
        asyncio.run(coder.auto_run(max_cycles=args.cycles))


if __name__ == "__main__":
    main()