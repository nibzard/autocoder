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
import subprocess
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
        """Setup enhanced logging to ~/.autocoder/logs/"""
        home_dir = Path.home()
        log_dir = home_dir / '.autocoder' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"autocoder-{datetime.now().strftime('%Y-%m-%d')}.log"
        
        # Create logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create file handler with enhanced format
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
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
    
    def get_latest_commit_info(self):
        """Get latest commit hash and attempt to generate GitHub link."""
        try:
            # Get latest commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None, "No git repository or commits found"
                
            commit_hash = result.stdout.strip()
            short_hash = commit_hash[:7]
            
            # Try to get GitHub URL using gh CLI
            try:
                gh_result = subprocess.run(
                    ['gh', 'repo', 'view', '--json', 'url'],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if gh_result.returncode == 0:
                    import json
                    repo_data = json.loads(gh_result.stdout)
                    repo_url = repo_data.get('url', '')
                    if repo_url:
                        commit_url = f"{repo_url}/commit/{commit_hash}"
                        return {
                            'hash': commit_hash,
                            'short_hash': short_hash,
                            'url': commit_url
                        }, None
                        
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                pass
            
            # Fallback: just return hash info
            return {
                'hash': commit_hash,
                'short_hash': short_hash,
                'url': None
            }, None
            
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return None, f"Git command failed: {e}"
    
    def log_detailed(self, level, message, **kwargs):
        """Enhanced logging with additional context."""
        # Add project context to log message
        project_name = self.project_dir.name
        enhanced_message = f"[{project_name}] {message}"
        
        # Add any additional context
        if kwargs:
            context_parts = []
            for key, value in kwargs.items():
                context_parts.append(f"{key}={value}")
            if context_parts:
                enhanced_message += f" ({', '.join(context_parts)})"
        
        if level == 'info':
            logging.info(enhanced_message)
        elif level == 'error':
            logging.error(enhanced_message)
        elif level == 'warning':
            logging.warning(enhanced_message)
    
    async def run_cycle(self):
        """Run one complete work cycle."""
        cycle_start_time = time.time()
        timestamp = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"🔄 Starting Work Cycle")
        print(f"📁 Project: {self.project_dir}")
        print(f"🕐 Time: {timestamp:%H:%M:%S}")
        
        # Log cycle start
        self.log_detailed('info', f"Starting new work cycle", 
                         timestamp=timestamp.isoformat(),
                         project_dir=str(self.project_dir))
        
        # Display API configuration
        api_info = self.config.get_api_info()
        if api_info['custom']:
            print(f"🌐 API: {api_info['provider']} ({api_info['endpoint']})")
            if 'model' in api_info:
                print(f"🤖 Model: {api_info['model']}")
            self.log_detailed('info', f"Using custom API configuration",
                             provider=api_info['provider'],
                             endpoint=api_info['endpoint'],
                             model=api_info.get('model', 'default'))
        else:
            print(f"🌐 API: {api_info['provider']}")
            self.log_detailed('info', f"Using default API configuration",
                             provider=api_info['provider'])
        
        print('='*60)
        
        try:
            # Configure options for Claude Code SDK
            options = ClaudeCodeOptions(
                cwd=str(self.project_dir),
                allowed_tools=["Task", "Read", "Write", "Edit", "MultiEdit", "Bash", "Glob", "Grep"],
                permission_mode="bypassPermissions"
            )
            
            # Use ClaudeSDKClient for conversation continuity
            async with ClaudeSDKClient(options=options) as client:
                # Step 1: Todo agent picks next task
                print("\n📋 Step 1: Checking todo list...")
                print("  🔍 Analyzing todo.md...")
                
                step1_start = time.time()
                self.log_detailed('info', "Step 1: Starting todo analysis")
                
                await client.query(
                    "Use todo-agent subagent to review the status of todo.md, pick the next uncompleted task with highest priority, and mark it as [~] in progress. DO NOT ask for confirmation - start working on the task immediately."
                )
                
                print("  ⚙️  Processing response...")
                # Check result using SDK's built-in status
                task_selected = False
                selected_task = None
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        # Log full response for user to check later
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                # Extract task information from the response
                                task_text = block.text
                                self.log_detailed('info', f"Step 1 Response: {task_text}")
                                
                                # Try to extract the actual task being worked on
                                if "marking" in task_text.lower() or "selected" in task_text.lower():
                                    lines = task_text.split('\n')
                                    for line in lines:
                                        if '[~]' in line or 'task:' in line.lower():
                                            selected_task = line.strip()
                                            break
                                            
                    elif isinstance(message, ResultMessage):
                        task_selected = not message.is_error
                        step1_time = time.time() - step1_start
                        if task_selected:
                            print(f"  ✅ Task selected ({step1_time:.1f}s)")
                            self.log_detailed('info', f"Step 1: Task selected successfully", 
                                            duration=f"{step1_time:.1f}s",
                                            task=selected_task or "Task details in response above")
                        else:
                            print(f"  ℹ️  No tasks found or all completed! ({step1_time:.1f}s)")
                            self.log_detailed('info', f"Step 1: No tasks available", 
                                            duration=f"{step1_time:.1f}s",
                                            reason="No uncompleted tasks found")
                        break
                
                if not task_selected:
                    return False
                
                # Step 2: Implement the task
                print("\n💻 Step 2: Implementing task...")
                step2_start = time.time()
                self.log_detailed('info', "Step 2: Starting task implementation",
                                task=selected_task or "Task from Step 1")
                
                await client.query(
                    "Implement the task that was just selected from todo.md. Write clean code, test it, and ensure it works correctly. Start working immediately - DO NOT ask for permission or confirmation."
                )
                
                # Wait for implementation to complete
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        # Log implementation details
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                # Only log first 200 chars to avoid spam
                                impl_summary = block.text[:200] + "..." if len(block.text) > 200 else block.text
                                self.log_detailed('info', f"Step 2 Implementation: {impl_summary}")
                    elif isinstance(message, ResultMessage):
                        step2_time = time.time() - step2_start
                        if message.is_error:
                            print(f"  ❌ Implementation failed ({step2_time:.1f}s)")
                            self.log_detailed('error', f"Step 2: Implementation failed",
                                            duration=f"{step2_time:.1f}s",
                                            error=str(message.result))
                            return False
                        else:
                            print(f"  ✅ Implementation complete ({step2_time:.1f}s)")
                            self.log_detailed('info', f"Step 2: Implementation completed successfully",
                                            duration=f"{step2_time:.1f}s")
                        break
                
                # Step 3: Git agent commits changes
                print("\n📦 Step 3: Committing changes...")
                step3_start = time.time()
                self.log_detailed('info', "Step 3: Starting git commit process")
                
                await client.query(
                    "Use git-agent subagent to commit all changes made for the implemented task. Use appropriate conventional commit format. Execute immediately - DO NOT ask for permission."
                )
                
                # Wait for commit to complete
                commit_message = None
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        # Extract commit message for logging
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                text = block.text
                                # Look for commit messages in the response
                                if 'git commit' in text and '-m' in text:
                                    # Extract commit message
                                    import re
                                    commit_match = re.search(r'git commit.*?-m\s*["\']([^"\']+)["\']', text)
                                    if commit_match:
                                        commit_message = commit_match.group(1)
                                
                    elif isinstance(message, ResultMessage):
                        step3_time = time.time() - step3_start
                        if message.is_error:
                            print(f"  ❌ Commit failed ({step3_time:.1f}s)")
                            self.log_detailed('error', f"Step 3: Git commit failed",
                                            duration=f"{step3_time:.1f}s",
                                            error=str(message.result))
                            return False
                        else:
                            print(f"  ✅ Changes committed ({step3_time:.1f}s)")
                            
                            # Get commit info and log with link if available
                            commit_info, error = self.get_latest_commit_info()
                            if commit_info:
                                if commit_info['url']:
                                    print(f"  🔗 Commit: {commit_info['url']}")
                                    self.log_detailed('info', f"Step 3: Git commit successful with GitHub link",
                                                    duration=f"{step3_time:.1f}s",
                                                    commit_hash=commit_info['short_hash'],
                                                    commit_url=commit_info['url'],
                                                    commit_message=commit_message or "See git log")
                                else:
                                    print(f"  📝 Commit: {commit_info['short_hash']}")
                                    self.log_detailed('info', f"Step 3: Git commit successful",
                                                    duration=f"{step3_time:.1f}s",
                                                    commit_hash=commit_info['short_hash'],
                                                    commit_message=commit_message or "See git log")
                            else:
                                self.log_detailed('info', f"Step 3: Git commit completed",
                                                duration=f"{step3_time:.1f}s",
                                                commit_message=commit_message or "See git log",
                                                note=error or "Could not retrieve commit info")
                        break
                
                # Step 4: Todo agent updates task status
                print("\n✏️  Step 4: Updating todo status...")
                step4_start = time.time()
                self.log_detailed('info', "Step 4: Starting todo status update")
                
                await client.query(
                    "Use todo-agent subagent to mark the just-implemented task as completed in todo.md. Use the appropriate completion format for this project. Execute immediately - DO NOT ask for permission."
                )
                
                # Wait for todo update to complete
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        # Log todo update details
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                text = block.text
                                # Look for completion markers
                                if '[x]' in text or 'completed' in text.lower():
                                    update_summary = text[:150] + "..." if len(text) > 150 else text
                                    self.log_detailed('info', f"Step 4 Update: {update_summary}")
                                    
                    elif isinstance(message, ResultMessage):
                        step4_time = time.time() - step4_start
                        if message.is_error:
                            print(f"  ❌ Todo update failed ({step4_time:.1f}s)")
                            self.log_detailed('error', f"Step 4: Todo update failed",
                                            duration=f"{step4_time:.1f}s",
                                            error=str(message.result))
                            return False
                        else:
                            print(f"  ✅ Todo updated ({step4_time:.1f}s)")
                            self.log_detailed('info', f"Step 4: Todo status updated successfully",
                                            duration=f"{step4_time:.1f}s")
                        break
                
                # Calculate total cycle time
                total_cycle_time = time.time() - cycle_start_time
                print(f"\n🎉 Work cycle completed successfully!")
                
                self.log_detailed('info', f"Work cycle completed successfully",
                                total_duration=f"{total_cycle_time:.1f}s",
                                task_completed=selected_task or "Task from Step 1")
                
                return True
                
        except Exception as e:
            total_cycle_time = time.time() - cycle_start_time
            print(f"\n❌ Cycle failed: {e}")
            self.log_detailed('error', f"Work cycle failed with exception",
                            total_duration=f"{total_cycle_time:.1f}s",
                            error=str(e),
                            exception_type=type(e).__name__)
            return False
    
    async def auto_run(self, max_cycles=10):
        """Run autonomous cycles until no tasks remain or max reached."""
        session_start_time = time.time()
        session_timestamp = datetime.now()
        
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
        
        # Log session start
        self.log_detailed('info', f"Starting autonomous coding session",
                         session_timestamp=session_timestamp.isoformat(),
                         max_cycles=max_cycles,
                         project_dir=str(self.project_dir),
                         api_provider=api_info['provider'])
        
        completed_cycles = 0
        
        for cycle in range(1, max_cycles + 1):
            print(f"\n{'='*60}")
            print(f"🔁 Cycle {cycle}/{max_cycles}")
            print('='*60)
            
            cycle_start = time.time()
            self.log_detailed('info', f"Starting cycle {cycle}/{max_cycles}")
            
            success = await self.run_cycle()
            
            cycle_time = time.time() - cycle_start
            
            if success:
                completed_cycles += 1
                self.log_detailed('info', f"Cycle {cycle} completed successfully",
                                cycle_duration=f"{cycle_time:.1f}s",
                                cycles_completed=completed_cycles)
                
                # Pause before next cycle
                if cycle < max_cycles:
                    print("\n⏸  Pausing before next cycle...")
                    await asyncio.sleep(3)
            else:
                print("\n📊 No more tasks or cycle failed")
                self.log_detailed('info', f"Session ended after cycle {cycle}",
                                reason="No tasks available or cycle failed",
                                cycles_completed=completed_cycles)
                break
        
        # Calculate total session time
        total_session_time = time.time() - session_start_time
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"📈 Session Summary")
        print(f"   Completed cycles: {completed_cycles}")
        print(f"   Project: {self.project_dir}")
        print('='*60)
        
        # Log session completion
        self.log_detailed('info', f"Autonomous coding session completed",
                         total_duration=f"{total_session_time:.1f}s",
                         cycles_completed=completed_cycles,
                         cycles_requested=max_cycles,
                         success_rate=f"{(completed_cycles/max_cycles)*100:.1f}%")


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