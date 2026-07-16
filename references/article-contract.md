# Substack Article Contract

## Contents

1. Run directory
2. Article metadata and structure
3. Image plan
4. Preview and validation
5. Approval report

## Run Directory

Create one directory per run:

```text
/Users/tom/Desktop/substack/YYYY-MM-DD-topic-slug/
├── candidates.md
├── sources.json
├── article.md
├── article.html
├── preview.html
├── images/
│   ├── cover-v1.png
│   ├── body-ai-v1.png
│   └── body-fact-v1.png
└── publish-receipt.json
```

`publish-receipt.json` is absent before verified publication. Use versioned image names and do not overwrite an earlier generation.

## Article Metadata and Structure

Start `article.md` with scalar YAML frontmatter:

```yaml
---
title: "具体、有判断力的标题"
subtitle: "说明变化、机制或影响的一句话"
run_date: "2026-07-15"
window_start: "2026-07-13T00:00:00+08:00"
window_end: "2026-07-14T23:59:59+08:00"
---
```

Write 1,800-2,600 Chinese characters in the readable body. Estimate at 450 Chinese characters per minute and keep the result between 4 and 6 minutes. Do not count long code blocks or the final source list as normal reading prose.

Use this sequence:

1. Short hook naming the new change or technical tension.
2. What happened in the two-day event window.
3. How the gateway, routing, scheduling, or inference mechanism works.
4. Why it matters, including limits and competing interpretations.
5. A clearly marked technical judgment.
6. Concrete implications or actions for practitioners.
7. Short canonical source list.

Keep paragraphs short. Use descriptive H2 headings, inline canonical links, one useful blockquote at most, and code only when it changes understanding. Preserve English project names, APIs, versions, and code identifiers. Do not use Markdown tables; convert exact comparisons into a deterministic image or structured bullets.

Facts and judgment must remain distinguishable. Avoid copied release language, generic AI transitions, inflated certainty, unsupported market trends, and invented context.

## Image Plan

Use at least three images with these exact Markdown role labels:

```markdown
![cover](images/cover-v1.png)
![body-ai](images/body-ai-v1.png)
![body-fact](images/body-fact-v1.png)
```

`body-hybrid` may replace `body-ai`. A fourth image is allowed only when it removes meaningful reader effort.

### Ian Xiaohei cover and body visual

Use **REQUIRED SUB-SKILL:** `ian-xiaohei-illustrations` for both AI-generated roles. The parent publisher must not call `create-image` directly; the Ian skill owns its own downstream image-generation call.

Give the Ian skill the complete article and the intended insertion points. Before generation, require one concise shot list that defines both images:

- `cover`: express the article's central tension or judgment as a thesis illustration;
- `body-ai` or `body-hybrid`: explain one mechanism, transition, or consequence that reduces reader effort.

Use the Ian skill for visual strategy, prompt design, generation, and its QA checklist. Make Xiaohei perform the core explanatory action. Use a fresh metaphor and a distinct composition for each image; the second image must add understanding rather than restate the cover. Do not pause for a separate image approval because the publisher's fingerprint approval covers the final article and image set.

Keep both images 16:9 with clean white backgrounds and versioned filenames. Short conceptual annotations are allowed when they pass manual text inspection. AI-rendered pixels must not carry exact versions, benchmark figures, commands, long labels, code, factual matrices, invented logos, or unsupported facts.

Reject an image when it is decorative, generic, duplicative, hard to understand, too dense, PPT-like, or when Xiaohei is only a mascot. Also reject garbled text, watermarks, clipped subjects, copied example compositions, and factual inventions. Retry once through the Ian workflow with a new filename and a tighter concept. Stop if the Ian skill is unavailable, unreadable, or cannot produce an image that passes its QA checklist. Do not fall back to direct `create-image` generation or an unrelated visual style.

### Deterministic factual visual

Use HTML/SVG for architecture, sequence, comparison, versions, commands, or exact data. Keep labels short, source every fact, and render to PNG at a stable 16:9 or 4:3 size with browser/Playwright screenshot support. Verify every label, arrow, number, and order against `sources.json`. Avoid dashboard chrome, nested cards, gradients, and dense legends.

## Preview and Validation

Build HTML after article and images are final:

```bash
python3 /Users/tom/.comate/skills/tom-substack-publisher/scripts/build_preview.py RUN_DIR
```

`preview.html` shows the real local images. `article.html` replaces local images with `data-tom-image` placeholders so the browser publisher can upload them to Substack in order. Raw HTML from Markdown is sanitized before either file is written.

Validate:

```bash
python3 /Users/tom/.comate/skills/tom-substack-publisher/scripts/validate_article.py RUN_DIR --json
```

Do not request approval until `ok` is true. Treat the returned SHA-256 value as the content fingerprint for the exact article, sources, and images.

## Approval Report

Show:

- run directory;
- title and subtitle;
- two-day window;
- verified source count and primary source count;
- unresolved factual risks;
- Chinese character count and reading estimate;
- cover/body image count and preview path;
- full content fingerprint.

Ask for explicit approval to publish that fingerprint to Substack web without subscriber email. Any title, subtitle, body, source, or image change requires rebuilding, validating, and asking again.
