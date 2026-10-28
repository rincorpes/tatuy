"""Generate the static Tatuy showcase shell around docs and playables."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any

from tatuy.tooling.web.validation import WebOutputBasePathValidator


class ShowcaseSiteBuilder:
    """Compose the public Tatuy showcase around existing web build outputs.

    Args:
        repository_root: Tatuy repository root.
        output_root: Existing web output root containing docs and playables.
    """

    def __init__(
        self, repository_root: Path, *, output_root: Path | None = None
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.output_root = (
            output_root or self.repository_root / "build" / "web"
        ).resolve()

    def build(self, *, featured_slug: str = "render-queue") -> Path:
        """Generate the showcase shell from the validated catalog manifest.

        Args:
            featured_slug: Catalog slug promoted in the home-page hero.

        Returns:
            Path to the composed web output root.

        Raises:
            FileNotFoundError: Required docs, manifest, or playable output is missing.
            ValueError: The manifest has no valid targets or the featured slug is unknown.
        """
        docs_root = self.output_root / "docs"
        if not (docs_root / "index.html").is_file():
            raise FileNotFoundError(
                f"Documentation build not found: {docs_root}"
            )

        entries = self._load_catalog()
        featured = next(
            (entry for entry in entries if entry.get("slug") == featured_slug),
            None,
        )
        if featured is None:
            raise ValueError(
                f"Featured showcase target not found: {featured_slug}"
            )

        for entry in entries:
            if entry.get("playable") is True:
                self._validate_playable(entry)

        assets_root = self.output_root / "assets"
        assets_root.mkdir(parents=True, exist_ok=True)
        (assets_root / "site.css").write_text(
            self._site_css(), encoding="utf-8"
        )
        (assets_root / "site.js").write_text(self._site_js(), encoding="utf-8")
        (self.output_root / "index.html").write_text(
            self._home_html(entries, featured), encoding="utf-8"
        )

        showcase_root = self.output_root / "showcase"
        if showcase_root.exists():
            shutil.rmtree(showcase_root)
        for entry in entries:
            if entry.get("playable") is not True:
                continue
            slug = str(entry["slug"])
            target_root = showcase_root / slug
            target_root.mkdir(parents=True, exist_ok=True)
            (target_root / "index.html").write_text(
                self._play_html(entry), encoding="utf-8"
            )
        (self.output_root / ".nojekyll").touch()
        WebOutputBasePathValidator().validate(self.output_root)
        return self.output_root

    def _load_catalog(self) -> list[dict[str, Any]]:
        """Load the generated showcase manifest used as the site source of truth.

        Returns:
            Non-empty list of catalog entry mappings.

        Raises:
            FileNotFoundError: The catalog manifest has not been generated.
            ValueError: The manifest does not contain a non-empty target list.
        """
        manifest = self.output_root / "manifest.json"
        if not manifest.is_file():
            raise FileNotFoundError(f"Showcase manifest not found: {manifest}")
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        targets = payload.get("targets")
        if not isinstance(targets, list) or not targets:
            raise ValueError(
                "Showcase manifest must contain at least one target"
            )
        entries = [entry for entry in targets if isinstance(entry, dict)]
        if len(entries) != len(targets):
            raise ValueError("Showcase manifest targets must be mappings")
        return entries

    def _validate_playable(self, entry: dict[str, Any]) -> None:
        """Validate one catalog entrypoint before generating its wrapper page."""
        entrypoint = entry.get("entrypoint")
        if not isinstance(entrypoint, str) or not entrypoint:
            raise ValueError(
                "Playable showcase entry is missing its entrypoint"
            )
        resolved = (self.output_root / entrypoint).resolve()
        try:
            resolved.relative_to(self.output_root)
        except ValueError as exc:
            raise ValueError("Playable entrypoint escapes web output") from exc
        if not resolved.is_file():
            raise FileNotFoundError(f"Playable build not found: {resolved}")

    @classmethod
    def _home_html(
        cls,
        entries: list[dict[str, Any]],
        featured: dict[str, Any],
    ) -> str:
        featured_slug = html.escape(str(featured["slug"]), quote=True)
        featured_title = html.escape(str(featured["title"]))
        cards = "\n".join(cls._card_html(entry) for entry in entries)
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Tatuy is a Python-first 2D game engine with browser-playable examples.">
  <title>Tatuy - Python-first 2D game engine</title>
  <link rel="stylesheet" href="./assets/site.css">
</head>
<body>
<header class="site-header">
  <a class="brand" href="./">Tatuy</a>
  <nav><a href="./docs/">Docs</a><a href="#showcase">Showcase</a><a href="https://github.com/rincorpes/tatuy">GitHub</a></nav>
</header>
<main>
  <section class="hero">
    <p class="eyebrow">Python-first · 2D · explicit architecture</p>
    <h1>Build games in Python without hiding how the engine works.</h1>
    <p class="lede">Scenes, ECS, explicit system phases, reusable gameplay features, and replaceable runtime boundaries.</p>
    <div class="actions"><a class="button primary" href="./showcase/{featured_slug}/">Play {featured_title}</a><a class="button" href="./docs/">Read the docs</a></div>
  </section>
  <section class="architecture">
    <div><p class="eyebrow">Architecture</p><h2>Game code stays separate from the host.</h2></div>
    <pre>Game\n  ↓\nScenes + Game Systems\n  ↓\nECS + Engine Features\n  ↓\nSystem / Render Pipelines\n  ↓\nBackend + Runtime Host</pre>
  </section>
  <section id="showcase" class="showcase">
    <div class="section-heading"><div><p class="eyebrow">Browser showcase</p><h2>Catalog</h2></div><span class="status">Generated from target metadata</span></div>
    <div class="catalog-grid">{cards}</div>
  </section>
  <section class="project-status"><p class="eyebrow">Project status</p><h2>Experimental by design.</h2><p>Tatuy is alpha software. The Python foundation, browser host, examples, documentation, and future native runtime are evolving together.</p></section>
</main>
<footer><span>Tatuy · MIT licensed</span><a href="https://github.com/rincorpes/tatuy">GitHub</a></footer>
</body>
</html>
"""

    @classmethod
    def _card_html(cls, entry: dict[str, Any]) -> str:
        title = html.escape(str(entry["title"]))
        description = html.escape(str(entry.get("description", "")))
        category = html.escape(str(entry.get("category", "target")).title())
        slug = html.escape(str(entry["slug"]), quote=True)
        tags_value = entry.get("tags", [])
        tags = tags_value if isinstance(tags_value, list) else []
        tags_html = "".join(
            f"<span>{html.escape(str(tag))}</span>" for tag in tags
        )
        actions: list[str] = []
        if entry.get("playable") is True:
            actions.append(
                f'<a class="button primary" href="./showcase/{slug}/">Play</a>'
            )
        source = html.escape(str(entry["source"]), quote=True)
        actions.append(
            '<a class="button" href="https://github.com/rincorpes/tatuy/tree/main/'
            f'{source}">Source</a>'
        )
        docs = entry.get("docs")
        if isinstance(docs, str) and docs:
            actions.append(
                f'<a class="button" href="{cls._docs_href(docs, prefix="./")}">Docs</a>'
            )
        return f"""<article class="card">
  <div class="card-preview"><span>{title}</span></div>
  <div class="card-body">
    <div class="tags"><span>{category}</span>{tags_html}</div>
    <h3>{title}</h3>
    <p>{description}</p>
    <div class="actions">{"".join(actions)}</div>
  </div>
</article>"""

    @classmethod
    def _play_html(cls, entry: dict[str, Any]) -> str:
        title = html.escape(str(entry["title"]))
        description = html.escape(str(entry.get("description", "")))
        category = html.escape(str(entry.get("category", "target")).title())
        source = html.escape(str(entry["source"]), quote=True)
        entrypoint = html.escape(str(entry["entrypoint"]), quote=True)
        docs = entry.get("docs")
        docs_link = ""
        if isinstance(docs, str) and docs:
            docs_link = f'<a class="button" href="{cls._docs_href(docs, prefix="../../")}">Docs</a>'
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - Tatuy</title>
  <link rel="stylesheet" href="../../assets/site.css">
</head>
<body class="play-page">
<header class="site-header"><a class="brand" href="../../">Tatuy</a><nav><a href="../../docs/">Docs</a><a href="https://github.com/rincorpes/tatuy">GitHub</a></nav></header>
<main class="play-main">
  <section class="play-heading"><p class="eyebrow">{category}</p><h1>{title}</h1><p>{description} Browser-v0 gates enabled audio until the first game interaction; capture remains disabled and storage is session-only.</p></section>
  <div class="runtime-frame"><iframe id="tatuy-runtime" title="Tatuy {title} runtime" src="../../{entrypoint}" allow="fullscreen"></iframe></div>
  <div class="runtime-focus" data-focus-status data-focused="false">Click the game to focus controls</div>
  <div class="play-controls"><button type="button" data-action="restart">Restart</button><button type="button" data-action="fullscreen">Fullscreen</button><span class="status">Audio unlocks on first game interaction when enabled</span></div>
  <div class="actions">{docs_link}<a class="button" href="https://github.com/rincorpes/tatuy/tree/main/{source}">Source</a></div>
</main>
<script src="../../assets/site.js"></script>
</body>
</html>
"""

    @staticmethod
    def _docs_href(docs: str, *, prefix: str) -> str:
        relative = docs.removeprefix("docs/")
        if relative.endswith(".md"):
            relative = relative[:-3]
        if relative.endswith("/index"):
            relative = relative[:-5]
        relative = relative.strip("/")
        return f"{prefix}docs/{relative}/" if relative else f"{prefix}docs/"

    @staticmethod
    def _site_js() -> str:
        return """(() => {
  const frame = document.querySelector("#tatuy-runtime");
  const restart = document.querySelector('[data-action="restart"]');
  const fullscreen = document.querySelector('[data-action="fullscreen"]');
  const focusStatus = document.querySelector('[data-focus-status]');
  const scrollKeys = new Set(["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " ", "PageUp", "PageDown", "Home", "End"]);

  const setFocused = (focused) => {
    if (!focusStatus) return;
    focusStatus.dataset.focused = focused ? "true" : "false";
    focusStatus.textContent = focused
      ? "Game focused — controls captured"
      : "Click the game to focus controls";
  };

  const focusRuntime = () => {
    frame?.focus();
    frame?.contentWindow?.focus();
    setFocused(true);
  };

  const installRuntimeGuards = () => {
    try {
      const runtimeWindow = frame?.contentWindow;
      const runtimeDocument = runtimeWindow?.document;
      if (!runtimeWindow || !runtimeDocument) return;
      runtimeDocument.addEventListener("keydown", (event) => {
        if (scrollKeys.has(event.key)) event.preventDefault();
        setFocused(true);
      }, { capture: true });
      runtimeDocument.addEventListener("pointerdown", () => setFocused(true), { capture: true });
      runtimeWindow.addEventListener("blur", () => setFocused(false));
      runtimeDocument.addEventListener("visibilitychange", () => {
        if (runtimeDocument.hidden) setFocused(false);
      });
    } catch (_error) {
      // The runtime is expected to be same-origin on GitHub Pages. If a host
      // changes that policy, focus UX still works without same-origin guards.
    }
  };

  frame?.addEventListener("load", installRuntimeGuards);
  window.addEventListener("blur", () => {
    queueMicrotask(() => setFocused(document.activeElement === frame));
  });
  document.addEventListener("focusin", () => {
    if (document.activeElement !== frame) setFocused(false);
  });

  restart?.addEventListener("click", () => {
    if (frame) frame.src = frame.src;
    setFocused(false);
  });
  fullscreen?.addEventListener("click", async () => {
    await frame?.parentElement?.requestFullscreen?.();
    focusRuntime();
  });
  document.addEventListener("fullscreenchange", () => {
    if (document.fullscreenElement) focusRuntime();
  });
})();
"""

    @staticmethod
    def _site_css() -> str:
        return """
:root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #0d1117; color: #f0f6fc; }
* { box-sizing: border-box; }
body { margin: 0; background: radial-gradient(circle at top left, #182235 0, #0d1117 42%); color: #f0f6fc; }
a { color: inherit; }
.site-header, footer { max-width: 1180px; margin: 0 auto; padding: 24px 32px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }
.site-header nav { display: flex; gap: 24px; }
.site-header nav a, footer a { color: #aeb9c8; text-decoration: none; }
.brand { font-size: 1.35rem; font-weight: 800; text-decoration: none; letter-spacing: -.04em; }
main { max-width: 1180px; margin: 0 auto; padding: 72px 32px 96px; }
.hero { max-width: 900px; padding: 64px 0 96px; }
.eyebrow { color: #7dd3fc; font-size: .78rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
h1 { font-size: clamp(3rem, 8vw, 6.5rem); line-height: .95; letter-spacing: -.065em; margin: 18px 0 28px; }
h2 { font-size: clamp(2rem, 4vw, 3.25rem); letter-spacing: -.045em; margin: 10px 0 18px; }
h3 { font-size: 2rem; margin: 14px 0; }
.lede, .project-status p, .play-heading p { color: #aeb9c8; font-size: 1.2rem; line-height: 1.7; max-width: 760px; }
.actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 32px; }
.button, button { border: 1px solid #334155; background: #111827; color: #f8fafc; padding: 12px 18px; border-radius: 10px; text-decoration: none; font-weight: 700; cursor: pointer; }
.button.primary { background: #f8fafc; color: #0f172a; border-color: #f8fafc; }
.architecture { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; padding: 64px 0; border-top: 1px solid #273244; border-bottom: 1px solid #273244; }
pre { margin: 0; padding: 28px; border-radius: 14px; background: #111827; color: #cbd5e1; line-height: 1.65; overflow: auto; }
.showcase, .project-status { padding: 88px 0 24px; }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 24px; }
.status { color: #8b9bb0; font-size: .9rem; }
.catalog-grid { display: grid; gap: 24px; margin-top: 30px; }
.card { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr); border: 1px solid #273244; border-radius: 18px; overflow: hidden; background: rgba(17,24,39,.82); }
.card-preview { min-height: 320px; display: grid; place-items: center; background: repeating-linear-gradient(135deg, #111827 0 20px, #172033 20px 40px); font-size: 2rem; font-weight: 800; }
.card-body { padding: 40px; }
.card-body p { color: #aeb9c8; line-height: 1.65; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tags span { padding: 6px 9px; border-radius: 999px; background: #172033; color: #9fb0c5; font-size: .75rem; }
footer { border-top: 1px solid #273244; color: #8b9bb0; }
.play-main { padding-top: 48px; }
.play-heading h1 { font-size: clamp(3rem, 7vw, 5rem); }
.runtime-frame { width: min(100%, 960px); margin: 36px auto 0; border: 1px solid #334155; border-radius: 16px; overflow: hidden; background: #000; aspect-ratio: 4 / 3; }
.runtime-frame iframe { width: 100%; height: 100%; border: 0; display: block; }
.runtime-frame:fullscreen { width: 100vw; height: 100vh; max-width: none; margin: 0; border: 0; border-radius: 0; aspect-ratio: auto; display: grid; place-items: center; background: #000; }
.runtime-frame:fullscreen iframe { width: 100%; height: 100%; }
.runtime-focus { margin-top: 12px; color: #fbbf24; font-size: .9rem; font-weight: 700; }
.runtime-focus[data-focused="true"] { color: #86efac; }
.play-controls { display: flex; align-items: center; gap: 12px; margin-top: 16px; }
.play-controls .status { margin-left: auto; }
@media (max-width: 760px) { .architecture, .card { grid-template-columns: 1fr; } .site-header { align-items: flex-start; } .site-header nav { gap: 12px; flex-wrap: wrap; justify-content: end; } main { padding-inline: 20px; } h1 { font-size: 3.4rem; } .play-controls { align-items: flex-start; flex-wrap: wrap; } .play-controls .status { width: 100%; margin-left: 0; } }
"""
