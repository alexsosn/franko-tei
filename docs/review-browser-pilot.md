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
