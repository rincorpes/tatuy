"""Generate the static Tatuy showcase shell around docs and playables."""

from __future__ import annotations

import shutil
from pathlib import Path


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
        """Generate the showcase shell without replacing docs or runtime bundles.

        Args:
            featured_slug: Existing playable slug embedded by the featured page.

        Returns:
            Path to the composed web output root.

        Raises:
            FileNotFoundError: Required docs or featured playable output is missing.
        """
        docs_root = self.output_root / "docs"
        play_root = self.output_root / "play" / featured_slug
        if not (docs_root / "index.html").is_file():
            raise FileNotFoundError(
                f"Documentation build not found: {docs_root}"
            )
        if not (play_root / "index.html").is_file():
            raise FileNotFoundError(f"Playable build not found: {play_root}")

        assets_root = self.output_root / "assets"
        assets_root.mkdir(parents=True, exist_ok=True)
        (assets_root / "site.css").write_text(
            self._site_css(), encoding="utf-8"
        )
        (assets_root / "site.js").write_text(self._site_js(), encoding="utf-8")
        (self.output_root / "index.html").write_text(
            self._home_html(featured_slug), encoding="utf-8"
        )

        showcase_root = self.output_root / "showcase" / featured_slug
        if showcase_root.exists():
            shutil.rmtree(showcase_root)
        showcase_root.mkdir(parents=True)
        (showcase_root / "index.html").write_text(
            self._play_html(featured_slug), encoding="utf-8"
        )
        (self.output_root / ".nojekyll").touch()
        return self.output_root

    @staticmethod
    def _home_html(featured_slug: str) -> str:
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
    <div class="actions"><a class="button primary" href="./showcase/{featured_slug}/">Play Render Queue</a><a class="button" href="./docs/">Read the docs</a></div>
  </section>
  <section class="architecture">
    <div><p class="eyebrow">Architecture</p><h2>Game code stays separate from the host.</h2></div>
    <pre>Game\n  ↓\nScenes + Game Systems\n  ↓\nECS + Engine Features\n  ↓\nSystem / Render Pipelines\n  ↓\nBackend + Runtime Host</pre>
  </section>
  <section id="showcase" class="showcase">
    <div class="section-heading"><div><p class="eyebrow">Browser showcase</p><h2>Featured playable</h2></div><span class="status">Early web preview</span></div>
    <article class="card featured-card">
      <div class="card-preview"><span>Render Queue</span></div>
      <div class="card-body">
        <div class="tags"><span>Fundamental</span><span>Rendering</span><span>Browser playable</span></div>
        <h3>Render Queue</h3>
        <p>Inspect Tatuy's queued rendering path through the same canonical target used on desktop.</p>
        <div class="actions"><a class="button primary" href="./showcase/{featured_slug}/">Play</a><a class="button" href="https://github.com/rincorpes/tatuy/tree/main/examples/fundamentals/009_rendering/002_render_queue">Source</a><a class="button" href="./docs/learn/rendering/">Rendering docs</a></div>
      </div>
    </article>
  </section>
  <section class="project-status"><p class="eyebrow">Project status</p><h2>Experimental by design.</h2><p>Tatuy is alpha software. The Python foundation, browser host, examples, documentation, and future native runtime are evolving together.</p></section>
</main>
<footer><span>Tatuy · MIT licensed</span><a href="https://github.com/rincorpes/tatuy">GitHub</a></footer>
</body>
</html>
"""

    @staticmethod
    def _play_html(featured_slug: str) -> str:
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Render Queue - Tatuy</title>
  <link rel="stylesheet" href="../../assets/site.css">
</head>
<body class="play-page">
<header class="site-header"><a class="brand" href="../../">Tatuy</a><nav><a href="../../docs/">Docs</a><a href="https://github.com/rincorpes/tatuy">GitHub</a></nav></header>
<main class="play-main">
  <section class="play-heading"><p class="eyebrow">Rendering fundamental</p><h1>Render Queue</h1><p>Inspect Tatuy's queued rendering path in the browser. Browser-v0 runs without audio, capture, or persistent storage.</p></section>
  <div class="runtime-frame"><iframe id="tatuy-runtime" title="Tatuy Render Queue runtime" src="../../play/{featured_slug}/index.html" allow="fullscreen"></iframe></div>
  <div class="play-controls"><button type="button" data-action="restart">Restart</button><button type="button" data-action="fullscreen">Fullscreen</button><span class="status">Audio disabled in browser-v0</span></div>
  <div class="actions"><a class="button" href="../../docs/learn/rendering/">Rendering docs</a><a class="button" href="https://github.com/rincorpes/tatuy/tree/main/examples/fundamentals/009_rendering/002_render_queue">Source</a></div>
</main>
<script src="../../assets/site.js"></script>
</body>
</html>
"""

    @staticmethod
    def _site_js() -> str:
        return """(() => {
  const frame = document.querySelector("#tatuy-runtime");
  const restart = document.querySelector('[data-action="restart"]');
  const fullscreen = document.querySelector('[data-action="fullscreen"]');
  restart?.addEventListener("click", () => {
    if (frame) frame.src = frame.src;
  });
  fullscreen?.addEventListener("click", () => frame?.requestFullscreen?.());
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
.featured-card { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr); margin-top: 30px; border: 1px solid #273244; border-radius: 18px; overflow: hidden; background: rgba(17,24,39,.82); }
.card-preview { min-height: 320px; display: grid; place-items: center; background: repeating-linear-gradient(135deg, #111827 0 20px, #172033 20px 40px); font-size: 2rem; font-weight: 800; }
.card-body { padding: 40px; }
.card-body p { color: #aeb9c8; line-height: 1.65; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tags span { padding: 6px 9px; border-radius: 999px; background: #172033; color: #9fb0c5; font-size: .75rem; }
footer { border-top: 1px solid #273244; color: #8b9bb0; }
.play-main { padding-top: 48px; }
.play-heading h1 { font-size: clamp(3rem, 7vw, 5rem); }
.runtime-frame { margin-top: 36px; border: 1px solid #334155; border-radius: 16px; overflow: hidden; background: #000; aspect-ratio: 4 / 3; }
.runtime-frame iframe { width: 100%; height: 100%; border: 0; display: block; }
.play-controls { display: flex; align-items: center; gap: 12px; margin-top: 16px; }
.play-controls .status { margin-left: auto; }
@media (max-width: 760px) { .architecture, .featured-card { grid-template-columns: 1fr; } .site-header { align-items: flex-start; } .site-header nav { gap: 12px; flex-wrap: wrap; justify-content: end; } main { padding-inline: 20px; } h1 { font-size: 3.4rem; } .play-controls { align-items: flex-start; flex-wrap: wrap; } .play-controls .status { width: 100%; margin-left: 0; } }
"""
