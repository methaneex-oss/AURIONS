"""Small, randomly initialized decoder-only Transformer baseline.

This is an owned trainable model component, not a pretrained-model adapter.
The byte tokenizer is deliberately language-agnostic: UTF-8 bytes are tokens.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
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
