# Scalable Proportional Participatory Budgeting

Implementation of Exact Equal Shares (EES) and completion heuristics for proportional participatory budgeting.

Based on the paper:
> **Streamlining Equal Shares**  
> Sonja Kraiczy, Isaac Robinson, and Edith Elkind  
> arXiv:2502.11797

## Installation

```bash
# Clone the repository
git clone https://github.com/robinsonaisaac/Scalable_Proportional_PB.git
cd Scalable_Proportional_PB

# Install in development mode
pip install -e ".[dev]"
```

## Quick Start

### Command Line Interface

```bash
# Run EES with approval (cardinal) utility
python -m scalable_proportional_pb run --input data.pb --utility approval

# Run EES with cost utility
python -m scalable_proportional_pb run --input data.pb --utility cost

# Run with ADD-OPT-SKIP completion heuristic
python -m scalable_proportional_pb run --input data.pb --completion add-opt-skip

# Run with ADD-ONE completion (exhaustive)
python -m scalable_proportional_pb run --input data.pb --completion add-one --exhaustive
```

### Python API

```python
from scalable_proportional_pb import parse_pabulib_file, ees_with_outcome
from scalable_proportional_pb.ees import cardinal_utility, cost_utility
from scalable_proportional_pb.completion import add_opt_skip_completion

# Parse a Pabulib file
election = parse_pabulib_file("data.pb")

# Run basic EES
outcome = ees_with_outcome(election, cardinal_utility)
print(f"Selected: {outcome.selected}")
print(f"Efficiency: {float(outcome.spending_efficiency(election.budget)):.2%}")

# Run with ADD-OPT-SKIP completion
outcome = add_opt_skip_completion(election, cardinal_utility, is_cardinal=True)
print(f"Selected: {outcome.selected}")
```

## Algorithms Implemented

| Algorithm | Description | Time Complexity |
|-----------|-------------|-----------------|
| EES (Algorithm 1) | Exact Equal Shares | O(m²n) |
| GREEDYPROJECTCHANGE (Algorithm 2) | For cardinal utilities | O(n) |
| ADD-OPT (Algorithm 3) | For cardinal utilities | O(mn) |
| GREEDYPROJECTCHANGE (Algorithm 4) | For uniform utilities | O(m + n) |
| ADD-OPT (Algorithm 5) | For uniform utilities | O(m²n) |

Where m = number of projects, n = number of voters.

### Completion Heuristics

- **ADD-ONE**: Increase budget by n per iteration until overspending
- **ADD-OPT**: Use optimal budget increment from ADD-OPT algorithm
- **ADD-OPT-SKIP**: Like ADD-OPT but only considers unselected projects (recommended)

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
Scalable_Proportional_PB/
├── src/scalable_proportional_pb/   # Core library
│   ├── __init__.py
│   ├── __main__.py                 # CLI entry point
│   ├── types.py                    # Data types (Election, EESOutcome)
│   ├── ees.py                      # EES algorithm (Algorithm 1)
│   ├── gpc_cardinal.py             # GREEDYPROJECTCHANGE for cardinal (Algorithm 2)
│   ├── add_opt_cardinal.py         # ADD-OPT for cardinal (Algorithm 3)
│   ├── gpc_uniform.py              # GREEDYPROJECTCHANGE for uniform (Algorithm 4)
│   ├── add_opt_uniform.py          # ADD-OPT for uniform (Algorithm 5)
│   ├── completion.py               # Completion heuristics
│   └── pabulib_io.py               # Pabulib file parsing
├── tests/                          # Unit tests
├── PB_scripts/                     # Legacy experiment scripts
├── results/                        # Experiment results (CSV)
├── pyproject.toml                  # Package configuration
└── README.md
```

## Input Format

Accepts [Pabulib](http://pabulib.org/) `.pb` files. Example:

```
META
key;value
budget;100000
num_projects;10
num_votes;500
vote_type;approval
PROJECTS
project_id;cost;name
p1;10000;Street Lights
p2;25000;Park Renovation
...
VOTES
voter_id;vote
1;p1,p2,p5
2;p2,p3
...
```

## Citation

If you use this code, please cite:

```bibtex
@article{kraiczy2025streamlining,
  title={Streamlining Equal Shares},
  author={Kraiczy, Sonja and Robinson, Isaac and Elkind, Edith},
  journal={arXiv preprint arXiv:2502.11797},
  year={2025}
}
```

## License

MIT License

