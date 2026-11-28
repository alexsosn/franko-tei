# Browser proofreading pilot

Refs #175 #176 #183 #190.

Each local batch is pinned to one exact commit and candidate blob. Re-fetch exact
commit bytes before opening or resuming; never silently migrate to a newer
reading. Use GitHub's public commit API only when main is selected, and the
existing native review issue form for submission. No account tokens. 
A compact dialog pairs the pinned source crop with a single native transcription field,
confirm/correct/defer decisions, local draft recovery and explicit JSON export.
Test browser-generated JSON using the existing Python validator on actual I/20.
No publication, adjudication or credit in this step.

The pilot uses origin-local sessions scoped to the candidate path and selected
reading ref (localStorage; at most 25 decisions and 32 KiB exported JSON per batch). The pencil in the text pane opens a dialog, with a
source crop (estimated box, contextual neighboring lines) and full scan link,
a single working transcription field, uncertainty notes (on demand), historical symbols, note,
save/confirm-and-next, defer and undo. Reopening the same candidate and ref resumes its pinned batch. Changing the
page, volume, candidate or explicit ref opens the corresponding batch instead.
Legacy single-key drafts remain intact and resume only on their matching candidate
and compatible ref. Return to that source to recover them. A batch opened from
main continues to use its originally pinned commit even as main advances. Preparing freezes the batch; copy JSON to the
public GitHub form. Only after saving/submitting externally should the user
clear the batch. A draft can also be explicitly discarded with confirmation.
No automatic submission, proof of inspection, acceptance or user credit.
The crop is above the field on narrow screens and beside it on wide screens.
Line selection shows line number and physical region, without a second excerpt.
The frozen literal remains in the pinned bundle target and is never replaced by
an edited value; font selection still uses the source language spans. No duplicate
transcription panel is needed for routine proofreading. This layout is also the
required base for future annotation editing, which is not yet a submission mode.
Image dimensions are checked, not image byte hashes; source crop is approximate.
Exact Git blob hash is computed from the fetched original candidate bytes.
The production CLI still decides trusted commit ancestry. The browser test
uses actual frozen I/20 and I/92 text and synthetic images; no scholarly decisions.

If the exact pinned candidate is unavailable or its Git blob changes, the
editor refuses to reopen the session, preserves the local data, and offers
a recovery download (not a submission bundle) or explicit discard.

## Historical character keyboard
Use the group selector: Diacritics, Letters (upper and lower case),
Superscript letters, Greek. The dotted circle is only a visual preview;
the button inserts the exact Unicode sequence at the editor selection,
without normalization. Key tooltip, accessible label and the last-inserted
character description include Unicode code points. Church Slavonic
breathing uses U+0486 (psili), U+0485 (dasia); iso and apostrof use
breathing then accent. Kamora is U+0311, yerok U+033E, vzmet U+A66F;
ordinary tilde U+0303 is offered separately, not treated as equivalent.
Pokrytie U+0487 may be added after a superscript letter when visible.
References: https://www.unicode.org/notes/tn41/tn41-1.pdf (Table 13)
and https://sci.ponomar.net/keyboard.html . The font cmap test covers
every key across the bundled Monomakh/Shafarik/Greek fallback stack;
this does not prove correct shaping of every historical combination.
