# zk-mcp

zk-mcp is an MCP (Model Context Protocol) server for integrating notes managed by [zk](https://zk-org.github.io/zk/index.html) with LLMs.
It enables LLMs to efficiently access and interact with knowledge bases managed under zk.

## Features

- **Note Query**: Search notes by content, tags, and complex filters
- **Link Analysis**: Discover relationships between notes (links to, linked by, related)
- **Tag Management**: List and filter by available tags
- **Note Access**: Read complete note contents
- **Note Creation**: Create new notes programmatically

## Prerequisites

- [zk : a plain text note-taking assistant](https://zk-org.github.io/zk/index.html)
- [uv](https://docs.astral.sh/uv/)
- Any MCP client (e.g., Claude Desktop, Continue, etc.)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/koei-kaji/zk-mcp.git
cd zk-mcp
```

2. Install dependencies:
```bash
uv sync
```

## Configuration

Add the following settings to your MCP client's `servers.json`:

```json
{
  "mcpServers": {
    "zk": {
      "alwaysAllow": [
        "get_note",
        "get_note_paths",
        "get_linking_notes",
        "get_tags",
        "create_note"
      ],
      "args": [
        "--directory",
        "/path/to/zk-mcp/",
        "run",
        "server.py"
      ],
      "command": "uv",
      "env": {
        "ZK_DIR": "/path/to/your/zk-note-directory/"
      }
    }
  }
}
```

**Important**: Replace `/path/to/zk-mcp/` with the actual path to this repository and `/path/to/your/zk-note-directory/` with the path to your zk notes directory.

## Available MCP Tools

This server provides the following MCP tools:

### `get_note_paths`

Search for notes based on various criteria:
- **include_str**: Filter notes containing specific strings in content or filename
- **include_str_operand**: Logical operator (`AND`/`OR`) for multiple string filters
- **exclude_str**: Exclude notes containing specific strings
- **include_tags**: Filter notes by tags
- **include_tags_operand**: Logical operator (`AND`/`OR`) for multiple tag filters
- **exclude_tags**: Exclude notes with specific tags

### `get_linking_notes`

Discover note relationships:
- **link_to_notes**: Notes that the specified note links to
- **linked_by_notes**: Notes that link to the specified note
- **related_notes**: Notes that are related to the specified note

### `get_tags`

List all available tags in the note repository.

### `get_note`

Read the complete content of a specific note by path.

### `create_note`

Create a new note with the specified title in an optional directory.

## Development

### Commands

- `make run` - Run the MCP server in development mode with `ZK_DIR=.`
- `make format` - Format code using ruff (imports + formatting)
- `make lint` - Run linting with ruff and type checking with mypy
- `make test` - Run all tests with pytest
- `make pre-commit` - Run both format and lint (recommended before commits)

### Package Management

- `uv add <package>` - Add runtime dependency
- `uv add --dev <package>` - Add development dependency
- `uv run <command>` - Run command in virtual environment

## Architecture

The server is built using:
- **FastMCP**: MCP server implementation
- **Pydantic**: Data validation and serialization
- **zk CLI**: Backend integration with zk note system

All tools return JSON responses using Pydantic models for type safety and validation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
