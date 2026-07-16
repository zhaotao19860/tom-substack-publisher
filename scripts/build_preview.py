#!/usr/bin/env python3
"""Build rich HTML and a standalone preview for a prepared article run."""

from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any


FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<meta>.*?)\n---\s*\n?", re.DOTALL)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
HTML_IMAGE_RE = re.compile(
    r'<p><img src="(?P<src>[^"]+)" alt="(?P<alt>[^"]*)"[^>]*/?></p>'
)
ALLOWED_TAGS = {
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "strong",
    "em",
    "s",
    "code",
    "pre",
    "blockquote",
    "ul",
    "ol",
    "li",
    "a",
    "hr",
    "br",
    "img",
    "figure",
    "figcaption",
}
VOID_TAGS = {"hr", "br", "img"}
DROP_CONTENT_TAGS = {"script", "style", "iframe", "object", "embed"}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title"},
    "code": {"class"},
    "ol": {"start"},
}


class _SafeArticleHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.drop_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in DROP_CONTENT_TAGS:
            self.drop_depth += 1
            return
        if self.drop_depth or tag not in ALLOWED_TAGS:
            return
        allowed = ALLOWED_ATTRIBUTES.get(tag, set())
        rendered: list[str] = []
        for name, value in attrs:
            name = name.lower()
            if name not in allowed or value is None:
                continue
            if name == "href" and not (
                value.startswith(("http://", "https://", "mailto:", "#"))
            ):
                continue
            if name == "src" and value.startswith(("javascript:", "data:text/html")):
                continue
            rendered.append(f'{name}="{html.escape(value, quote=True)}"')
        attributes = f" {' '.join(rendered)}" if rendered else ""
        suffix = " /" if tag in VOID_TAGS else ""
        self.parts.append(f"<{tag}{attributes}{suffix}>")

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in DROP_CONTENT_TAGS:
            if self.drop_depth:
                self.drop_depth -= 1
            return
        if self.drop_depth or tag not in ALLOWED_TAGS or tag in VOID_TAGS:
            return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self.drop_depth:
            self.parts.append(html.escape(data))

    def get_html(self) -> str:
        return "".join(self.parts)


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    values: dict[str, str] = {}
    for raw_line in match.group("meta").splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key.strip()] = value
    return values


def render_fragment(article: Path, output: Path, pandoc_bin: str) -> None:
    try:
        subprocess.run(
            [
                pandoc_bin,
                "--from=gfm-raw_html",
                "--to=html5",
                "--wrap=none",
                str(article),
                "-o",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise RuntimeError(f"pandoc failed: {message}") from exc


def _image_placeholders(fragment: str) -> str:
    def replace(match: re.Match[str]) -> str:
        src = html.escape(match.group("src"), quote=True)
        alt = html.escape(match.group("alt") or "article image")
        return (
            f'<p class="tom-image-placeholder" data-tom-image="{src}" '
            f'data-alt="{alt}">[插图：{alt}]</p>'
        )

    return HTML_IMAGE_RE.sub(replace, fragment)


def _sanitize_fragment(fragment: str) -> str:
    parser = _SafeArticleHTML()
    parser.feed(fragment)
    parser.close()
    return parser.get_html()


def build_preview(run_dir: Path, pandoc_bin: str = "pandoc") -> dict[str, Any]:
    run_dir = run_dir.expanduser().resolve()
    article = run_dir / "article.md"
    if not article.is_file():
        raise FileNotFoundError(f"article.md is missing: {article}")

    resolved_pandoc = shutil.which(pandoc_bin)
    if resolved_pandoc is None:
        raise RuntimeError(
            f"pandoc is required to build Substack HTML; command not found: {pandoc_bin}"
        )

    css_path = Path(__file__).resolve().parent.parent / "assets" / "article-preview.css"
    if not css_path.is_file():
        raise FileNotFoundError(f"preview CSS is missing: {css_path}")

    article_html = run_dir / "article.html"
    preview_html = run_dir / "preview.html"
    render_fragment(article, article_html, resolved_pandoc)

    fragment = _sanitize_fragment(article_html.read_text(encoding="utf-8"))
    article_html.write_text(_image_placeholders(fragment), encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    metadata = _frontmatter(article)
    title = html.escape(metadata.get("title", "Substack article preview"))
    subtitle = html.escape(metadata.get("subtitle", ""))
    subtitle_html = f'<p class="article-subtitle">{subtitle}</p>' if subtitle else ""
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
{css}
  </style>
</head>
<body>
  <main class="article-preview">
    <header class="article-header">
      <p class="article-kicker">SUBSTACK PREVIEW</p>
      <h1>{title}</h1>
      {subtitle_html}
    </header>
    <article>
{fragment}
    </article>
  </main>
</body>
</html>
"""
    preview_html.write_text(page, encoding="utf-8")

    markdown = article.read_text(encoding="utf-8")
    return {
        "article_html": str(article_html),
        "preview_html": str(preview_html),
        "image_count": len(IMAGE_RE.findall(markdown)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--pandoc", default="pandoc")
    args = parser.parse_args()
    result = build_preview(args.run_dir, pandoc_bin=args.pandoc)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
