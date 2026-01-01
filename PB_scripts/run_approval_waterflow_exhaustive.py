"""
Run Method of Equal Shares (waterflow) with exhaustive budget increases (approval utilities).

Continues until all projects are selected.
"""

from pabutools.election import parse_pabulib, Cardinality_Sat
import pandas as pd
import os
from pathlib import Path
import sys

from core.mes import mes_with_budget_increase_exhaustion, create_mes_results_df
from core.cli import setup_results_dir, save_results


def run_mes_exhaustive(pabulib_file: str, budget: int = 0) -> pd.DataFrame:
    """
    Run MES with exhaustive budget increases (approval utilities).
    
    Continues until all projects are selected (does not stop on overspend).
    """
    instance, profile = parse_pabulib(pabulib_file)
    
    if budget > 0:
        initial_budget = int(budget)
        instance.budget_limit = int(budget)
    else:
        initial_budget = int(instance.budget_limit)

    instance.budget_limit = int(instance.budget_limit)

    result, efficiency, increase_counter = mes_with_budget_increase_exhaustion(
        instance, profile,
        sat_class=Cardinality_Sat,
        stop_on_overspend=False,  # Continue until all projects selected
    )

    return create_mes_results_df(
        result=result,
        efficiency=efficiency,
        budget_increase_count=increase_counter,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_approval_waterflow_exhaustive.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    
    input_path = Path(file_path).resolve()
    results_dir = setup_results_dir("waterflow_equal_shares/approval/exhaustive")
    
    try:
        output_filename = f"{input_path.stem}.csv"
        
        print(f"Processing file: {input_path}")
        print(f"Results will be saved to: {results_dir / output_filename}")
        
        output_df = run_mes_exhaustive(str(input_path))
        save_results(output_df, results_dir, output_filename)
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        sys.exit(1)
