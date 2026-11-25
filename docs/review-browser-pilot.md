# Browser proofreading pilot

Refs #175 #176 #183 #190.

One local session pinned to one exact commit and candidate blob. Re-fetch exact
commit bytes before opening or resuming; never silently migrate to a newer
reading. Use GitHub's public commit API only when main is selected, and the
existing native review issue form for submission. No account tokens. 
A compact dialog contains source context, the original literal, a native editor,
confirm/correct/defer decisions, local draft recovery and explicit JSON export.
Test browser-generated JSON using the existing Python validator on actual I/20.
No publication, adjudication or credit in this step.

The pilot uses a single origin-local session (localStorage, at most 25 decisions
and 32 KiB exported JSON). The pencil in the text pane opens a dialog, with a
source crop (estimated box, contextual neighboring lines) and full scan link,
original literal, uncertainty notes, native editor, historical symbols, note,
save/confirm-and-next, defer and undo. Reopening resumes the pinned candidate
even if the reader has moved. Preparing freezes the batch; copy JSON to the
public GitHub form. Only after saving/submitting externally should the user
clear the batch. A draft can also be explicitly discarded with confirmation.
No automatic submission, proof of inspection, acceptance or user credit.
Image dimensions are checked, not image byte hashes; source crop is approximate.
Exact Git blob hash is computed from the fetched original candidate bytes.
The production CLI still decides trusted commit ancestry. The browser test
uses actual frozen text and a synthetic image; no scholarly decisions.

If the exact pinned candidate is unavailable or its Git blob changes, the
editor refuses to reopen the session, preserves the local data, and offers
a recovery download (not a submission bundle) or explicit discard.
