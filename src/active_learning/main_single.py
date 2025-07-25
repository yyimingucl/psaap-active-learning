import logging

from src.active_learning.batch_active_learning_experiment_runner import ALExperimentRunner
from src.active_learning.util_classes import BiFidelityDataset, ALExperimentConfig
from src.models.bfgpc import BFGPC_ELBO
from src.batch_al_strategies.mutual_information_strategy_bmfal_n_weighted import MutualInformationBMFALNweightedStrategy
from src.batch_al_strategies.mutual_information_strategy_bernoulli_p import MutualInformationBernoulliPStrategy
from src.batch_al_strategies.mutual_information_strategy_bernoulli_p_with_repeats import MutualInformationBernoulliPRepeatsStrategy
from src.problems.toy_example import create_smooth_change_linear

logging.basicConfig(level=logging.INFO)

linear_low_f1, linear_high_f1, p_LF_toy, p_HF_toy = create_smooth_change_linear()


def sampling_function_L(X_normalized):  # Expects N x 2 normalized input
    Y_linear_low_grid, probs_linear_low_grid = linear_low_f1(X_normalized, reps=1)
    Y_linear_high_grid = Y_linear_low_grid.mean(axis=0)
    return Y_linear_high_grid


def sampling_function_H(X_normalized):
    Y_linear_high_grid, probs_linear_high_grid = linear_high_f1(X_normalized, reps=1)
    Y_linear_high_grid = Y_linear_high_grid.mean(axis=0)
    return Y_linear_high_grid


def main():
    dataset = BiFidelityDataset(sample_LF=sampling_function_L, sample_HF=sampling_function_H,
                                true_p_LF=p_LF_toy, true_p_HF=p_HF_toy,
                                name='ToyLinear', c_LF=0.1, c_HF=1.0)

    # strategy = RandomStrategy(model=model, dataset=dataset, seed=seed, gamma=0.9)
    # strategy = MutualInformationBMFALStrategy(model=model, dataset=dataset, seed=seed, N_MC=100, plot_all_scores=True)
    # strategy = MutualInformationGridStrategy(model=model, dataset=dataset, seed=seed, plot_all_scores=True, max_pool_subset=50)
    # strategy = MutualInformationGridStrategyObservables(model, dataset, seed=seed, plot_all_scores=True, N_y_samples=100)
    # strategy = MaxUncertaintyStrategy(model=model, dataset=dataset, beta=0.5, gamma=0.5, plot_all_scores=True)
    # strategy = MutualInformationBMFALNweightedStrategy(model=model, dataset=dataset, seed=seed, N_test_points=100, max_pool_subset=50, plot_all_scores=True)
    # strategy = MutualInformationBernoulliPStrategy(dataset=dataset, N_test_points=100, max_pool_subset=200, plot_all_scores=True)
    strategy = MutualInformationBernoulliPRepeatsStrategy(dataset=dataset, N_test_points=100, max_pool_subset=50, plot_all_scores=False, repeat_jitter=0.01, Nmax=10)

    base_config = ALExperimentConfig(
        N_L_init=500,
        N_H_init=250,
        cost_constraints=[100] * 5,
        N_cand_LF=2000,
        N_cand_HF=1000,
        train_epochs=100,
        train_lr=0.1,
        N_reps=1,
        model_args={'n_inducing_pts': 256},

    )

    experiment = ALExperimentRunner(dataset, strategy, base_config)
    experiment.run_experiment()


if __name__ == '__main__':
    main()