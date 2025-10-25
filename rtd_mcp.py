# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "fastmcp",
# ]
# ///

import os
import httpx
from fastmcp import FastMCP

RTD_BASE = os.getenv("RTD_BASE", "https://readthedocs.org")
RTD_TOKEN = os.getenv("RTD_TOKEN")
HEADERS = {"Authorization": f"Token {RTD_TOKEN}"} if RTD_TOKEN else {}
client = httpx.Client(base_url=RTD_BASE, headers=HEADERS, timeout=20)

mcp = FastMCP("readthedocs")

@mcp.tool
def list_projects(limit: int = 10):
    """List RTD projects for the current user."""
    return client.get("/api/v3/projects/", params={"limit": limit}).json()

@mcp.tool
def project_info(project: str):
    """Get details for a project (slug)."""
    return client.get(f"/api/v3/projects/{project}/").json()

@mcp.tool
def list_builds(project: str, limit: int = 10, running: bool | None = None):
    """List recent builds for a project."""
    params: dict[str, int | str] = {"limit": limit}
    if running is not None:
        params["running"] = str(running).lower()
    return client.get(f"/api/v3/projects/{project}/builds/", params=params).json()

@mcp.tool
def trigger_build(project: str, version: str = "latest"):
    """Trigger a build for project/version."""
    r = client.post(f"/api/v3/projects/{project}/versions/{version}/builds/")
    r.raise_for_status()
    return r.json()

@mcp.tool
def get_embed_content(url: str):
    """Fetch content from the RTD embed API."""
    r = client.get("/api/v3/embed/", params={"url": url})
    r.raise_for_status()
    return r.json()

# Versions
@mcp.tool
def list_versions(project: str, limit: int = 10, active: bool | None = None):
    """List versions for a project. Optionally filter by active status."""
    params: dict[str, int | str] = {"limit": limit}
    if active is not None:
        params["active"] = str(active).lower()
    return client.get(f"/api/v3/projects/{project}/versions/", params=params).json()

@mcp.tool
def get_version(project: str, version: str):
    """Get details of a specific version."""
    return client.get(f"/api/v3/projects/{project}/versions/{version}/").json()

@mcp.tool
def update_version(project: str, version: str, active: bool | None = None, hidden: bool | None = None):
    """Update a version (activate/deactivate, show/hide)."""
    data = {}
    if active is not None:
        data["active"] = active
    if hidden is not None:
        data["hidden"] = hidden
    r = client.patch(f"/api/v3/projects/{project}/versions/{version}/", json=data)
    r.raise_for_status()
    return {"status": "updated", "version": version}

# Build management
@mcp.tool
def get_build(project: str, build_id: int):
    """Get details of a specific build."""
    return client.get(f"/api/v3/projects/{project}/builds/{build_id}/").json()

# Project management
@mcp.tool
def update_project(project: str, name: str | None = None, repository_url: str | None = None, 
                   language: str | None = None, programming_language: str | None = None,
                   homepage: str | None = None, tags: list[str] | None = None):
    """Update project settings."""
    data = {}
    if name is not None:
        data["name"] = name
    if repository_url is not None:
        data["repository"] = {"url": repository_url}
    if language is not None:
        data["language"] = language
    if programming_language is not None:
        data["programming_language"] = programming_language
    if homepage is not None:
        data["homepage"] = homepage
    if tags is not None:
        data["tags"] = tags
    r = client.patch(f"/api/v3/projects/{project}/", json=data)
    r.raise_for_status()
    return {"status": "updated", "project": project}

@mcp.tool
def sync_versions(project: str):
    """Trigger a sync of versions from the repository."""
    r = client.post(f"/api/v3/projects/{project}/sync-versions/")
    r.raise_for_status()
    return {"status": "sync triggered", "project": project}

# Subprojects
@mcp.tool
def list_subprojects(project: str, limit: int = 10):
    """List all subprojects for a project."""
    return client.get(f"/api/v3/projects/{project}/subprojects/", params={"limit": limit}).json()

@mcp.tool
def get_subproject(project: str, alias: str):
    """Get details of a specific subproject relationship."""
    return client.get(f"/api/v3/projects/{project}/subprojects/{alias}/").json()

@mcp.tool
def create_subproject(project: str, child: str, alias: str | None = None):
    """Create a subproject relationship."""
    data = {"child": child}
    if alias:
        data["alias"] = alias
    r = client.post(f"/api/v3/projects/{project}/subprojects/", json=data)
    r.raise_for_status()
    return r.json()

@mcp.tool
def delete_subproject(project: str, alias: str):
    """Delete a subproject relationship."""
    r = client.delete(f"/api/v3/projects/{project}/subprojects/{alias}/")
    r.raise_for_status()
    return {"status": "deleted", "alias": alias}

# Translations
@mcp.tool
def list_translations(project: str, limit: int = 10):
    """List all translations for a project."""
    return client.get(f"/api/v3/projects/{project}/translations/", params={"limit": limit}).json()

# Redirects
@mcp.tool
def list_redirects(project: str, limit: int = 10):
    """List all redirects for a project."""
    return client.get(f"/api/v3/projects/{project}/redirects/", params={"limit": limit}).json()

@mcp.tool
def get_redirect(project: str, redirect_id: int):
    """Get details of a specific redirect."""
    return client.get(f"/api/v3/projects/{project}/redirects/{redirect_id}/").json()

@mcp.tool
def create_redirect(project: str, redirect_type: str, from_url: str | None = None, 
                    to_url: str | None = None, http_status: int = 302):
    """Create a redirect. Types: 'page', 'exact', 'clean_url_to_html', 'html_to_clean_url'."""
    data = {"type": redirect_type, "http_status": http_status}
    if from_url:
        data["from_url"] = from_url
    if to_url:
        data["to_url"] = to_url
    r = client.post(f"/api/v3/projects/{project}/redirects/", json=data)
    r.raise_for_status()
    return r.json()

@mcp.tool
def update_redirect(project: str, redirect_id: int, redirect_type: str | None = None,
                    from_url: str | None = None, to_url: str | None = None):
    """Update an existing redirect."""
    data = {}
    if redirect_type:
        data["type"] = redirect_type
    if from_url:
        data["from_url"] = from_url
    if to_url:
        data["to_url"] = to_url
    r = client.put(f"/api/v3/projects/{project}/redirects/{redirect_id}/", json=data)
    r.raise_for_status()
    return r.json()

@mcp.tool
def delete_redirect(project: str, redirect_id: int):
    """Delete a redirect."""
    r = client.delete(f"/api/v3/projects/{project}/redirects/{redirect_id}/")
    r.raise_for_status()
    return {"status": "deleted", "redirect_id": redirect_id}

# Environment Variables
@mcp.tool
def list_environment_variables(project: str, limit: int = 10):
    """List all environment variables for a project."""
    return client.get(f"/api/v3/projects/{project}/environmentvariables/", params={"limit": limit}).json()

@mcp.tool
def get_environment_variable(project: str, variable_id: int):
    """Get details of a specific environment variable."""
    return client.get(f"/api/v3/projects/{project}/environmentvariables/{variable_id}/").json()

@mcp.tool
def create_environment_variable(project: str, name: str, value: str, public: bool = False):
    """Create an environment variable. Set public=True to expose in PR builds."""
    data = {"name": name, "value": value, "public": public}
    r = client.post(f"/api/v3/projects/{project}/environmentvariables/", json=data)
    r.raise_for_status()
    return r.json()

@mcp.tool
def delete_environment_variable(project: str, variable_id: int):
    """Delete an environment variable."""
    r = client.delete(f"/api/v3/projects/{project}/environmentvariables/{variable_id}/")
    r.raise_for_status()
    return {"status": "deleted", "variable_id": variable_id}

# Remote repositories (for discovering importable repos)
@mcp.tool
def list_remote_repositories(name: str | None = None, vcs_provider: str | None = None, limit: int = 10):
    """List importable repositories from connected VCS. Provider: 'github', 'gitlab', or 'bitbucket'."""
    params: dict[str, int | str] = {"limit": limit}
    if name:
        params["name"] = name
    if vcs_provider:
        params["vcs_provider"] = vcs_provider
    return client.get("/api/v3/remote/repositories/", params=params).json()

@mcp.tool
def list_remote_organizations(name: str | None = None, vcs_provider: str | None = None, limit: int = 10):
    """List connected VCS organizations. Provider: 'github', 'gitlab', or 'bitbucket'."""
    params: dict[str, int | str] = {"limit": limit}
    if name:
        params["name"] = name
    if vcs_provider:
        params["vcs_provider"] = vcs_provider
    return client.get("/api/v3/remote/organizations/", params=params).json()

# Resource: fetch a built doc page (wildcard path segment)
@mcp.resource("rtd://{project}/{version}/{path*}", mime_type="text/html")
def fetch_doc(project: str, version: str, path: str):
    """Fetch a built doc page as HTML."""
    url = f"https://{project}.readthedocs.io/en/{version}/{path}"
    r = httpx.get(url, follow_redirects=True, timeout=20)
    r.raise_for_status()
    return r.text  # FastMCP converts str to TextResourceContents

if __name__ == "__main__":
    mcp.run()
