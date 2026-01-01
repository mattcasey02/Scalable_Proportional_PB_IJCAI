"""
Core modules for Participatory Budgeting experiments.

This package contains shared implementations extracted from the various
runner scripts to reduce code duplication.

Modules:
- utils: Common utility functions (profile preprocessing, utility functions)
- ees: Exact Equal Shares implementations
- add_opt: ADD-OPT and Greedy Project Change implementations
- cli: Command-line interface helpers and results handling
"""

from .utils import (
    profile_preprocessing,
    cardinal_utility,
    cost_utility,
    filter_sd,
    calculate_bang_per_buck,
)

from .ees import (
    exact_method_of_equal_shares,
    exact_method_of_equal_shares_approval,
    exact_method_of_equal_shares_cost,
)

from .add_opt import (
    greedy_project_change_approvals,
    greedy_project_change_uniform,
    add_opt_approval,
    add_opt_approval_heuristic,
    add_opt_cost,
    add_opt_cost_heuristic,
)

from .cli import (
    run_experiment,
    save_results,
    setup_results_dir,
)

from .mes import (
    run_mes_approval,
    run_mes_cost,
    calculate_efficiency,
    mes_with_budget_increase_exhaustion,
    create_mes_results_df,
)

__all__ = [
    # utils
    "profile_preprocessing",
    "cardinal_utility",
    "cost_utility",
    "filter_sd",
    "calculate_bang_per_buck",
    # ees
    "exact_method_of_equal_shares",
    "exact_method_of_equal_shares_approval",
    "exact_method_of_equal_shares_cost",
    # add_opt
    "greedy_project_change_approvals",
    "greedy_project_change_uniform",
    "add_opt_approval",
    "add_opt_approval_heuristic",
    "add_opt_cost",
    "add_opt_cost_heuristic",
    # cli
    "run_experiment",
    "save_results",
    "setup_results_dir",
    # mes
    "run_mes_approval",
    "run_mes_cost",
    "calculate_efficiency",
    "mes_with_budget_increase_exhaustion",
    "create_mes_results_df",
]

