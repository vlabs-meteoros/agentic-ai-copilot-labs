"""
A tiny MCP client that checks your server WITHOUT any AI model.

    python test_client.py                                   # starts helpdesk_server.py over STDIO
    python test_client.py --url http://127.0.0.1:8000/mcp   # connects to a server already running with --transport http
    python test_client.py --url http://127.0.0.1:8000/sse   # ... or with --transport sse

It does what Copilot does behind the scenes: connect, list what the server offers, then call a tool,
read a resource and fetch a prompt.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import Client
from mcp.client.sse import sse_client
from mcp.client.stdio import StdioServerParameters

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SERVER = Path(__file__).resolve().parent / "helpdesk_server.py"


def show(title):
    print(f"\n=== {title} " + "=" * (60 - len(title)))


async def main(url: str | None, query: str):
    # STDIO: launch the server as a child process with the same Python (.venv) that runs this script.
    # HTTP: a URL ending in /sse uses the older SSE transport, any other URL uses Streamable HTTP.
    if url and url.rstrip("/").endswith("/sse"):
        target = sse_client(url)
    else:
        target = url or StdioServerParameters(command=sys.executable, args=[str(SERVER)])

    async with Client(target) as client:
        info = client.server_info
        print(f"Connected to '{info.name if info else '?'}' using protocol {client.protocol_version}")

        show("Tools")
        for tool in (await client.list_tools()).tools:
            print(f"- {tool.name}: {(tool.description or '').splitlines()[0]}")
            print(f"    inputs: {list(tool.input_schema.get('properties', {}))}")

        show("Resources and resource templates")
        for res in (await client.list_resources()).resources:
            print(f"- {res.uri}  ({res.name})")
        for tpl in (await client.list_resource_templates()).resource_templates:
            print(f"- {tpl.uri_template}  ({tpl.name})")

        show("Prompts")
        for prompt in (await client.list_prompts()).prompts:
            print(f"- {prompt.name}: {prompt.description}")

        show(f"call_tool search_kb('{query}')")
        result = await client.call_tool("search_kb", {"query": query})
        if result.structured_content is not None:
            print(json.dumps(result.structured_content, indent=2))
        else:
            print(result.content[0].text)

        show("read_resource kb://categories")
        res = await client.read_resource("kb://categories")
        print(res.contents[0].text)

        show("read_resource kb://articles/KB-001")
        res = await client.read_resource("kb://articles/KB-001")
        print(res.contents[0].text)

        show("get_prompt troubleshoot")
        prompt = await client.get_prompt("troubleshoot", {"problem": "VPN shows error 809"})
        print(prompt.messages[0].content.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL of a running HTTP server, e.g. http://127.0.0.1:8000/mcp")
    parser.add_argument("--query", default="vpn error 809")
    args = parser.parse_args()
    asyncio.run(main(args.url, args.query))
