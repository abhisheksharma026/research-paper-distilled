"""Figure and table labels, shared so that every script agrees on what a caption is.

Covers "Figure 3.1:" and "Table 2:", and the IEEE and Springer forms "Fig. 4.", "FIG. 4." and "TABLE II".
"""
LABEL = r'(?:Figure|Fig\.|FIG\.|Table|TABLE) (?:[0-9A-Z]+\.)?(?:\d+|[IVXL]+)\b'


def caption_after(label):
    """What follows a label that opens a caption: a colon, or a full stop and a space.
    An IEEE "TABLE II" stands alone on its line, so whitespace follows it."""
    return r'\s' if label.startswith('TABLE') else r'(?::|\.\s)'
