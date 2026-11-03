"""Trains and serves word embeddings used to score guesses by semantic proximity,
the same way Cemantix/Pedantix rank a guess against the secret word(s).

Implementation note: gensim/scipy don't ship binary wheels for brand-new Python
versions for a while after release, so instead of word2vec we build vectors
ourselves with plain numpy: a windowed co-occurrence matrix -> PPMI weighting
-> truncated SVD. This is the classic "distributional semantics" recipe
(GloVe/word2vec are refinements of the same idea) and is plenty for a corpus
the size of a few rap catalogs.
"""
import json
from functools import lru_cache

import numpy as np
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Song
from app.text_utils import normalize_word

WINDOW = 5
MIN_COUNT = 2
VECTOR_SIZE = 150


def build_corpus(db: Session) -> list[list[str]]:
    """One "sentence" per song: its title words + normalized lyrics word tokens, in order.

    Title words are folded into the sentence (rather than trained separately) so that
    words which only ever appear as a song title still end up with a usable vector.
    """
    sentences: list[list[str]] = []
    for tokens, title_tokens in db.query(Song.tokens, Song.title_tokens).all():
        words = [normalize_word(t["t"]) for t in tokens if t["w"]]
        words = [w for w in words if w]
        if words:
            sentences.append(list(title_tokens) + words)
    return sentences


def _build_vocab(sentences: list[list[str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sent in sentences:
        for w in sent:
            counts[w] = counts.get(w, 0) + 1
    vocab = [w for w, c in counts.items() if c >= MIN_COUNT]
    return {w: i for i, w in enumerate(sorted(vocab))}


def _cooccurrence_matrix(sentences: list[list[str]], vocab: dict[str, int]) -> np.ndarray:
    n = len(vocab)
    mat = np.zeros((n, n), dtype=np.float64)
    for sent in sentences:
        idxs = [vocab[w] for w in sent if w in vocab]
        for i, wi in enumerate(idxs):
            lo = max(0, i - WINDOW)
            hi = min(len(idxs), i + WINDOW + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                dist = abs(j - i)
                mat[wi, idxs[j]] += 1.0 / dist
    return mat


def _ppmi(cooc: np.ndarray) -> np.ndarray:
    total = cooc.sum()
    if total == 0:
        return cooc
    row_sums = cooc.sum(axis=1, keepdims=True)
    col_sums = cooc.sum(axis=0, keepdims=True)
    expected = (row_sums @ col_sums) / total
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((cooc + 1e-12) / (expected + 1e-12))
    pmi[~np.isfinite(pmi)] = 0.0
    return np.maximum(pmi, 0.0)


def train_and_save(db: Session, vector_size: int = VECTOR_SIZE) -> int:
    sentences = build_corpus(db)
    if not sentences:
        raise ValueError("No songs in DB yet — collect & import some lyrics first.")

    vocab = _build_vocab(sentences)
    if len(vocab) < 10:
        raise ValueError(f"Vocabulary too small ({len(vocab)} words) — collect more lyrics first.")

    cooc = _cooccurrence_matrix(sentences, vocab)
    ppmi = _ppmi(cooc)

    k = min(vector_size, min(ppmi.shape) - 1)
    u, s, _vt = np.linalg.svd(ppmi, full_matrices=False)
    vectors = u[:, :k] * np.sqrt(s[:k])

    settings.models_dir.mkdir(parents=True, exist_ok=True)
    np.save(settings.models_dir / "vectors.npy", vectors)
    with open(settings.models_dir / "vocab.json", "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False)

    reload_model()
    return len(vocab)


class _Model:
    def __init__(self, vectors: np.ndarray, vocab: dict[str, int]):
        self.vectors = vectors
        self.vocab = vocab
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9
        self.unit_vectors = vectors / norms

    def __contains__(self, word: str) -> bool:
        return word in self.vocab

    def vector(self, word: str) -> np.ndarray:
        return self.vectors[self.vocab[word]]


@lru_cache(maxsize=1)
def _load_model() -> _Model:
    vectors_path = settings.models_dir / "vectors.npy"
    vocab_path = settings.models_dir / "vocab.json"
    if not vectors_path.exists() or not vocab_path.exists():
        raise RuntimeError(
            "No trained embeddings found. Run `python scripts/train_embeddings.py` after "
            "collecting at least a handful of songs."
        )
    vectors = np.load(vectors_path)
    vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
    return _Model(vectors, vocab)


def reload_model() -> None:
    _load_model.cache_clear()


def target_vector(title_tokens: list[str]) -> np.ndarray | None:
    model = _load_model()
    vecs = [model.vector(w) for w in title_tokens if w in model]
    if not vecs:
        return None
    return np.mean(vecs, axis=0)


def score_guess(guess_norm: str, title_tokens: list[str]) -> tuple[float, int | None]:
    """Returns (similarity in [-1, 1], rank) where rank=1 is the closest possible word.

    Falls back to (0.0, None) if the guess or the whole title is out of vocabulary.
    """
    model = _load_model()
    if guess_norm not in model:
        return 0.0, None

    tvec = target_vector(title_tokens)
    if tvec is None:
        return 0.0, None

    tvec_unit = tvec / (np.linalg.norm(tvec) + 1e-9)
    sims = model.unit_vectors @ tvec_unit

    similarity = float(sims[model.vocab[guess_norm]])
    rank = int((sims > similarity).sum()) + 1

    return similarity, rank
