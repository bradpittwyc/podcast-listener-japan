import re
import pykakasi

_kks = None

def get_kks():
    global _kks
    if _kks is None:
        _kks = pykakasi.kakasi()
    return _kks

HAS_KANJI_RE = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')
KANA_WORD_RE = re.compile(r'[\u3040-\u30ff\u31f0-\u31ff]{2,}')
WORD_CLEAN_RE = re.compile(r'[^\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff a-zA-Z0-9]')

def text_to_ruby(text: str) -> str:
    """Converts Japanese text into HTML with <ruby> and <rt> tags for Kanji."""
    if not text:
        return text

    kks = get_kks()
    result = kks.convert(text)
    html_parts = []

    for item in result:
        orig = item.get('orig', '')
        hira = item.get('hira', '')

        if not orig:
            continue

        if not HAS_KANJI_RE.search(orig):
            if KANA_WORD_RE.search(orig):
                html_parts.append(f'<span class="word" data-word="{orig}">{orig}</span>')
            else:
                html_parts.append(orig)
            continue

        # Match common prefix
        prefix_len = 0
        while (prefix_len < len(orig) and prefix_len < len(hira) and orig[prefix_len] == hira[prefix_len]):
            prefix_len += 1

        # Match common suffix
        suffix_len = 0
        while (suffix_len < len(orig) - prefix_len and 
               suffix_len < len(hira) - prefix_len and 
               orig[len(orig) - 1 - suffix_len] == hira[len(hira) - 1 - suffix_len]):
            suffix_len += 1

        prefix = orig[:prefix_len]
        suffix = orig[len(orig) - suffix_len:] if suffix_len > 0 else ""

        core_orig = orig[prefix_len:len(orig) - suffix_len if suffix_len > 0 else len(orig)]
        core_hira = hira[prefix_len:len(hira) - suffix_len if suffix_len > 0 else len(hira)]

        if core_orig:
            ruby_item = f'<span class="word" data-word="{orig}"><ruby>{core_orig}<rt>{core_hira}</rt></ruby></span>'
        else:
            ruby_item = ""

        html_parts.append(f"{prefix}{ruby_item}{suffix}")

    return "".join(html_parts)

def text_to_word_spans(text: str) -> str:
    """Converts Japanese text into clickable word spans."""
    if not text:
        return ""
    kks = get_kks()
    result = kks.convert(text)
    html_parts = []
    for item in result:
        orig = item.get('orig', '')
        if not orig:
            continue
        cleaned = WORD_CLEAN_RE.sub('', orig)
        if cleaned:
            html_parts.append(f'<span class="word" data-word="{cleaned}">{orig}</span>')
        else:
            html_parts.append(orig)
    return "".join(html_parts)

def batch_to_ruby(sentences: list[str]) -> list[dict]:
    """Converts a batch of sentences to ruby HTML dicts and word HTML dicts."""
    res = []
    for s in sentences:
        res.append({
            "text": s,
            "ruby_html": text_to_ruby(s),
            "word_html": text_to_word_spans(s)
        })
    return res
