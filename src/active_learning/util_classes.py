import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional

import gpytorch
import torch
import numpy as np


class BiFidelityModel(ABC):
    @abstractmethod
    def forward(self, X):  # Return predictive probability P(y_H=1 | x_predict)
        pass

    @abstractmethod
    def evaluate_elpp(self, X_HF_test, Y_HF_test):
        pass

    @abstractmethod
    def train_model(self, X_LF, Y_LF, X_HF, Y_HF, lr, n_epochs):
        pass

    @abstractmethod
    def predict_f_H(self, x_predict):
        pass

    @abstractmethod
    def predict_multi_fidelity_latent_joint(self, X_L: torch.tensor, X_H: torch.tensor, X_prime: torch.tensor):
        pass

    @abstractmethod
    def predict_prob_mean(self, x_predict):
        pass

    @abstractmethod
    def predict_prob_var(self, x_predict):
        pass


@dataclass
class BiFidelityDataset():
    """Data needed to define a bi-fidelity toy dataset (sampling functions and their costs)"""
    sample_LF: Callable[[np.ndarray], np.ndarray]
    sample_HF: Callable[[np.ndarray], np.ndarray]
    true_p_LF: Optional[Callable[[np.ndarray], np.ndarray]]
    true_p_HF: Optional[Callable[[np.ndarray], np.ndarray]]
    name: str
    c_LF: float
    c_HF: float


@dataclass
class ALExperimentConfig:
    """Settings for initialising a bi fidelity batch active learning experiment"""
    N_L_init: int
    N_H_init: int
    cost_constraints: list[float]
    N_cand_LF: int
    N_cand_HF: int
    domain_bounds: list[tuple[float, float]] = field(default_factory=lambda: [(0, 1), (0, 1)])
    N_test: int = 1000
    train_lr: float = 0.01
    train_epochs: int = 500
    random_seed: Optional[int] = None
    N_reps: int = 5

    def __post_init__(self):
        if not self.cost_constraints:
            raise ValueError("cost_constraints list cannot be empty.")
        if any(self.cost_constraints[i] > self.cost_constraints[i + 1] for i in range(len(self.cost_constraints) - 1)):
            logging.warning(
                "cost_constraints are not monotonically increasing. This might lead to unexpected behavior.")
