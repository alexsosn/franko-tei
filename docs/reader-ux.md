# Reader UX and accessibility

Applies to the corpus reader, search, contents/index navigation, settings, annotation layers, annotation editing and proofreading. The reader is used for source-based scholarly work on phones as well as desktops. New functions must integrate with existing patterns rather than creating isolated layouts.

## Shared patterns

- Use the existing native dialog, heading, dismiss action, form field, primary action and disclosure patterns. Keep semantic HTML and native keyboard behavior. Every dialog needs an accessible name; icon-only buttons need an accessible label. Escape and Close restore focus to the invoker. Avoid nested modals.
- Use consistent left-aligned labels immediately above controls on narrow screens, full-width fields, a 4/8/12/16 spacing rhythm, and at least 44 CSS px for primary touch controls (project target above WCAG 2.2 AA minimum). Inputs/selects used on phones should have at least 16px text to avoid unintended iOS zoom. Keep historical script typography where necessary. Use visible focus and sufficient contrast.
- For independent fields use a responsive grid only when labels and values fit; otherwise use one column. Do not mix centered labels, intrinsic-width selects and full-width controls in the same form. Check long Ukrainian labels and mixed historical scripts. Use `minmax(0,1fr)`, `min-width:0` and wrapping rather than clipping.
- Keep the main action beside the task or directly following it. Choose one visually primary action per task. Avoid long blocks of help, repetitive labels and unexplained technical terms. Put secondary options behind native disclosures, show active settings when closed, and preserve the user's values on reopening.
- Use one clearly identifiable vertical scroll surface per dialog when possible; avoid a nested scroll area for search results. A long result list in Contents may use its dedicated scroll body. Keep dismissal accessible. Sticky controls must not obscure focused content or consume a short landscape viewport; test keyboard-open behavior on actual mobile browsers when available.
- Prefer existing CSS tokens/classes and component patterns. Consolidate conflicting selectors, not additional override chains. Do not use global CSS that changes manuscript display or editorial meaning. Do not change data schemas or search semantics merely to simplify a layout.
- Use visible status, no-results and recoverable error states; report incomplete index coverage, unavailable revisions and provisional readings explicitly. Do not report absent annotations as absence of historical phenomena.

## Search contract

A query and its primary action are together; volume and source use identical field styling. Annotation filters and historical character entry are disclosed separately. Non-default filters remain visible in the summary when collapsed. Valid submission collapses auxiliary panels to expose results but retains their values. Expansion mode has a persistent warning about incomplete annotation coverage. A query may be empty only for supported annotation searches; invalid source/filter combinations produce an explicit message without silently changing settings. Search results retain source identity, line anchors, provenance and exact diplomatic glyphs. Do not autocorrect or autocapitalize historical queries. Existing literal search, expansion search and other documented semantics are unchanged.

## Before every web PR

1. Research actual user task and existing implementation; capture a screenshot/viewport or reproduction, user-facing acceptance criteria and relevant sources.
2. Add a failing browser regression in the existing web tests before implementing changes. Cover behavior as well as geometry: no horizontal overflow at 320px, full labels and controls, correct focus, visible status, no lost values. Add fixture cases for empty, loading, failure and results where applicable.
3. Exercise 320×640, 390×844, 896×414 landscape, 1280×800 desktop; EN and UK; keyboard-only navigation, Escape, long strings and a narrow/short viewport. Test real iOS Safari or WebKit where available, including the on-screen keyboard. Chromium screenshots alone do not certify Safari.
4. Visually inspect before/after screenshots at phone and desktop sizes and capture them in the PR evidence, then run `python web/test_review.py` and relevant existing browser suites. Perform an independent adversarial review of scroll, focus, state, accessibility and research semantics before merging. Do not claim a visual pass when only source or synthetic assertions were inspected.
5. For a broad redesign, audit the other dialogs against this contract and track remaining exceptions with concrete follow-up issues; avoid unreviewed changes to unrelated transcription work.

## References

- [NN/g: Website Forms Usability](https://www.nngroup.com/articles/web-form-design/)
- [NN/g: Reduce Cognitive Load in Forms](https://www.nngroup.com/articles/4-principles-reduce-cognitive-load/)
- [Helsinki Design System: Building forms](https://hds.hel.fi/patterns/forms/form-building/)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/), especially 1.4.10 Reflow, 2.4.7 Focus Visible, 2.4.11 Focus Not Obscured and 2.5.8 Target Size (Minimum)
- [WAI-ARIA APG: Modal Dialog Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

These are project design requirements and acceptance targets, not a claim that the whole existing application already complies with WCAG.
