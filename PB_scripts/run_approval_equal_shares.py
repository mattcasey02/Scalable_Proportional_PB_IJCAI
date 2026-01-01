"""
Run Exact Equal Shares with completion (approval utilities, non-exhaustive).

Uses ADD-OPT to find minimum budget increases until budget is exhausted.
"""

from pabutools.election import parse_pabulib
import pandas as pd
import copy
from pathlib import Path
import os
import sys

from core.utils import profile_preprocessing
from core.ees import exact_method_of_equal_shares_approval
from core.add_opt import add_opt_approval
from core.cli import setup_results_dir, save_results


def exact_method_of_equal_shares_with_completion_approval(pabulib_file: str, budget: int = 0):
    """
    Run EES with budget completion using ADD-OPT (non-exhaustive, non-heuristic).
    
    Stops when total cost exceeds initial budget.
    """
    instance, profile = parse_pabulib(pabulib_file)
    profile = profile_preprocessing(profile)

    initial_budget = instance.budget_limit
    if budget > 0:
        instance.budget_limit = budget

    # Initial EES run
    selected_projects, payments, shares, total_cost = exact_method_of_equal_shares_approval(
        instance, profile
    )
    
    most_efficient_project_set = copy.deepcopy(selected_projects)
    budget_increase_count = 0
    budget_increase_list = []
    efficiency_tracker = total_cost / initial_budget

    prev_total_cost = total_cost
    prev_project_set = copy.deepcopy(selected_projects)

    while True:
        min_budget_increase = add_opt_approval(
            instance, profile, selected_projects, payments, shares
        )

        if min_budget_increase == float("inf"):
            break

        budget_increase_count += 1
        instance.budget_limit += min_budget_increase * len(profile)

        selected_projects, payments, shares, total_cost = exact_method_of_equal_shares_approval(
            instance, profile
        )

        if total_cost > initial_budget:
            break
        
        budget_increase_list.append(min_budget_increase)
        prev_project_set = copy.deepcopy(selected_projects)
        prev_total_cost = total_cost
        
        efficiency_candidate = total_cost / initial_budget
        if efficiency_candidate > efficiency_tracker:
            efficiency_tracker = efficiency_candidate
            most_efficient_project_set = copy.deepcopy(selected_projects)

    final_efficiency = prev_total_cost / initial_budget if prev_total_cost > 0 else 0

    data = {
        'most_efficient_project_set': [most_efficient_project_set],
        'highest_efficiency_attained': [efficiency_tracker],
        'final_project_set': [prev_project_set],
        'final_efficiency': [final_efficiency],
        'budget_increase_count': [budget_increase_count],
        'len_budget_increase_list': [len(budget_increase_list)],
        'max_budget_increase': [max(budget_increase_list)] if budget_increase_list else [0],
        'min_budget_increase': [min(budget_increase_list)] if budget_increase_list else [0],
        'avg_budget_increase': [sum(budget_increase_list)/len(budget_increase_list)] if budget_increase_list else [0]
    }

    return pd.DataFrame(data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_approval_equal_shares.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    
    input_path = Path(file_path).resolve()
    results_dir = setup_results_dir("exact_equal_shares/approval/non_exhaustive")
    
    try:
        output_filename = f"{input_path.stem}.csv"
        output_path = results_dir / output_filename
        
        print(f"Processing file: {input_path}")
        print(f"Results will be saved to: {output_path}")
        
        output_df = exact_method_of_equal_shares_with_completion_approval(str(input_path))
        save_results(output_df, results_dir, output_filename)
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        sys.exit(1)
