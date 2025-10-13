# ai_filter.py
import torch
import torch.nn as nn

class RadarDenoiser(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(100, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 100)
        )

    def forward(self, x):
        return self.net(x)
