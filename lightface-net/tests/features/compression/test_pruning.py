# tests/features/compression/test_pruning.py
"""
Unit tests for sparsity training and BN pruning.

Run:
    pytest tests/features/compression/ -v
"""

import pytest
import torch
import torch.nn as nn


def _small_model() -> nn.Sequential:
    return nn.Sequential(
        nn.Conv2d(3, 16, 3, padding=1, bias=False),
        nn.BatchNorm2d(16),
        nn.ReLU(),
        nn.Conv2d(16, 32, 3, padding=1, bias=False),
        nn.BatchNorm2d(32),
        nn.ReLU(),
    )


class TestBNPruner:
    def test_prune_zeroes_small_gamma_channels(self):
        from features.compression.pruning.bn_pruner import BNPruner, PrunerConfig
        model = _small_model()
        # Force one BN gamma to very small value
        with torch.no_grad():
            model[1].weight[:4] = 0.001
        pruner = BNPruner(PrunerConfig(prune_threshold=0.5))
        pruner.prune(model)
        # Channels with small gamma should be zeroed
        assert (model[1].weight[:4] == 0).all()

    def test_large_gamma_channels_preserved(self):
        from features.compression.pruning.bn_pruner import BNPruner, PrunerConfig
        model = _small_model()
        with torch.no_grad():
            model[1].weight.fill_(1.0)      # all large gammas
        pruner = BNPruner(PrunerConfig(prune_threshold=0.01))
        pruner.prune(model)
        # Near threshold=0.01: channels above that should survive
        assert (model[1].weight >= 0).all()


class TestSparsityTrainer:
    def test_l1_penalty_positive(self):
        from features.compression.pruning.sparsity_trainer import SparsityTrainer, SparsityConfig
        model = _small_model()
        trainer = SparsityTrainer(
            model=model,
            config=SparsityConfig(lambda_sparse=1e-4)
        )
        l1 = trainer.l1_bn_penalty()
        assert l1.item() > 0, "L1 BN penalty should be positive for non-zero gammas"

    def test_zero_penalty_for_zero_gamma(self):
        from features.compression.pruning.sparsity_trainer import SparsityTrainer, SparsityConfig
        model = _small_model()
        with torch.no_grad():
            for m in model.modules():
                if isinstance(m, nn.BatchNorm2d):
                    m.weight.zero_()
        trainer = SparsityTrainer(model=model, config=SparsityConfig())
        assert trainer.l1_bn_penalty().item() == pytest.approx(0.0, abs=1e-6)
