# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastmcp",
# ]
# ///

import os
import json
import shutil
import subprocess
from typing import Any
from fastmcp import FastMCP

# Resolve Vale executable path: env VALE_PATH wins; else search in PATH.
VALE_PATH = os.getenv("VALE_PATH") or shutil.which("vale") or "vale"

mcp = FastMCP("vale")

def _run_vale(args: list[str], *, stdin: str | None = None) -> tuple[int, str, str]:
    """Run Vale with provided args. Returns (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            [VALE_PATH, *args],
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as e:
        return 127, "", f"Vale executable not found: {VALE_PATH}"


@mcp.tool
def server_info() -> dict[str, Any]:
    """Get Vale CLI info (version and path)."""
    code, out, err = _run_vale(["--version"]) 
    return {
        "vale_path": VALE_PATH,
        "returncode": code,
        "version": out.strip() if out else None,
        "stderr": err.strip() if err else None,
    }

@mcp.tool
def list_styles(config_path: str | None = None) -> dict[str, Any]:
    """List available Vale styles (per config)."""
    args: list[str] = ["ls"]
    if config_path:
        args += ["--config", config_path]
    code, out, err = _run_vale(args)
    styles: list[str] = []
    if out:
        # Try to parse as JSON first (future-proof). Fallback to lines.
        try:
            data = json.loads(out)
            if isinstance(data, dict) and "styles" in data:
                styles = list(map(str, data.get("styles", [])))
            elif isinstance(data, list):
                styles = list(map(str, data))
        except json.JSONDecodeError:
            styles = [line.strip() for line in out.splitlines() if line.strip()]
    return {"returncode": code, "styles": styles, "stderr": err.strip() if err else None}

@mcp.tool
def lint_text(
    text: str,
    styles: list[str] | None = None,
    min_alert_level: str = "suggestion",
    ext: str = ".txt",
    config_path: str | None = None,
):
    """Lint a string of text with Vale via CLI. Returns normal CLI output text.

    Args:
      text: The text to lint.
      styles: Optional list of styles to enable (if supported by your Vale version).
      min_alert_level: suggestion | warning | error.
      ext: File extension hint for stdin, affects which rules apply.
      config_path: Optional path to a .vale.ini/.vale.yaml to use.
    """
    args: list[str] = ["--no-exit", f"--minAlertLevel={min_alert_level}", "--ext", ext, "-"]
    if config_path:
        args = ["--config", config_path, *args]
    if styles:
        # Some Vale versions support --styles, others require config; best-effort.
        args = [f"--styles={','.join(styles)}", *args]
    code, out, err = _run_vale(args, stdin=text)
    return {
        "returncode": code,
        "output": out,
        "stderr": err.strip() if err else None,
    }

@mcp.tool
def lint_file(
    path: str,
    styles: list[str] | None = None,
    min_alert_level: str = "suggestion",
    config_path: str | None = None,
):
    """Lint a file with Vale via CLI. Returns normal CLI output text."""
    args: list[str] = ["--no-exit", f"--minAlertLevel={min_alert_level}", path]
    if config_path:
        args = ["--config", config_path, *args]
    if styles:
        args = [f"--styles={','.join(styles)}", *args]
    code, out, err = _run_vale(args)
    return {
        "returncode": code,
        "output": out,
        "stderr": err.strip() if err else None,
    }

@mcp.tool
def list_alert_levels():
    """List possible alert levels (suggestion, warning, error)."""
    return ["suggestion", "warning", "error"]

if __name__ == "__main__":
    mcp.run()
