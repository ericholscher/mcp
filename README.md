# MCP Servers: Read the Docs + Vale

This repo provides two MCP servers for local use:

- `rtd_mcp.py`: Read the Docs API tools and resources
- `vale_mcp.py`: Vale linter tools using the local Vale CLI

## Requirements

- Python 3.11+
- `uv` (recommended) or a Python environment with `fastmcp` installed
- Vale CLI installed and on your PATH (or set `VALE_PATH`)

## Quick start

Run with uv:

```bash
# Read the Docs
uv run rtd_mcp.py

# Vale
uv run vale_mcp.py
```

Alternatively with Python directly:

```bash
python3 rtd_mcp.py
python3 vale_mcp.py
```

## Configure Claude Desktop

Copy the sample MCP configuration into your Claude Desktop config at:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Merge this snippet (adjust paths as needed):

```json
{
  "mcpServers": {
    "readthedocs": {
      "command": "uv",
      "args": ["run", "/Users/eric/projects/rtd-mcp/rtd_mcp.py"],
      "env": {
        "RTD_TOKEN": "<your_rtd_token_here>"
      }
    },
    "vale": {
      "command": "uv",
      "args": ["run", "/Users/eric/projects/rtd-mcp/vale_mcp.py"],
      "env": {
        "VALE_PATH": "/usr/local/bin/vale"
      }
    }
  }
}
```

Restart Claude Desktop to pick up changes.

## Vale MCP Tools

- `server_info()` — Returns Vale CLI version/path
- `list_styles(config_path?)` — Lists available styles (respects `--config` if provided)
- `lint_text(text, styles?, min_alert_level?, ext?, config_path?)` — Lints text from stdin, returns normal CLI output in `output`
- `lint_file(path, styles?, min_alert_level?, config_path?)` — Lints a file, returns normal CLI output in `output`
- `list_alert_levels()` — Returns `["suggestion","warning","error"]`

Notes:
- For some Vale versions, `--styles` may not be supported; prefer setting styles via your `.vale.ini`/`.vale.yaml` and pass `config_path` when needed.
- We pass `--no-exit` so results are returned even when issues are found.

## Troubleshooting

- If `fastmcp` import fails, install it: `uv add fastmcp` or `pip install fastmcp`.
- If Vale isn’t found, install it from https://vale.sh or set `VALE_PATH` to the binary.
- To increase rule coverage for stdin, set an appropriate `ext` like `.md` or `.rst`.
