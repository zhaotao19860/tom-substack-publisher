---
name: tom-substack-publisher
description: Use when the user asks for a Substack gateway article, 网关文章, L4/L7 gateway analysis, API/AI/inference/Agent/MCP gateway news, inference engine updates, or a two-day gateway topic review intended for researched, illustrated, human-approved web publication.
---

# Tom Substack Publisher

## Core Contract

Research the previous two Beijing-calendar days, select one defensible gateway topic, and prepare one illustrated Chinese article for technical practitioners. Use `Asia/Shanghai`; for run date D, the event window is D-2 00:00:00 through D-1 23:59:59.

Store every run under `/Users/tom/Desktop/substack/YYYY-MM-DD-topic-slug/`. Preparation does not authorize publication. Publish only after explicit approval of the current content fingerprint. Web publication must preserve `send_email=false`.

## Workflow

1. Read [references/research-matrix.md](references/research-matrix.md). Search all eight topic buckets in Chinese and English. Verify original dates, canonical sources, numbers, versions, and strong claims. Write `candidates.md` and `sources.json`. Stop when the two-day window cannot support a useful article.
2. Select exactly one topic for technical depth, source quality, practitioner value, and explanatory potential. Record why it won and why leading alternatives lost.
3. Read [references/article-contract.md](references/article-contract.md). Write `article.md` in Chinese, preserving English project names, APIs, versions, and code identifiers. Target 1,800-2,600 Chinese characters and about five minutes at 450 characters per minute.
4. Use **REQUIRED SUB-SKILL:** `ian-xiaohei-illustrations` for both the cover and the AI/hybrid body image. Give it the complete article, require a distinct explanatory concept for each role, and use its shot-list, prompt-design, generation, and QA workflow. Do not call `create-image` directly from this skill. Add one deterministic factual visual for exact data. Stop if the Ian skill is unavailable or an image still fails its QA checklist after one retry; do not substitute a decorative fallback.
5. Build and validate. The fingerprint covers the source Markdown, generated `article.html`, `sources.json`, and every image, so the HTML actually pasted into Substack is part of the approval boundary:

```bash
python3 /Users/tom/.comate/skills/tom-substack-publisher/scripts/build_preview.py RUN_DIR
python3 /Users/tom/.comate/skills/tom-substack-publisher/scripts/validate_article.py RUN_DIR --json
```

6. Write the absolute run path to `/Users/tom/Desktop/substack/latest-article-path.txt`. Present the title, subtitle, source count, unresolved risks, reading time, image count, preview path, and content fingerprint. Stop and request explicit approval for this exact fingerprint.
7. After approval, recompute the fingerprint. Any content, source, or image change invalidates approval. Read [references/substack-browser-publish.md](references/substack-browser-publish.md) and use **REQUIRED SUB-SKILL:** `browser:control-in-app-browser` to publish through the signed-in browser session.
8. Verify the public URL, title, body, images, and web-only state. Only then write `publish-receipt.json` with the approved fingerprint and `send_email=false`.

## Stop Conditions

- Do not fabricate a topic, date, source, benchmark, version, CVE, or causal claim.
- Do not continue with fewer than two verified sources or without a primary source.
- Do not bypass `ian-xiaohei-illustrations`, accept decorative AI images, or fall back to direct image generation when its workflow fails.
- Do not publish with missing images, failed validation, unresolved critical facts, stale approval, missing login, ambiguous publication, changed UI, or an unclear email setting.
- Never read, export, print, or store Substack cookies or passwords.
- Never describe a local preview, saved editor state, or draft as a successful public post.

## Completion Report

Before approval, report only preparation status and local paths. After verified publication, additionally report the public URL, publication time, content fingerprint, and confirmation that subscriber email was disabled.
