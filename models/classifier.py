"""Edema classifier head and full model."""
import torch.nn as nn
from .encoder import Encoder

class EdemaHead(nn.Module):
    """Linear classifier operating on the CLS token."""

    def __init__(self, emb_size: int = 256, classes: int = 2):
        super().__init__()
        self.lin = nn.Linear(emb_size, classes)

    def forward(self, x):
        return self.lin(x[:, 0])

class M3T_Edema(nn.Module):
    """Encoder plus classification head for edema prediction."""

    def __init__(self, cfg):
        super().__init__()
        self.encoder = Encoder(cfg)
        self.head = EdemaHead(cfg["emb_size"], 2)

    def forward(self, x):
        cls, _ = self.encoder(x)
        return self.head(cls)
