"""
Exact Equal Shares (EES) implementations.

This module contains the core EES algorithm that can be parameterized
by different utility functions (cardinal/approval or cost/uniform).
"""

from typing import Callable, Dict, List, Tuple, Any
from collections import OrderedDict
from functools import partial

from .utils import (
    profile_preprocessing,
    cardinal_utility,
    cost_utility,
    filter_sd,
    calculate_bang_per_buck,
    get_project_support,
    initialize_payments,
    initialize_shares,
)


def exact_method_of_equal_shares(
    instance,
    profile,
    utility_function: Callable = cardinal_utility,
    budget: float = 0
) -> Tuple[OrderedDict, Dict, Dict, float]:
    """
    Run the Exact Method of Equal Shares algorithm.
    
    This is the core EES implementation that selects projects by highest
    bang-per-buck, where only voters who can afford equal shares contribute.
    
    Args:
        instance: Pabulib instance with budget_limit and project_meta
        profile: Voter profile (will be preprocessed if needed)
        utility_function: Function mapping project -> utility (default: cardinal)
        budget: Optional budget override (uses instance.budget_limit if 0)
        
    Returns:
        Tuple of:
        - funded_projects: OrderedDict mapping project -> bang_per_buck (in selection order)
        - X_payments: Dict mapping (voter_name, project) -> payment amount
        - shares: Dict mapping voter_name -> remaining budget
        - total_cost: Total cost of selected projects
    """
    if budget > 0:
        instance.budget_limit = budget

    budget = instance.budget_limit
    projects = instance.project_meta

    # Preprocess profile
    profile = profile_preprocessing(profile)
    num_voters = len(profile)
    
    # Initialize data structures
    X_payments = initialize_payments(profile, projects)
    shares = initialize_shares(profile, budget)
    funded_projects = OrderedDict()
    total_cost = 0
    project_support = get_project_support(projects, profile)

    while True:
        best_project = None
        max_bang_per_buck = 0
        best_index = 0
        best_supp_shares = None

        # Sort all voter shares once per iteration
        supp_shares_base = sorted(shares.items(), key=lambda item: item[1])

        for project in projects:
            if project in funded_projects:
                continue

            if not project_support[project]:
                continue

            # Filter to only supporters of this project
            supp_shares = filter_sd(supp_shares_base, project_support[project])

            number_paying_voters = len(supp_shares)
            for i in range(len(supp_shares)):
                max_contribution = project.cost / number_paying_voters
                
                if max_contribution <= supp_shares[i][1]:
                    bang_per_buck = calculate_bang_per_buck(
                        project, number_paying_voters, utility_function
                    )
                    
                    if bang_per_buck > max_bang_per_buck:
                        max_bang_per_buck = bang_per_buck
                        best_project = (project, bang_per_buck)
                        best_index = i
                        best_supp_shares = supp_shares
                    elif bang_per_buck == max_bang_per_buck and best_project is not None:
                        # Tie-breaking: larger project name wins
                        if project.name > best_project[0].name:
                            best_project = (project, bang_per_buck)
                            best_index = i
                            best_supp_shares = supp_shares
                    break
                number_paying_voters -= 1

        if best_project is None:
            break

        # Fund the project
        contribution = best_project[0].cost / (len(best_supp_shares) - best_index)

        for voter_name, _ in best_supp_shares[best_index:]:
            shares[voter_name] -= contribution
            X_payments[(voter_name, best_project[0])] = contribution

        funded_projects[best_project[0]] = best_project[1]
        total_cost += best_project[0].cost

    return funded_projects, X_payments, shares, total_cost


# Convenience wrappers for specific utility functions

def exact_method_of_equal_shares_approval(
    instance,
    profile,
    budget: float = 0
) -> Tuple[List, Dict, Dict, float]:
    """
    EES with cardinal/approval utility (u(p) = 1).
    
    Returns:
        Tuple of (selected_projects_list, payments, shares, total_cost)
    """
    funded_projects, payments, shares, total_cost = exact_method_of_equal_shares(
        instance, profile, utility_function=cardinal_utility, budget=budget
    )
    return list(funded_projects.keys()), payments, shares, total_cost


def exact_method_of_equal_shares_cost(
    instance,
    profile,
    budget: float = 0
) -> Tuple[OrderedDict, Dict, Dict, float]:
    """
    EES with cost/uniform utility (u(p) = cost(p)).
    
    Returns:
        Tuple of (funded_projects_with_bpb, payments, shares, total_cost)
    """
    return exact_method_of_equal_shares(
        instance, profile, utility_function=cost_utility, budget=budget
    )


# Alias for backwards compatibility
exact_method_of_equal_shares_uniform = exact_method_of_equal_shares_cost

