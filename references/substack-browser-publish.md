# Guarded Substack Browser Publication

## Preconditions

Use **REQUIRED SUB-SKILL:** `browser:control-in-app-browser` because publishing depends on the user's signed-in Substack browser session.

Proceed only when all conditions are true:

- local validation returned `ok: true`;
- the user explicitly approved the displayed content fingerprint;
- recomputing the fingerprint returns the same value;
- the target publication is unambiguous;
- the browser is signed in as the expected account.

Never inspect, export, print, or persist cookies or passwords. The earlier decision to use browser publishing is not approval for a specific article.

## Create and Inspect the Post

1. Open the publication dashboard and inspect the visible account/publication identity.
2. Create a new text post. If Substack shows an existing non-empty editor, stop instead of overwriting it.
3. Fill the title and subtitle from frontmatter.
4. Read `article.html`. Focus the ProseMirror/Tiptap body editor and insert it as `text/html`, not with a plain-text fill operation. Prefer an actual paste event with HTML clipboard data so the editor records a normal transaction. Do not assign `innerHTML` directly; that can bypass editor state and autosave.
5. Verify headings, bold text, links, lists, blockquotes, and code blocks in the editor DOM.
6. For each `data-tom-image` placeholder in document order, remove the placeholder paragraph, use the editor's image upload control, upload the referenced local file, and verify the uploaded image appears at that location.
7. Set the cover/thumbnail using `images/cover-vN.png` when the editor exposes a separate cover setting.
8. Wait for the visible saved state. Compare title, subtitle, major heading order, link count, and image count with the local preview.

If HTML paste is blocked, use the rendered local article as the copy source and perform a normal browser copy/paste. Never fall back to pasting raw Markdown or setting the editor DOM without a saved-state verification.

## Publish Web Only

1. Recompute and compare the approved content fingerprint immediately before entering publication settings.
2. Open the review/continue step and inspect all delivery choices.
3. Select the option whose visible meaning is web publication without subscriber email. Explicitly verify that email delivery, inbox delivery, or equivalent subscriber-send control is disabled.
4. If the interface exposes only a combined web-and-email action, or the email state is unclear, stop without publishing.
5. Publish once. Do not retry an uncertain click.

The invariant is `send_email=false`. Do not enable a subscriber email, notification blast, or mass-send option even if it is selected by default.

## Verify and Record

After the action:

1. Capture the returned public URL from the interface.
2. Open it in a normal public post view.
3. Verify the title, subtitle, heading order, body presence, links, image count, and public state.
4. Treat missing URL, author-only editor URL, preview URL, partial body, or missing images as failure.
5. Only after successful verification, write `publish-receipt.json`:

```json
{
  "status": "published",
  "public_url": "https://publication.substack.com/p/article-slug",
  "published_at": "2026-07-15T18:30:00+08:00",
  "content_fingerprint": "64-character-sha256",
  "send_email": false
}
```

Report the verified URL and `send_email=false`.

## Stop Conditions

Stop and preserve local artifacts when login is missing, account/publication identity is ambiguous, the editor is unexpectedly non-empty, rich formatting did not persist, an image failed to upload, saved state is absent, the fingerprint changed, the UI changed materially, delivery controls are unclear, or public verification fails.
