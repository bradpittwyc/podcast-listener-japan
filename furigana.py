import re
import pykakasi

_kks = None

def get_kks():
    global _kks
    if _kks is None:
        _kks = pykakasi.kakasi()
    return _kks

HAS_KANJI_RE = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')
WORD_CLEAN_RE = re.compile(r'[^\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff a-zA-Z0-9]')

def process_sentence(text: str) -> dict:
    """Processes a Japanese sentence into both ruby_html (Furigana) and word_html (tokenized words)."""
    if not text:
        return {"text": "", "ruby_html": "", "word_html": ""}

    kks = get_kks()
    tokens = kks.convert(text)

    ruby_parts = []
    word_parts = []

    for item in tokens:
        orig = item.get('orig', '')
        hira = item.get('hira', '')

        if not orig:
            continue

        cleaned = WORD_CLEAN_RE.sub('', orig)
        if not cleaned:
            ruby_parts.append(orig)
            word_parts.append(orig)
            continue

        # Build word_html for plain mode
        word_parts.append(f'<span class="word" data-word="{cleaned}">{orig}</span>')

        # Build ruby_html for furigana mode
        if not HAS_KANJI_RE.search(orig):
            ruby_parts.append(f'<span class="word" data-word="{cleaned}">{orig}</span>')
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
            ruby_item = f'<ruby>{core_orig}<rt>{core_hira}</rt></ruby>'
        else:
            ruby_item = core_orig

        ruby_parts.append(f'<span class="word" data-word="{cleaned}">{prefix}{ruby_item}{suffix}</span>')

    return {
        "text": text,
        "ruby_html": "".join(ruby_parts),
        "word_html": "".join(word_parts)
    }

def batch_to_ruby(sentences: list[str]) -> list[dict]:
    """Converts a batch of sentences into ruby and word HTML dicts."""
    return [process_sentence(s) for s in sentences]
