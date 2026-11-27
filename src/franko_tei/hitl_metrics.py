"""Literal, fixed-line CER for a frozen human-reviewed HITL reference.

Inputs must already be source-validated and aligned by the trusted operator.
This evaluator does not authenticate reviewers or promote editorial status.
"""


def _distance(reference, candidate):
    previous = list(range(len(candidate) + 1))
    for i, a in enumerate(reference, 1):
        current = [i]
        for j, b in enumerate(candidate, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def score_lines(reference, baseline, retry=None):
    """Score explicit reviewed rows only; missing reference rows are unscored.

    All mappings use the same physical line IDs. A retry must contain exactly
    the baseline line IDs; structural changes need external alignment first.
    No Unicode normalization, whitespace trimming or case folding.
    """
    for lines in (reference, baseline) + (() if retry is None else (retry,)):
        if not isinstance(lines, dict) or any(
            not isinstance(k, str) or not k or not isinstance(v, str)
            for k, v in lines.items()
        ):
            raise ValueError('expected line ID to literal text mapping')
    if not baseline or not reference.keys() <= baseline.keys():
        raise ValueError('unknown reference line or empty baseline')
    if retry is not None and retry.keys() != baseline.keys():
        raise ValueError('retry line IDs differ; explicit alignment required')
    characters = sum(map(len, reference.values()))

    def measure(candidate):
        rows = [{'line_id': key, 'reference_characters': len(reference[key]),
                 'edits': _distance(reference[key], candidate[key])}
                for key in baseline if key in reference]
        edits = sum(row['edits'] for row in rows)
        return {'edits': edits, 'reference_characters': characters,
                'cer': edits / characters if characters else None,
                'rows': rows}

    return {**measure(baseline), 'method': 'literal Unicode code-point CER',
            'reviewed_lines': len(reference), 'eligible_lines': len(baseline),
            'complete': reference.keys() == baseline.keys(),
            'retry': None if retry is None else measure(retry)}
