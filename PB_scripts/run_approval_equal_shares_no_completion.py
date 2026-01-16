"""
Run Exact Equal Shares without completion (approval utilities).

Single EES run without any budget increases.
"""

from pabutools.election import parse_pabulib
import pandas as pd
import copy
from pathlib import Path
import os
import sys

from core.utils import profile_preprocessing
from core.ees import exact_method_of_equal_shares_approval, create_ees_results_df
from core.add_opt import add_opt_approval
from core.cli import setup_results_dir, save_results


def exact_method_of_equal_shares_with_completion_approval(pabulib_file: str, budget: int = 0):
    """
    Run EES without budget completion.
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
    
    efficiency = total_cost / initial_budget


    return create_ees_results_df(
        result = selected_projects,
        efficiency = efficiency,
        budget_increase_count=0
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_approval_equal_shares_no_completion.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    
    input_path = Path(file_path).resolve()
    results_dir = setup_results_dir("exact_equal_shares/approval/no_completion")
    
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
