"""Interactive Git review component for MCP Apps-compatible hosts."""

from __future__ import annotations

GIT_REVIEW_RESOURCE_URI = "ui://tatuy/git-review/v1.html"
GIT_REVIEW_MIME_TYPE = "text/html;profile=mcp-app"

GIT_REVIEW_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Tatuy Git Review</title>
  <style>
    :root {
      color-scheme: light dark;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      padding: 10px;
      background: transparent;
      color: CanvasText;
    }

    button {
      font: inherit;
      color: inherit;
    }

    .panel {
      border: 1px solid color-mix(in srgb, CanvasText 16%, transparent);
      border-radius: 12px;
      overflow: hidden;
      background: color-mix(in srgb, Canvas 96%, transparent);
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 12px;
      border-bottom: 1px solid color-mix(in srgb, CanvasText 12%, transparent);
    }

    .title {
      min-width: 0;
    }

    .title strong {
      display: block;
      font-size: 13px;
      line-height: 1.3;
    }

    .summary {
      margin-top: 2px;
      font-size: 12px;
      opacity: 0.65;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .refresh {
      flex: 0 0 auto;
      border: 1px solid color-mix(in srgb, CanvasText 18%, transparent);
      border-radius: 8px;
      background: transparent;
      padding: 5px 9px;
      cursor: pointer;
      font-size: 12px;
    }

    .refresh:hover:not(:disabled) {
      background: color-mix(in srgb, CanvasText 7%, transparent);
    }

    .refresh:disabled {
      cursor: wait;
      opacity: 0.5;
    }

    .files {
      display: grid;
      max-height: 240px;
      overflow: auto;
    }

    .file {
      display: grid;
      grid-template-columns: auto minmax(0, 1fr) auto;
      align-items: center;
      gap: 8px;
      width: 100%;
      border: 0;
      border-bottom: 1px solid color-mix(in srgb, CanvasText 8%, transparent);
      background: transparent;
      padding: 8px 12px;
      text-align: left;
      cursor: pointer;
    }

    .file:last-child { border-bottom: 0; }

    .file:hover,
    .file[aria-current="true"] {
      background: color-mix(in srgb, CanvasText 7%, transparent);
    }

    .status {
      width: 22px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 11px;
      font-weight: 700;
      opacity: 0.7;
    }

    .path {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
    }

    .counts {
      display: flex;
      gap: 6px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 11px;
      white-space: nowrap;
    }

    .add { color: #1f9d55; }
    .del { color: #d64545; }

    .empty,
    .error {
      padding: 14px 12px;
      font-size: 12px;
      opacity: 0.7;
    }

    .error { color: #d64545; opacity: 1; }

    .diff-wrap {
      border-top: 1px solid color-mix(in srgb, CanvasText 12%, transparent);
    }

    .diff-title {
      padding: 8px 12px;
      font-size: 11px;
      font-weight: 700;
      opacity: 0.7;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    pre {
      margin: 0;
      max-height: 360px;
      overflow: auto;
      border-top: 1px solid color-mix(in srgb, CanvasText 8%, transparent);
      padding: 10px 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 11px;
      line-height: 1.45;
      white-space: pre;
      tab-size: 4;
    }

    [hidden] { display: none !important; }
  </style>
</head>
<body>
  <section class="panel" aria-label="Git changes">
    <header class="header">
      <div class="title">
        <strong>Working tree</strong>
        <div id="summary" class="summary">Loading changes...</div>
      </div>
      <button id="refresh" class="refresh" type="button">Refresh</button>
    </header>

    <div id="files" class="files" aria-live="polite"></div>
    <div id="error" class="error" hidden></div>

    <div id="diff-wrap" class="diff-wrap" hidden>
      <div id="diff-title" class="diff-title"></div>
      <pre id="diff"></pre>
    </div>
  </section>

  <script>
    (() => {
      const summaryEl = document.getElementById("summary");
      const filesEl = document.getElementById("files");
      const refreshEl = document.getElementById("refresh");
      const errorEl = document.getElementById("error");
      const diffWrapEl = document.getElementById("diff-wrap");
      const diffTitleEl = document.getElementById("diff-title");
      const diffEl = document.getElementById("diff");

      let project = "engine";
      let snapshot = null;
      let selectedPath = null;
      let rpcId = 0;
      const pendingRequests = new Map();

      const setError = (message) => {
        errorEl.textContent = message || "";
        errorEl.hidden = !message;
      };

      const updateSummary = () => {
        if (!snapshot) {
          summaryEl.textContent = "Loading changes...";
          return;
        }

        if (snapshot.clean) {
          summaryEl.textContent = `${snapshot.branch || "repository"} | clean`;
          return;
        }

        const totals = snapshot.totals || {};
        const fileCount = Number(totals.files ?? snapshot.files?.length ?? 0);
        const additions = Number(totals.additions ?? 0);
        const deletions = Number(totals.deletions ?? 0);
        summaryEl.textContent =
          `${snapshot.branch || "repository"} | ${fileCount} file${fileCount === 1 ? "" : "s"}` +
          ` | +${additions} -${deletions}`;
      };

      const renderFiles = () => {
        filesEl.replaceChildren();
        updateSummary();

        const files = Array.isArray(snapshot?.files) ? snapshot.files : [];
        if (!files.length) {
          const empty = document.createElement("div");
          empty.className = "empty";
          empty.textContent = snapshot?.clean
            ? "No working-tree changes."
            : "No changed files were returned.";
          filesEl.appendChild(empty);
          selectedPath = null;
          diffWrapEl.hidden = true;
          return;
        }

        for (const file of files) {
          const row = document.createElement("button");
          row.type = "button";
          row.className = "file";
          row.dataset.path = file.path;
          row.setAttribute("aria-current", String(file.path === selectedPath));

          const status = document.createElement("span");
          status.className = "status";
          status.textContent = file.status === "untracked" ? "??" : String(file.status || "");

          const path = document.createElement("span");
          path.className = "path";
          path.textContent = file.path;
          path.title = file.path;

          const counts = document.createElement("span");
          counts.className = "counts";

          const additions = document.createElement("span");
          additions.className = "add";
          additions.textContent = `+${Number(file.additions ?? 0)}`;

          const deletions = document.createElement("span");
          deletions.className = "del";
          deletions.textContent = `-${Number(file.deletions ?? 0)}`;

          counts.append(additions, deletions);
          row.append(status, path, counts);
          filesEl.appendChild(row);
        }
      };

      const showDiff = (path, text) => {
        selectedPath = path;
        diffTitleEl.textContent = path || "Diff";
        diffEl.textContent = text || "No diff available.";
        diffWrapEl.hidden = false;
        renderFiles();
      };

      const applyStructuredContent = (content) => {
        if (!content || typeof content !== "object") return;

        if (typeof content.project === "string" && content.project) {
          project = content.project;
        }

        if (Array.isArray(content.files)) {
          snapshot = content;
          renderFiles();
          setError("");
          return;
        }

        if (typeof content.diff === "string") {
          showDiff(content.path || selectedPath, content.diff);
          setError("");
        }
      };

      const notify = (method, params) => {
        window.parent.postMessage({ jsonrpc: "2.0", method, params }, "*");
      };

      const request = (method, params) =>
        new Promise((resolve, reject) => {
          const id = ++rpcId;
          pendingRequests.set(id, { resolve, reject });
          window.parent.postMessage(
            { jsonrpc: "2.0", id, method, params },
            "*"
          );
        });

      window.addEventListener(
        "message",
        (event) => {
          if (event.source !== window.parent) return;
          const message = event.data;
          if (!message || message.jsonrpc !== "2.0") return;

          if (typeof message.id === "number") {
            const pending = pendingRequests.get(message.id);
            if (!pending) return;
            pendingRequests.delete(message.id);
            if (message.error) pending.reject(message.error);
            else pending.resolve(message.result);
            return;
          }

          if (message.method === "ui/notifications/tool-input") {
            if (typeof message.params?.project === "string") {
              project = message.params.project;
            }
            return;
          }

          if (message.method === "ui/notifications/tool-result") {
            applyStructuredContent(message.params?.structuredContent);
          }
        },
        { passive: true }
      );

      const bridgeReady = (async () => {
        await request("ui/initialize", {
          appInfo: { name: "tatuy-git-review", version: "1.0.0" },
          appCapabilities: {},
          protocolVersion: "2026-01-26",
        });
        notify("ui/notifications/initialized", {});
      })();

      const callTool = async (name, args) => {
        await bridgeReady;
        const result = await request("tools/call", {
          name,
          arguments: args,
        });
        applyStructuredContent(result?.structuredContent);
        return result;
      };

      refreshEl.addEventListener("click", async () => {
        refreshEl.disabled = true;
        refreshEl.textContent = "Refreshing...";
        setError("");
        try {
          await callTool("git_snapshot", { project });
          if (selectedPath && snapshot?.files?.some((file) => file.path === selectedPath)) {
            await callTool("git_diff", {
              project,
              path: selectedPath,
              staged: false,
              context_lines: 3,
            });
          } else {
            selectedPath = null;
            diffWrapEl.hidden = true;
          }
        } catch (error) {
          setError(`Refresh failed: ${error?.message || "unknown error"}`);
        } finally {
          refreshEl.disabled = false;
          refreshEl.textContent = "Refresh";
        }
      });

      filesEl.addEventListener("click", async (event) => {
        const row = event.target.closest("button.file");
        if (!row) return;
        const path = row.dataset.path;
        if (!path) return;

        selectedPath = path;
        renderFiles();
        diffTitleEl.textContent = `${path} | loading...`;
        diffEl.textContent = "";
        diffWrapEl.hidden = false;
        setError("");

        try {
          await callTool("git_diff", {
            project,
            path,
            staged: false,
            context_lines: 3,
          });
        } catch (error) {
          setError(`Diff failed: ${error?.message || "unknown error"}`);
        }
      });
    })();
  </script>
</body>
</html>
"""
