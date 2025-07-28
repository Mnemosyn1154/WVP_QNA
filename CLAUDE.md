## Gemini CLI 연동 가이드

### 목적
사용자가 「Gemini와 상의하면서 진행해줘」 (또는 유사한 표현)라고 지시할 경우, Claude는 이후 작업을 Gemini CLI와 협력하여 진행한다.
Gemini로부터 받은 응답은 그대로 보여주고, Claude의 해설이나 통합 설명을 덧붙여 두 에이전트의 지식을 결합한다.

### 트리거
- 정규표현식: `/Gem.*상의하면서/`
- 예시:
  - 「Gem과 상의하면서 진행해줘」
  - 「이건 Gemini랑 이야기하면서 하자」

### Gemini CLI 사용법
```bash
# 기본 사용법
gemini -p "프롬프트 내용"

# 파일을 컨텍스트로 제공
gemini -p "프롬프트 내용" < input_file.md

# 여러 줄 프롬프트 (heredoc 사용)
export PROMPT="여러 줄의
프롬프트 내용"
gemini <<EOF
$PROMPT
EOF

# 주요 옵션
# -m, —model: 모델 선택 (기본: gemini-2.5-pro)
# -p, —prompt: 프롬프트 텍스트
# -d, —debug: 디버그 모드
# -y, —yolo: 자동 승인 모드
```

# Gemini CLI Commands (Updated 2025)

## Core Commands

### `/permissions`
Display and manage permission settings for Gemini CLI. Shows current tool permissions and authentication status.

### `/status` 
Check the current status of Gemini CLI including:
- Connection status to Gemini model
- Authentication method in use
- Rate limit information (60 requests/minute, 1000/day for free tier)
- Active MCP servers

### `/memory`
Manage the AI's instructional context from GEMINI.md files:
- `/memory` - Display current memory context
- `/memory add <text>` - Add text to AI's memory

### `/mcp`
Model Context Protocol server management:
- `/mcp` - List configured MCP servers and connection status
- `/mcp show` - Show detailed descriptions for servers and tools
- `/mcp hide` - Hide tool descriptions, show only names

### `/auth`
Switch between authentication methods:
- Google account login (free tier)
- API key authentication
- Vertex AI authentication

### `/stats`
Display usage statistics:
- Request count for current session
- Daily/minute rate limit usage
- Model being used (gemini-2.5-pro/flash)

### `/help`
Display help information about Gemini CLI commands and features

## Shell Integration

### `!` prefix
Execute shell commands directly:
- `!ls -la` - List files
- `!git status` - Check git status
- Commands run with user's shell permissions

## File Operations

### `@` symbol
Reference files in prompts:
- `@file.txt` - Include file content in prompt
- Supports multiple files with `read_many_files` tool

## Authentication Notes

1. **Free Tier (Google Login)**
   - 60 requests per minute
   - 1,000 requests per day
   - May switch to gemini-2.5-flash during high load

2. **API Key**
   - Higher rate limits available
   - Configure in settings

3. **Vertex AI**
   - Enterprise authentication option
   - Custom quotas

## Security Configuration

- `excludeTools`: String matching for command restrictions (can be bypassed)
- `coreTools`: Explicitly allowed commands (recommended)
- `allowedMcpServerNames`: Restrict available MCP servers
- Tool usage requires user permission before execution

<vooster-docs>
- @vooster-docs/prd.md
- @vooster-docs/architecture.md
- @vooster-docs/guideline.md
- @vooster-docs/step-by-step.md
- @vooster-docs/clean-code.md
- @vooster-docs/git-commit-message.md
</vooster-docs>

