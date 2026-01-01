"""
Run Method of Equal Shares (waterflow) without completion (cost utilities).

Single MES run without any budget increases.
"""

from pabutools.election import parse_pabulib, Cost_Sat
from pabutools.rules import method_of_equal_shares
import pandas as pd
import os
from pathlib import Path
import sys

from core.mes import create_mes_results_df
from core.cli import setup_results_dir, save_results


def run_mes_no_completion(pabulib_file: str, budget: int = 0) -> pd.DataFrame:
    """
    Run MES without completion (cost utilities).
    
    Single run without any budget increases.
    """
    instance, profile = parse_pabulib(pabulib_file)
    
    if budget > 0:
        initial_budget = int(budget)
        instance.budget_limit = int(budget)
    else:
        initial_budget = int(instance.budget_limit)

    instance.budget_limit = int(instance.budget_limit)

    result = method_of_equal_shares(
        instance=instance,
        profile=profile,
        sat_class=Cost_Sat,
    )
    
    total_cost = sum(p.cost for p in result)
    efficiency = total_cost / initial_budget if initial_budget > 0 else 0.0

    return create_mes_results_df(
        result=result,
        efficiency=efficiency,
        budget_increase_count=0,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_cost_waterflow_no_completion.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    
    input_path = Path(file_path).resolve()
    results_dir = setup_results_dir("waterflow_equal_shares/cost/no_completion")
    
    try:
        output_filename = f"{input_path.stem}.csv"
        
        print(f"Processing file: {input_path}")
        print(f"Results will be saved to: {results_dir / output_filename}")
        
        output_df = run_mes_no_completion(str(input_path))
        save_results(output_df, results_dir, output_filename)
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        sys.exit(1)
