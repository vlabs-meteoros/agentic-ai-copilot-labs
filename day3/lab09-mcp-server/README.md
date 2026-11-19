# Lab 9: Build Your Own MCP Server in Python

| | |
|---|---|
| **Duration** | 50 minutes |
| **Topic** | MCP: fundamentals, STDIO and HTTP (SSE) transports, custom tools and resources in Python |
| **You need** | Copilot signed in (Lab 8). Day 3 setup done (it installs the `mcp` package). No Azure keys |
| **Files** | `helpdesk_server.py` (the server), `test_client.py` (a checker), `mcp.json` (Copilot's connection settings), `solution/` |

## Objectives

* Explain what an MCP server offers: **tools**, **resources** and **prompts**
* Run a Python MCP server and test it without any AI model
* Connect it to **GitHub Copilot Agent mode** and watch Copilot call your tools
* Add a new tool that changes something, and see the approval step (human in the loop)
* Run the same server over **STDIO** and over **HTTP**, and explain when to use each

## MCP in one picture

```
 You ──prompt──>  GitHub Copilot (Agent mode)  = the MCP CLIENT, it decides which tool to call
                        │   ▲
       MCP messages     │   │   JSON-RPC: list tools, call tool, read resource...
       over STDIO       ▼   │   or over HTTP
                  helpdesk_server.py  = the MCP SERVER (your Python code)
                        │
                        ▼
                  day2/data/helpdesk_kb.json  (Kaveri Systems knowledge base)
```

The **Model Context Protocol (MCP)** is a standard plug between AI apps and tools. You write a tool **once** as an MCP server,
and every MCP client can use it: Copilot in VS Code, Claude, ChatGPT, your own Python agents.

| An MCP server offers | What it is | In this lab |
|---|---|---|
| **Tools** | Functions the AI can **call** (they can act) | `search_kb`, `get_article`, and `create_ticket` (you add it) |
| **Resources** | Data the AI or the user can **read** (no side effects) | `kb://categories`, `kb://articles/{article_id}` |
| **Prompts** | Ready-made prompt templates the **user** picks | `troubleshoot` |

---

## Task 1: Read the server (5 min)

Open `day3\lab9-mcp-server\helpdesk_server.py`. It's about 100 lines. Find these parts:

1. `mcp = MCPServer(name="kaveri-helpdesk", instructions=...)`: creates the server. The `instructions` tell the AI how to use it.
2. `@mcp.tool()` above `search_kb` and `get_article`: this decorator turns a normal Python function into an MCP tool.
   * The **function name** becomes the tool name.
   * The **type hints** (`query: str`, `max_results: int = 3`) become the tool's input schema.
   * The **docstring** becomes the description that the AI reads to decide *when* to call the tool. Write it for the AI!
3. `@mcp.resource("kb://categories")` and `@mcp.resource("kb://articles/{article_id}")`: read-only data, addressed by a URI. `{article_id}` is a template parameter.
4. `@mcp.prompt()` above `troubleshoot`: a reusable prompt.
5. At the bottom, `mcp.run()` starts the server. With no arguments it uses **STDIO**.

> **Note:** this lab uses version 2 of the official MCP Python SDK. Many tutorials online still use version 1, where
> the class was called `FastMCP` (`from mcp.server.fastmcp import FastMCP`). The decorators work the same way.

**Checkpoint:** you can say which function the AI would call for *"show me article KB-014"* (answer: `get_article`).

## Task 2: Test the server without AI (5 min)

Before you give a tool to an AI, check it works on its own. `test_client.py` is a tiny MCP client: it starts your server, lists everything it offers, and calls a tool.

In the VS Code terminal, at the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python day3\lab-mcp-server\test_client.py
```

Read the output from top to bottom: **Tools**, **Resources**, **Prompts**, then a real `search_kb` call, two resource reads and one prompt.

Try your own search:

```powershell
python day3\lab09-mcp-server\test_client.py --query "travel hotel limit"
```

**Checkpoint:** the first search returns **KB-001** (VPN) with the highest score, and `kb://categories` shows IT: 13, HR: 8, Finance: 6, Facilities: 5, Security: 4.

> **What just happened?** `test_client.py` started `helpdesk_server.py` as a **child process** and talked to it through its
> standard input and output (**STDIO**). When the client finished, the server stopped. That's exactly what Copilot does next.

## Task 3: Connect the server to GitHub Copilot (10 min)

VS Code reads MCP servers from `.vscode\mcp.json` in your workspace.

1. Copy the prepared file into place:

   ```powershell
   New-Item -ItemType Directory -Force .vscode | Out-Null
   Copy-Item day3\lab09-mcp-server\mcp.json .vscode\mcp.json
   ```

2. Open `.vscode\mcp.json`. It tells VS Code **how to start** the server: run `.venv\Scripts\python.exe` with `helpdesk_server.py`.
   `${workspaceFolder}` is the repository folder you opened in VS Code.

3. Start the server: select **Start** in the small grey text above `"kaveri-helpdesk"`, or open the Command Palette
   (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>) and run **MCP: List Servers** > **kaveri-helpdesk** > **Start Server**.
   If VS Code asks whether you **trust** this server, read what it will run, then confirm.

4. Open the Chat view, select **New Chat**, and switch to **Agent** mode.
5. Select **Configure Tools** (the tools icon in the chat input). Find **kaveri-helpdesk** with its tools `search_kb` and `get_article`. Make sure they're ticked, then close the list.
6. Ask:

   ```text
   My VPN shows error 809 when I work from home. What should I do?
   ```

7. Copilot decides to call **search_kb** and then **get_article**. Expand each tool call in the chat to see the **input** Copilot sent and the **output** your server returned.
   If Copilot asks for permission to run a tool, select **Allow** (for this session).

**Checkpoint:** the answer tells you to switch the gateway to **India-South-443** and mentions **KB-001**. That fact exists only in the Kaveri knowledge base, so it came from your server.

> **Not working?** Command Palette > **MCP: List Servers** > **kaveri-helpdesk** > **Show Output** shows the server's log and any Python error.
> If the server isn't listed in **Configure Tools** at all, your organization may block MCP servers: tell your trainer.

**Try a few more** (watch which tool Copilot picks each time):

```text
How many days of sick leave do I get, and when do I need a medical certificate?
```

```text
What is the hotel limit for a business trip to Hyderabad?
```

## Task 4: Use resources and the prompt (5 min)

**Resources** are data you (or the AI) attach as context, like attaching a file.

1. In the chat input, select **Add Context** > **MCP Resources** (or run **MCP: Browse Resources** from the Command Palette), and pick **kb://categories**.
2. Ask:

   ```text
   Which knowledge base category has the most articles?
   ```

**Prompts** are templates that you start yourself.

3. In the chat input, type `/` and look for **kaveri-helpdesk.troubleshoot** (on some VS Code versions it's listed as **mcp.kaveri-helpdesk.troubleshoot**). Select it.
4. When it asks for **problem**, type `My account keeps getting locked` and press <kbd>Enter</kbd>. The template from your server is filled in and sent.

**Checkpoint:** the category answer is **IT (13 articles)**. The troubleshoot answer has at most 5 numbered steps and ends with `Source: KB-003`.

## Task 5: Add a tool that does something (12 min)

So far the tools only **read**. Real agents also **act**: they create tickets, send messages, update records. Add a `create_ticket` tool.

1. In `helpdesk_server.py`, find the comment `# TODO (Lab 09, Task 5)`. Below it, paste this code:

   ```python
   @mcp.tool()
   def create_ticket(summary: str, category: str, priority: str = "P3") -> dict:
       """Create a helpdesk ticket when the knowledge base doesn't solve the employee's problem.

       Args:
           summary: One sentence describing the problem.
           category: IT, HR, Finance, Facilities or Security.
           priority: P1 (a whole team cannot work), P2 (one person cannot work) or P3 (everything else).
       """
       if priority not in ("P1", "P2", "P3"):
           return {"error": "priority must be P1, P2 or P3"}

       TICKETS_FILE.parent.mkdir(exist_ok=True)
       tickets = json.loads(TICKETS_FILE.read_text(encoding="utf-8")) if TICKETS_FILE.exists() else []
       ticket = {
           "ticket_id": f"INC-{1001 + len(tickets)}",
           "summary": summary,
           "category": category,
           "priority": priority,
           "created": datetime.now().isoformat(timespec="seconds"),
       }
       tickets.append(ticket)
       TICKETS_FILE.write_text(json.dumps(tickets, indent=2), encoding="utf-8")
       return ticket
   ```

   Notice: the docstring explains **when** to use the tool and what each priority means, so the AI can choose correctly.
   The `if priority not in ...` check protects you from bad input: never trust what an AI sends to your tool.

   *Alternative:* ask Copilot (Agent mode) to write the tool for you from a description, then compare its code with the one above.

2. Save the file. Check it still works: `python day3\lab09-mcp-server\test_client.py` now lists **create_ticket**.
3. Restart the server so Copilot sees the new tool: **MCP: List Servers** > **kaveri-helpdesk** > **Restart Server**.
4. **New Chat**, **Agent** mode. Ask:

   ```text
   The projector in the Chamundi boardroom has stopped working. Check the knowledge base first; if there's
   nothing about it, raise a ticket. Only one meeting is affected.
   ```

5. Copilot searches the knowledge base, finds nothing about projectors, and wants to call **create_ticket**. Before it runs, **look at the inputs it chose** (summary, category, priority). Then select **Allow**.

**Checkpoint:** `day3\lab09-mcp-server\outputs\tickets.json` exists and contains ticket **INC-1001** with category **Facilities**. Copilot's answer quotes the ticket id.

> **Human in the loop.** A tool that changes things should be approved by a person, at least until you trust it.
> VS Code asks before running tools; don't switch that off for tools that act. If you select **Allow** for the session or workspace,
> Copilot stops asking for that tool: fine for `search_kb`, risky for a tool that deletes or pays.

## Task 6: Run the same server over HTTP (8 min)

With STDIO, the client **starts** the server on the same machine, one copy per client. With an **HTTP** transport, the server runs **on its own**
(on a laptop, a VM, or in the cloud), and many clients connect to it by URL.

1. Open a **second terminal** (the **+** in the terminal panel) and start the server in HTTP mode. Leave it running:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   python day3\lab09-mcp-server\helpdesk_server.py --transport http
   ```

   It prints `Uvicorn running on http://127.0.0.1:8000`.

2. In your **first** terminal, test it by URL:

   ```powershell
   python day3\lab09-mcp-server\test_client.py --url http://127.0.0.1:8000/mcp
   ```

   Watch the second terminal: every MCP message shows up as an HTTP request (`POST /mcp ... 200 OK`).

3. Connect Copilot by URL. In `.vscode\mcp.json`, add a second server after the first one (mind the comma):

   ```json
       "kaveri-helpdesk-http": {
         "type": "http",
         "url": "http://127.0.0.1:8000/mcp"
       }
   ```

   The finished file is in `solution\mcp.json`.

4. Stop the STDIO copy so Copilot doesn't see every tool twice: **MCP: List Servers** > **kaveri-helpdesk** > **Stop Server**.
   Then start **kaveri-helpdesk-http** the same way.
5. **New Chat**, **Agent** mode, and ask a question, for example *"Can I carry over unused annual leave?"*

**Checkpoint:** Copilot answers from **KB-013** (up to 10 days carry over), and the second terminal shows new `POST /mcp` lines for the tool calls.

6. When you're done, press <kbd>Ctrl</kbd>+<kbd>C</kbd> in the second terminal to stop the HTTP server.

**What about SSE?** **SSE** (Server-Sent Events) is the *older* HTTP transport for MCP. The newer **Streamable HTTP** you just used replaced it,
but you'll still meet SSE servers. Your server supports both:

```powershell
python day3\lab00-mcp-server\helpdesk_server.py --transport sse          # serves http://127.0.0.1:8000/sse
python day3\lab09-mcp-server\test_client.py --url http://127.0.0.1:8000/sse
```

In `mcp.json` an SSE server uses `"type": "sse"` and the `/sse` URL.

---

## STDIO or HTTP?

| | **STDIO** | **HTTP** (Streamable HTTP; SSE is the older form) |
|---|---|---|
| Who starts the server | The client, as a child process | You (or a cloud service). It runs on its own |
| Where it runs | Same machine as the client | Anywhere with a URL |
| How many clients | One per server process | Many at the same time |
| Security | Runs with **your** user rights on your machine: only install servers you trust | Needs authentication (OAuth/tokens) when it's not on `localhost` |
| Typical use | Local tools: files, Git, your own scripts, this lab | Shared company services: ticketing, CRM, databases |

## Clean up (optional)

* **MCP: List Servers** > stop the servers you started.
* Delete `.vscode\mcp.json` if you don't want Copilot to offer these servers in later labs.
* `day3\lab09-mcp-server\outputs\` holds your tickets; Git ignores it.

## Summary

* MCP is a standard way to give any AI client new **tools** (actions), **resources** (data) and **prompts** (templates).
* In Python, a decorator does the work: `@mcp.tool()`, `@mcp.resource(...)`, `@mcp.prompt()`. **Docstrings and type hints are the interface the AI reads.**
* Test a server without AI first (`test_client.py`), then connect it to Copilot with `.vscode\mcp.json`.
* **STDIO** for local servers the client starts; **HTTP** for shared servers that run on their own (SSE is the older HTTP transport).
* Tools that act need validation in your code **and** a human approval step.
