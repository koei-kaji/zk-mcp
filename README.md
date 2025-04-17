# zk-mcp

zk-mcp is an MCP server for integrating notes managed by zk with LLMs.
It aims to enable LLMs to efficiently access knowledge bases managed under zk.

# Prerequisites

- [zk : a plain text note-taking assistant](https://zk-org.github.io/zk/index.html)
- [uv](https://docs.astral.sh/uv/)
- Any MCP client

# How to use

1. Clone this repository
2. Add the following settings into `servers.json` :

```json
{
  "mcpServers": {
    "zk": {
      "alwaysAllow": [
        "get_note",
        "get_note_paths",
        "get_linking_notes",
        "get_tags"
      ],
      "args": [
        "--directory",
        "/path/to/github.com/koei-kaji/zk-mcp/",
        "run",
        "server.py"
      ],
      "command": "uv",
      "env": {
        "ZK_DIR": "/path/to/zk-note-directory/"
      }
    }
  }
}
```
