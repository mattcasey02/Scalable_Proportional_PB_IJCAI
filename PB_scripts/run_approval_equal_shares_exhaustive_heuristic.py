"""
Run Exact Equal Shares with completion (approval utilities, exhaustive, heuristic).

Uses ADD-OPT-SKIP and continues until all projects are selected.
"""

from pabutools.election import parse_pabulib
import pandas as pd
import copy
from pathlib import Path
import os
import sys

from core.utils import profile_preprocessing
from core.ees import exact_method_of_equal_shares_approval
from core.add_opt import add_opt_approval_heuristic
from core.cli import setup_results_dir, save_results


def exact_method_of_equal_shares_with_completion_approval_exhaustive_heuristic(pabulib_file: str, budget: int = 0):
    """
    Run EES with budget completion using ADD-OPT-SKIP heuristic (exhaustive).
    
    Continues until all projects are selected, tracking monotonicity violations.
    """
    instance, profile = parse_pabulib(pabulib_file)
    profile = profile_preprocessing(profile)
    number_total_projects = len(instance)

    initial_budget = instance.budget_limit
    if budget > 0:
        instance.budget_limit = budget

    selected_projects, payments, shares, total_cost = exact_method_of_equal_shares_approval(
        instance, profile
    )
    
    most_efficient_project_set = copy.deepcopy(selected_projects)
    budget_increase_count = 0
    budget_increase_list = []
    efficiency_tracker = total_cost / initial_budget
    monotonic_violation = 0
    exceeded_non_exhaustive_case = 0

    prev_total_cost = total_cost
    prev_project_set = copy.deepcopy(selected_projects)
    final_efficiency = 0

    while True:
        min_budget_increase = add_opt_approval_heuristic(
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
            exceeded_non_exhaustive_case = 1
        else:
            budget_increase_list.append(min_budget_increase)
            prev_project_set = copy.deepcopy(selected_projects)
            prev_total_cost = total_cost
            
            efficiency_candidate = total_cost / initial_budget
            if efficiency_candidate > efficiency_tracker:
                if exceeded_non_exhaustive_case:
                    monotonic_violation = 1
                efficiency_tracker = efficiency_candidate
                most_efficient_project_set = copy.deepcopy(selected_projects)

        if len(selected_projects) == number_total_projects:
            final_efficiency = prev_total_cost / initial_budget
            break

    data = {
        'most_efficient_project_set': [most_efficient_project_set],
        'highest_efficiency_attained': [efficiency_tracker],
        'final_project_set': [prev_project_set],
        'final_efficiency': [final_efficiency],
        'budget_increase_count': [budget_increase_count],
        'len_budget_increase_list': [len(budget_increase_list)],
        'max_budget_increase': [max(budget_increase_list)] if budget_increase_list else [0],
        'min_budget_increase': [min(budget_increase_list)] if budget_increase_list else [0],
        'avg_budget_increase': [sum(budget_increase_list)/len(budget_increase_list)] if budget_increase_list else [0],
        'monotonic_violation': [monotonic_violation]
    }

    return pd.DataFrame(data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_approval_equal_shares_exhaustive_heuristic.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    
    input_path = Path(file_path).resolve()
    results_dir = setup_results_dir("exact_equal_shares/approval/exhaustive_heuristic")
    
    try:
        output_filename = f"{input_path.stem}.csv"
        output_path = results_dir / output_filename
        
        print(f"Processing file: {input_path}")
        print(f"Results will be saved to: {output_path}")
        
        output_df = exact_method_of_equal_shares_with_completion_approval_exhaustive_heuristic(str(input_path))
        save_results(output_df, results_dir, output_filename)
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        sys.exit(1)
