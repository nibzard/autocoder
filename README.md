# Autocoder

Autonomous coding tool using Claude Code SDK that automatically works through your todo list.

## Overview

Autocoder creates a self-sustaining development loop where Claude continuously works through tasks in your `todo.md` file:

1. **Todo agent** reads `todo.md`, picks the next highest priority task, marks it as `[~]` (in progress)
2. **Developer agent** implements the task with clean, tested code
3. **Git agent** commits changes with conventional commit messages
4. **Todo agent** updates the task to `[x]` (completed)
5. Loop repeats until all tasks are done

## Quick Start

Run autocoder directly from GitHub without installation:

```bash
uvx git+https://github.com/nibzard/autocoder
```

Or install it:

```bash
uv tool install git+https://github.com/nibzard/autocoder
autocoder
```

## Usage

```bash
# Run one cycle in current directory
autocoder

# Run multiple cycles
autocoder -n 5

# Work in specific project
autocoder -p ~/myproject -n 10

# Initialize project with todo.md and agents
autocoder --init
```

## How It Works

### Sub-Agents

Autocoder creates specialized Claude Code sub-agents in `.claude/agents/`:

- **todo-agent.md**: Manages todo.md, picks tasks by priority (P0 > P1 > P2 > P3)
- **developer.md**: Implements tasks with production-ready code
- **git-agent.md**: Creates conventional commits and pushes changes

### Todo Format

Your `todo.md` should use this format:

```markdown
# Project Todo List

## Tasks

### Phase 1: Setup
- [ ] **P0** Critical task
- [ ] **P1** High priority task
- [~] **P1** Currently working on this
- [x] **P2** Completed task

### Phase 2: Features
- [ ] **P0** Another critical task
```

Priority levels: **P0** (Critical) > **P1** (High) > **P2** (Medium) > **P3** (Low)

## Requirements

- Python 3.8+
- Claude Code Python SDK (automatically installed)
- Git repository (initialized automatically if needed)

## Configuration

Autocoder automatically detects and uses custom API configurations from `.env` files. This allows you to use alternative Claude-compatible endpoints.

### Using Zhipu GLM-4.5

Create a `.env` file in your project directory:

```bash
# .env
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
ANTHROPIC_AUTH_TOKEN=your_zhipu_api_key_here
ANTHROPIC_MODEL=glm-4.5
API_TIMEOUT_MS=300000
```

Then run autocoder normally - it will automatically detect and use Zhipu:

```bash
uvx git+https://github.com/nibzard/autocoder
# Output: 🌐 API: Zhipu (GLM-4.5) (https://api.z.ai/api/anthropic)
```

### Other Supported Endpoints

- **AWS Bedrock**: Set `ANTHROPIC_BASE_URL` and AWS credentials
- **Google Vertex AI**: Set `ANTHROPIC_BASE_URL` and Vertex project ID  
- **Custom Endpoints**: Any Claude-compatible API

See `.env.example` for complete configuration templates.

### Default Behavior

Without any `.env` file, autocoder uses Anthropic's official API:
```bash
uvx git+https://github.com/nibzard/autocoder
# Output: 🌐 API: Anthropic Claude (default)
```

## Example Workflow

1. Create a project with `todo.md`
2. Run `autocoder -n 10`
3. Watch Claude work through your todo list automatically
4. Each task gets its own commit with proper conventional commit format
5. Continue until all tasks are complete

Perfect for autonomous development sessions where you want Claude to systematically work through a project roadmap.