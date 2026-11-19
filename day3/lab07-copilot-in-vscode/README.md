# Lab 7: Enable and Explore GitHub Copilot in VS Code

| | |
|---|---|
| **Duration** | 35 minutes |
| **Topic** | Prompting Fundamentals: how GitHub Copilot responds to your instructions |
| **You need** | Your company GitHub account with a **GitHub Copilot Business** seat (your trainer confirms this) |
| **Files** | You create them in `day3\lab07-copilot-in-vscode\outputs\` (Git ignores this folder) |

> Adapted from the Microsoft Learn exercises *Enable GitHub Copilot in Visual Studio Code* and *Examine GitHub Copilot settings and user interface features*
> ([MicrosoftLearning/mslearn-github-copilot-dev](https://github.com/MicrosoftLearning/mslearn-github-copilot-dev), MIT licence), shortened for the lab VM and Python.

## Objectives

* Sign in to GitHub Copilot in VS Code and check that your Business seat is active
* Find the Copilot settings that matter (turn suggestions on and off, per language)
* Use the four ways to talk to Copilot: **Chat view**, **Quick Chat**, **Inline Chat** and **Smart Actions**
* See the difference between **Ask** mode (Copilot answers) and **Agent** mode (Copilot edits your files)
* Accept code completions (ghost text) and **next edit suggestions**

> **Copilot changes every month.** Buttons move and get renamed between VS Code versions. If a step doesn't match your screen exactly,
> look for the closest option, or hover over the icons for their names. The ideas stay the same.

---

## Task 1: Sign in to GitHub Copilot (5 min)

1. In VS Code, open **Help > About** and note the version. If it's older than about six months, run **Help > Check for Updates** (or ask your trainer).
2. At the bottom right of the window (the **Status Bar**), find the **Copilot icon** (a small face with goggles). Hover over it and select **Set up Copilot** or **Sign in**.

   * No Copilot icon at all? Open the Extensions view (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>), search for **GitHub Copilot Chat** and install it.

3. A browser window opens. Sign in with the **GitHub account that has your Copilot Business seat**, then select **Authorize Visual Studio Code**. Allow the browser to open VS Code again.

   * If VS Code shows a page that offers *Copilot Free*, still choose **Sign in**: once you sign in with your company account, Copilot picks up the Business seat.

4. Back in VS Code, select the Copilot icon in the Status Bar again. The menu now shows your account and Copilot status.

**Checkpoint:** the Copilot status menu opens without asking you to sign in. In the browser, `https://github.com/settings/copilot` says Copilot Business is active and **managed by your organization**.

> **Business vs Free:** with Copilot Business, your organization's admins decide the policies (for example, which models you can pick, whether suggestions matching public code are blocked, and whether MCP servers are allowed). That's why some options on the GitHub settings page are greyed out for you.

> The remaining tasks will be added after everyone completes Task 1.