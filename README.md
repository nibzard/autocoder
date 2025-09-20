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

### Standard Usage (Anthropic Claude)

```bash
uvx git+https://github.com/nibzard/autocoder
# Output: 🌐 API: Anthropic Claude (default)
```

### With Zhipu GLM-4.5

```bash
# Create .env file
echo "ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic" > .env
echo "ANTHROPIC_AUTH_TOKEN=your_zhipu_api_key" >> .env

# Run autocoder - automatically detects Zhipu
uvx git+https://github.com/nibzard/autocoder
# Output: 🌐 API: Zhipu (GLM-4.5) (https://api.z.ai/api/anthropic)
```

### Installation

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

Autocoder intelligently adapts to any todo.md format. It works with simple checkboxes or complex project management formats:

#### Simple Format
```markdown
# Todo List
- [ ] **P0** Critical task
- [ ] **P1** High priority task  
- [x] **P2** Completed task
```

#### Complex Format (like your ProfiCo project)
```markdown
# Project Todo List

## Phase 2: Core Features - PARTIALLY COMPLETED ⚠️

### 👥 User Management
- [✅] 🔴 **P0** Create user dashboard **@claude** *(needs refinement)*
- [ ] 🟡 **P1** Build admin user management interface **@claude**
- [!] 🟡 **P1** Create team hierarchy *(blocked on API design)*
- [❌] 🟢 **P2** Add user photos *(failed implementation)*
```

#### Supported Status Markers
- `[ ]` - Not started
- `[~]` - In progress  
- `[x]` - Completed
- `[!]` - Blocked/needs attention
- `[❌]` - Failed implementation
- `[✅]` - Completed but needs verification

#### Priority Detection
Autocoder understands priority however you express it:
- **P0**, **P1**, **P2**, **P3** 
- 🔴 **P0 (Critical)**, 🟡 **P1 (High)**, 🟢 **P2 (Medium)**, 🔵 **P3 (Low)**
- **Critical**, **High Priority**, **Important**, etc.
- Context-based urgency from language

## Requirements

- Python 3.8+
- Claude Code Python SDK (automatically installed)
- Git repository (initialized automatically if needed)

## API Configuration

Autocoder automatically detects and uses custom API configurations from `.env` files in your project directory. This allows you to use alternative Claude-compatible endpoints with zero configuration changes.

### Supported Endpoints

| Provider | Configuration | API Display |
|----------|---------------|-------------|
| **Anthropic Claude** | None needed (default) | `🌐 API: Anthropic Claude (default)` |
| **Zhipu GLM-4.5** | Set `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic` | `🌐 API: Zhipu (GLM-4.5) (https://api.z.ai/api/anthropic)` |
| **AWS Bedrock** | Set `ANTHROPIC_BASE_URL` + AWS credentials | `🌐 API: AWS Bedrock (your-endpoint)` |
| **Google Vertex AI** | Set `ANTHROPIC_BASE_URL` + Vertex project ID | `🌐 API: Google Vertex AI (your-endpoint)` |
| **Custom API** | Set `ANTHROPIC_BASE_URL` to any endpoint | `🌐 API: Custom API (your-endpoint)` |

### Quick Configuration Examples

#### Zhipu GLM-4.5
```bash
# .env
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
ANTHROPIC_AUTH_TOKEN=your_zhipu_api_key_here
ANTHROPIC_MODEL=glm-4.5
API_TIMEOUT_MS=300000
```

#### AWS Bedrock
```bash
# .env
ANTHROPIC_BASE_URL=https://bedrock-runtime.us-east-1.amazonaws.com
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

#### Custom Endpoint
```bash
# .env
ANTHROPIC_BASE_URL=https://your-custom-endpoint.com/api
ANTHROPIC_API_KEY=your_custom_api_key
ANTHROPIC_MODEL=your_preferred_model
```

### Configuration Templates

Copy and customize from `.env.example`:

```bash
cp .env.example .env
# Edit .env with your credentials
```

The `.env.example` file contains complete templates for all supported endpoints with detailed comments.

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_BASE_URL` | Custom API endpoint URL | `https://api.z.ai/api/anthropic` |
| `ANTHROPIC_API_KEY` | API key for Anthropic/custom endpoints | `sk-ant-...` |
| `ANTHROPIC_AUTH_TOKEN` | Alternative to API_KEY (Zhipu format) | `your_zhipu_key` |
| `ANTHROPIC_MODEL` | Override default model | `glm-4.5`, `claude-3-5-sonnet` |
| `API_TIMEOUT_MS` | Timeout for slower endpoints | `300000` (5 minutes) |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `VERTEX_PROJECT_ID` | Google Cloud project ID | `your-project-123` |

## Example Workflow

1. Create a project with `todo.md`
2. Run `autocoder -n 10`
3. Watch Claude work through your todo list automatically
4. Each task gets its own commit with proper conventional commit format
5. Continue until all tasks are complete

Perfect for autonomous development sessions where you want Claude to systematically work through a project roadmap.