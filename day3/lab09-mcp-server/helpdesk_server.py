"""
Kaveri Systems Helpdesk: a small MCP server written in Python.

It exposes the Day 2 helpdesk knowledge base (day2/data/helpdesk_kb.json) to any MCP client,
for example GitHub Copilot in VS Code (Agent mode).

    Tools      (actions the AI can call)   search_kb, get_article   (+ create_ticket, which you add in Task 5)
    Resources  (data the AI can read)      kb://categories, kb://articles/{article_id}
    Prompts    (reusable prompt templates) troubleshoot

Run it:
    python helpdesk_server.py                          # STDIO: the client starts this script itself (default)
    python helpdesk_server.py --transport http         # Streamable HTTP on http://127.0.0.1:8000/mcp
    python helpdesk_server.py --transport sse          # SSE (older HTTP transport) on http://127.0.0.1:8000/sse

Built with the official MCP Python SDK, version 2 (`pip install "mcp[cli]"`).
Many tutorials online still show version 1, where the class was called FastMCP; here it is MCPServer.
"""
import argparse
import json
from datetime import datetime          # used by create_ticket (Task 5)
from pathlib import Path

from mcp.server.mcpserver import MCPServer

# ---------------------------------------------------------------- data
REPO_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "day2" / "data").is_dir())
KB_FILE = REPO_ROOT / "day2" / "data" / "helpdesk_kb.json"
TICKETS_FILE = REPO_ROOT / "day3" / "lab09-mcp-server" / "outputs" / "tickets.json"

ARTICLES = json.loads(KB_FILE.read_text(encoding="utf-8"))

# ---------------------------------------------------------------- server
mcp = MCPServer(
    name="kaveri-helpdesk",
    instructions="Answers questions about Kaveri Systems IT, HR, Finance, Facilities and Security policies. "
                 "Search the knowledge base before answering and quote the article id (for example KB-003).",
)

# IMPORTANT for STDIO servers: never print() to stdout. stdout carries the MCP messages,
# so a stray print breaks the connection. (print(..., file=sys.stderr) is safe.)


# ---------------------------------------------------------------- tools
@mcp.tool()
def search_kb(query: str, category: str = "", max_results: int = 3) -> list[dict]:
    """Search the Kaveri Systems helpdesk knowledge base.

    Args:
        query: Keywords describing the problem, for example "vpn error 809" or "sick leave".
        category: Optional filter: IT, HR, Finance, Facilities or Security. Leave empty for all.
        max_results: How many articles to return (1-10).
    """
    words = [w for w in query.lower().split() if len(w) > 2]
    scored = []
    for article in ARTICLES:
        if category and article["category"].lower() != category.lower():
            continue
        title = article["title"].lower()
        text = article["text"].lower()
        # Simple keyword score: a match in the title counts 3 times, in the text once.
        score = sum(3 * (w in title) + (w in text) for w in words)
        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    max_results = max(1, min(max_results, 10))
    return [
        {"id": a["id"], "category": a["category"], "title": a["title"], "score": s}
        for s, a in scored[:max_results]
    ]


@mcp.tool()
def get_article(article_id: str) -> dict:
    """Get the full text of one knowledge base article by its id, for example KB-001."""
    for article in ARTICLES:
        if article["id"].lower() == article_id.strip().lower():
            return article
    return {"error": f"No article with id {article_id}. Use search_kb to find valid ids."}


# ------------------------------------------------- TODO (Lab 09, Task 5)
# Add a create_ticket tool here.


# ---------------------------------------------------------------- resources
@mcp.resource("kb://categories", mime_type="application/json")
def list_categories() -> str:
    """The knowledge base categories and how many articles each one has."""
    counts: dict[str, int] = {}
    for article in ARTICLES:
        counts[article["category"]] = counts.get(article["category"], 0) + 1
    return json.dumps(counts, indent=2)


@mcp.resource("kb://articles/{article_id}", mime_type="text/markdown")
def article_as_markdown(article_id: str) -> str:
    """One knowledge base article as Markdown."""
    article = get_article(article_id)
    if "error" in article:
        return article["error"]
    return f"# {article['id']}: {article['title']}\n\n*Category: {article['category']}*\n\n{article['text']}\n"


# ---------------------------------------------------------------- prompts
@mcp.prompt()
def troubleshoot(problem: str) -> str:
    """Helpdesk troubleshooting: answer an employee's problem from the knowledge base."""
    return (
        "You are the Kaveri Systems IT helpdesk assistant.\n"
        f"Employee's problem: {problem}\n\n"
        "1. Use the search_kb tool to find the relevant articles, then get_article to read them.\n"
        "2. Answer in at most 5 short numbered steps, using only facts from the articles.\n"
        "3. End with 'Source: <article id>'.\n"
        "4. If the articles don't cover the problem, say so and give the helpdesk contact from KB-036."
    )


# ---------------------------------------------------------------- start
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kaveri Systems Helpdesk MCP server")
    parser.add_argument("--transport", choices=["stdio", "http", "sse"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()                                             # talk over stdin/stdout
    elif args.transport == "http":
        mcp.run(transport="streamable-http", port=args.port)  # http://127.0.0.1:8000/mcp
    else:
        mcp.run(transport="sse", port=args.port)              # http://127.0.0.1:8000/sse
