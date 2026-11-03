import re

from unidecode import unidecode

# A "word" token is a run of unicode letters/digits (mixed, e.g. "2k17"), optionally
# joined by an apostrophe (e.g. "j'ai"). Anything else (spaces, newlines, punctuation)
# is kept as-is and always visible.
_TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*|[^\w\s]+|\s+", re.UNICODE)


def tokenize(text: str) -> list[dict]:
    """Split text into tokens preserving layout.

    Returns a list of {"t": original_text, "w": is_word} dicts that can be
    concatenated back into the exact original string.
    """
    tokens = []
    for match in _TOKEN_RE.finditer(text):
        chunk = match.group(0)
        # letters AND digit runs are guessable "words"; only punctuation/whitespace aren't.
        is_word = bool(re.match(r"^[^\W_]", chunk, re.UNICODE))
        tokens.append({"t": chunk, "w": is_word})
    return tokens


def normalize_word(word: str) -> str:
    """Lowercase + strip accents + strip any residual punctuation, for matching/embeddings."""
    word = unidecode(word).lower()
    word = re.sub(r"[^a-z0-9']", "", word)
    return word


def distinct_word_tokens(text: str) -> list[str]:
    """Normalized word tokens from text, deduped, keeping first-occurrence order."""
    return list(
        dict.fromkeys(normalize_word(t["t"]) for t in tokenize(text) if t["w"] and normalize_word(t["t"]))
    )


def clean_lyrics(raw: str) -> str:
    """Strip common Genius scraping artifacts from a lyrics blob."""
    text = raw

    # Leading "12 ContributorsSong Title Lyrics" header some scrapes leave in.
    text = re.sub(r"^\d+\s*Contributors?.*?Lyrics", "", text, count=1, flags=re.DOTALL)

    # Trailing "...123Embed" noise left by the Genius embed widget counter.
    text = re.sub(r"\d*Embed$", "", text.strip())

    return text.strip()
