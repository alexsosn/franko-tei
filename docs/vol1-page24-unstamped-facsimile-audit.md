# I/24 (XV): collation against unstamped facsimile photographs

On 2026-11-26 the user supplied two photographs of an unstamped facsimile of the same printed page. The full view shows the folio XV and identical physical line breaks; the second is a rotated lower-page detail. Both show the final two lines without the library stamp present on the pinned JPEG. This is supplementary visual evidence of the printed edition, not two independent textual witnesses. No images are committed or publicly rehosted. The exact byte SHA256 values and all 42 aligned physical positions (folio plus 41 body rows) are in [the collation record](../pilot/reviews/vol1_scan00024_unstamped_facs_20261126.json). Both prior frozen readings remain unchanged.

## Recovered readings

| Stable source line | Reading on unstamped facsimile |
|---|---|
| palaea-line-04 | зволених до читаня, але по просту канонїчних. Під назвою Палеї |
| palaea-line-05 | звісні були в старій Руси два твори, що не мають іс собою нїчого |

The lower-page detail confirms **іс**, not modernized **із**, and **Палеї**, **нїчого**. The first impression in chat normalized іс to із; the enlargement corrects that. No text inferred from the next page. The page itself ends with нїчого (sentence continues). The pinned scan remains occluded; the recovered text comes specifically from the unstamped photographs.

## Rest of page

Collated all physical positions against the prior alternate reading; confirmed several historical forms where the first candidate differs, including віданя, манїхейських, дуалїстичних, висше, богомільськими, еміґрантами, лїтописї, рядї, числї. Noted a printed semicolon after Ми знаємо and a comma following Южно-русскихъ. The complete comparison includes both prior readings, not only changed lines. Distinguish exact glyph encoding, incidental ink specks and punctuation: the collation remains provisional, not verified or a blind independent reading.

## Projection blocker and acceptance criteria

The original source validation requires each occluded line to have an unreadable suffix and the existing accepted-correction projection expressly refuses gap-bearing lines (see [adjudication contract](review-adjudication.md)). Do not remove the actual obstruction metadata, falsify image provenance or create a synthetic issue submission. The recovered strings are ready for a future source-linked editorial projection. It must bind the old candidate blob, original obscuration and supplementary photo digests, retain stable line IDs, distinguish an image obstruction from a real textual lacuna, reannotate recovered suffixes and display/export the complete reading without an editorial ellipsis while preserving the original scan-only reading. Test against the real two lines and reject mismatched source/line/photograph claims. No code change in this evidence PR; no active corpus correction claimed. Separate review rechecked the lower crop and line identity, especially іс vs із and final нїчого.
