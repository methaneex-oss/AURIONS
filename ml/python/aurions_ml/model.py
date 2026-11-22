"""Small, randomly initialized decoder-only Transformer baseline.

This is an owned trainable model component, not a pretrained-model adapter.
The byte tokenizer is deliberately language-agnostic: UTF-8 bytes are tokens.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
import re
from typing import Any

import torch
from torch import nn


@dataclass(frozen=True)
class DecoderConfig:
    vocab_size: int = 259
    context_length: int = 128
    width: int = 96
    heads: int = 4
    layers: int = 2
    feed_forward_width: int = 384
    dropout: float = 0.0

    def validate(self) -> None:
        if self.vocab_size < 259:
            raise ValueError("vocab_size must reserve byte, BOS, EOS and PAD IDs")
        if self.context_length < 2:
            raise ValueError("context_length must be at least 2")
        if self.width < 8 or self.heads < 1 or self.width % self.heads:
            raise ValueError("width must be >= 8 and divisible by heads")
        if self.layers < 1 or self.feed_forward_width < self.width:
            raise ValueError("invalid Transformer depth or feed-forward width")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")


class ByteTokenizer:
    """Reversible UTF-8 byte tokenizer with explicit boundary tokens."""

    PAD = 258
    BOS = 256
    EOS = 257
    VOCAB_SIZE = 259
    VERSION = "aurions-byte-v1"

    def encode(self, text: str, *, add_boundaries: bool = True) -> list[int]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        ids = list(text.encode("utf-8"))
        return [self.BOS, *ids, self.EOS] if add_boundaries else ids

    def decode(self, ids: list[int]) -> str:
        raw = bytearray()
        for token in ids:
            if 0 <= token <= 255:
                raw.append(token)
            elif token not in (self.PAD, self.BOS, self.EOS):
                raise ValueError(f"token ID out of range: {token}")
        return raw.decode("utf-8", errors="replace")


class ByteBPETokenizer:
    """Deterministic trainable byte-level BPE tokenizer with frozen merge lineage."""

    VERSION = "aurions-byte-bpe-v1"
    PAD = 0
    BOS = 1
    EOS = 2
    BYTE_OFFSET = 3
    BASE_VOCAB_SIZE = 259

    def __init__(self, merges: list[tuple[int, int]], training_corpus_sha256: str) -> None:
        if re.fullmatch(r"[0-9a-f]{64}", training_corpus_sha256 or "") is None:
            raise ValueError("tokenizer training corpus digest must be a SHA-256 hex digest")
        self.merges = tuple((int(left), int(right)) for left, right in merges)
        self.training_corpus_sha256 = training_corpus_sha256
        pieces: list[bytes] = [b"", b"", b""]
        pieces.extend(bytes([value]) for value in range(256))
        for index, (left, right) in enumerate(self.merges):
            new_id = self.BASE_VOCAB_SIZE + index
            if not (self.BYTE_OFFSET <= left < new_id and self.BYTE_OFFSET <= right < new_id):
                raise ValueError("BPE merge references a token that is not already defined")
            pieces.append(pieces[left] + pieces[right])
        self._token_bytes = tuple(pieces)

    @property
    def vocab_size(self) -> int:
        return self.BASE_VOCAB_SIZE + len(self.merges)

    @classmethod
    def train(
        cls, text: str, *, vocab_size: int = 512, min_frequency: int = 2,
        min_tokens: int = 0
    ) -> "ByteBPETokenizer":
        if not isinstance(text, str) or not text:
            raise ValueError("tokenizer training text must be non-empty")
        if vocab_size < cls.BASE_VOCAB_SIZE or vocab_size > 4096:
            raise ValueError("BPE vocab_size must be between 259 and 4096")
        if min_frequency < 2:
            raise ValueError("min_frequency must be at least 2")
        if min_tokens < 0:
            raise ValueError("min_tokens cannot be negative")

        corpus_bytes = text.encode("utf-8")
        sequences = [[cls.BYTE_OFFSET + value for value in corpus_bytes]]
        merges: list[tuple[int, int]] = []
        while cls.BASE_VOCAB_SIZE + len(merges) < vocab_size:
            pair_counts = Counter(
                pair for sequence in sequences for pair in zip(sequence, sequence[1:])
            )
            if not pair_counts:
                break
            pair, frequency = max(pair_counts.items(), key=lambda item: (item[1], item[0]))
            if frequency < min_frequency:
                break

            new_id = cls.BASE_VOCAB_SIZE + len(merges)
            merged_sequences: list[list[int]] = []
            for sequence in sequences:
                merged: list[int] = []
                index = 0
                while index < len(sequence):
                    if index + 1 < len(sequence) and (sequence[index], sequence[index + 1]) == pair:
                        merged.append(new_id)
                        index += 2
                    else:
                        merged.append(sequence[index])
                        index += 1
                merged_sequences.append(merged)
            if min_tokens and len(merged_sequences[0]) < min_tokens:
                break
            sequences = merged_sequences
            merges.append(pair)

        return cls(merges, hashlib.sha256(corpus_bytes).hexdigest())

    def encode(self, text: str, *, add_boundaries: bool = True) -> list[int]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        tokens = [self.BYTE_OFFSET + value for value in text.encode("utf-8")]
        for new_id, pair in enumerate(self.merges, start=self.BASE_VOCAB_SIZE):
            merged: list[int] = []
            index = 0
            while index < len(tokens):
                if index + 1 < len(tokens) and (tokens[index], tokens[index + 1]) == pair:
                    merged.append(new_id)
                    index += 2
                else:
                    merged.append(tokens[index])
                    index += 1
            tokens = merged
        return [self.BOS, *tokens, self.EOS] if add_boundaries else tokens

    def decode(self, token_ids: list[int]) -> str:
        raw = bytearray()
        for token_id in token_ids:
            if self.BYTE_OFFSET <= token_id < self.vocab_size:
                raw.extend(self._token_bytes[token_id])
            elif token_id not in (self.PAD, self.BOS, self.EOS):
                raise ValueError(f"token ID out of range: {token_id}")
        return raw.decode("utf-8", errors="replace")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.VERSION,
            "vocab_size": self.vocab_size,
            "special_tokens": {"pad": self.PAD, "bos": self.BOS, "eos": self.EOS},
            "merges": [[left, right] for left, right in self.merges],
            "training_corpus_sha256": self.training_corpus_sha256,
        }

    @classmethod
    def from_dict(cls, metadata: dict[str, Any]) -> "ByteBPETokenizer":
        if not isinstance(metadata, dict) or metadata.get("name") != cls.VERSION:
            raise ValueError("unsupported tokenizer identity")
        if metadata.get("special_tokens") != {
            "pad": cls.PAD, "bos": cls.BOS, "eos": cls.EOS
        }:
            raise ValueError("tokenizer special-token mapping is incompatible")
        raw_merges = metadata.get("merges")
        if not isinstance(raw_merges, list) or any(
            not isinstance(pair, list) or len(pair) != 2 or
            any(not isinstance(value, int) for value in pair)
            for pair in raw_merges
        ):
            raise ValueError("tokenizer merge table is malformed")
        tokenizer = cls(
            [(pair[0], pair[1]) for pair in raw_merges],
            metadata.get("training_corpus_sha256", ""),
        )
        if metadata.get("vocab_size") != tokenizer.vocab_size:
            raise ValueError("tokenizer vocabulary size does not match its merge table")
        return tokenizer


class DecoderOnlyTransformer(nn.Module):
    """Causal language model initialized from this model's own random weights."""

    def __init__(self, config: DecoderConfig | None = None) -> None:
        super().__init__()
        self.config = config or DecoderConfig()
        self.config.validate()
        self.token_embedding = nn.Embedding(self.config.vocab_size, self.config.width)
        self.position_embedding = nn.Embedding(self.config.context_length, self.config.width)
        layer = nn.TransformerEncoderLayer(
            d_model=self.config.width,
            nhead=self.config.heads,
            dim_feedforward=self.config.feed_forward_width,
            dropout=self.config.dropout,
            activation="gelu",
            batch_first=True,
            norm_first=False,
        )
        self.blocks = nn.TransformerEncoder(layer, num_layers=self.config.layers)
        self.final_norm = nn.LayerNorm(self.config.width)
        self.output = nn.Linear(self.config.width, self.config.vocab_size, bias=False)
        self.output.weight = self.token_embedding.weight

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        if token_ids.ndim != 2:
            raise ValueError("token_ids must have shape [batch, sequence]")
        _, length = token_ids.shape
        if length < 1 or length > self.config.context_length:
            raise ValueError("sequence length is outside configured context")
        positions = torch.arange(length, device=token_ids.device).unsqueeze(0)
        hidden = self.token_embedding(token_ids) + self.position_embedding(positions)
        causal_mask = torch.triu(
            torch.ones(length, length, dtype=torch.bool, device=token_ids.device), diagonal=1
        )
        hidden = self.blocks(hidden, mask=causal_mask)
        return self.output(self.final_norm(hidden))

    def architecture_manifest(self) -> dict[str, Any]:
        return {"architecture": "decoder-only-causal-transformer", **asdict(self.config)}
