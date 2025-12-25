"""
Algorithm 4: GREEDYPROJECTCHANGE for Uniform Utilities

From "Streamlining Equal Shares" (arXiv:2502.11797), Section 5.1.

For uniform utilities, voters may need to withdraw support from multiple
projects to fund a new one. This algorithm computes the minimum per-voter
budget increase d such that project p certifies instability.

This algorithm runs in O(m + n) time.
"""

from fractions import Fraction
from typing import Callable, Dict, List, Optional, Set, Tuple

from .types import Election, EESOutcome, Project


def greedy_project_change_uniform(
    election: Election,
    outcome: EESOutcome,
    project_id: str,
    utility: Callable[[Project], Fraction],
    L_lists: List[List[Tuple[int, Fraction]]],
) -> Optional[Fraction]:
    """
    Algorithm 4: GREEDYPROJECTCHANGE for uniform utilities.
    
    Computes the minimum d > 0 such that project p certifies instability
    of (W, X) for E(b + n*d) under uniform utility function u.
    
    Args:
        election: The election E(b)
        outcome: A stable EES outcome (W, X) for E(b)
        project_id: The project p to consider
        utility: The uniform utility function u(p)
        L_lists: Precomputed L_1, ..., L_{w+1} lists (see compute_L_lists)
        
    Returns:
        The minimum d value, or None if p cannot certify instability (infinity).
    """
    project = election.projects[project_id]
    cost = project.cost
    
    # N_p: voters who approve p
    N_p = election.project_supporters(project_id)
    
    # N_p(X): voters already paying for p in outcome
    N_p_X = outcome.project_payers(project_id)
    
    # O_p(X) = N_p \ N_p(X): supporters not currently paying
    O_p_X = N_p - N_p_X
    
    if not O_p_X and not N_p_X:
        return None  # Infinity
    
    if not O_p_X:
        return None  # Infinity
    
    # Get selection order with BpB values
    selection_order = outcome.selection_order
    w = len(selection_order)
    
    # Compute BpB for project p if it were to be funded by t voters
    def bpb_for_t(t: int) -> Fraction:
        if t == 0:
            return Fraction(0)
        return utility(project) * t / cost
    
    # Filter L lists to only include voters in O_p(X)
    L_Op: List[List[Tuple[int, Fraction]]] = []
    for L_i in L_lists:
        filtered = [(v, val) for v, val in L_i if v in O_p_X]
        filtered.sort(key=lambda x: x[1])
        L_Op.append(filtered)
    
    d: Optional[Fraction] = None  # None means infinity
    ell = 0  # number of voters from O_p(X) contributing
    i = w  # pointer into selection_order (1-indexed in paper, but we use 0-indexed)
    
    N_p_X_count = len(N_p_X)
    
    # Main loop: iterate through possible values of t (total contributors)
    while i >= 0 and ell < len(O_p_X):
        remaining_from_Op = len(O_p_X) - ell
        t = N_p_X_count + remaining_from_Op
        
        if t == 0:
            break
            
        PvP = cost / t  # per-voter price
        current_bpb = bpb_for_t(t)
        
        # Decrease i while current_bpb is worse than project at position i-1
        while i > 0:
            prev_id, prev_bpb = selection_order[i - 1]
            if current_bpb < prev_bpb or (current_bpb == prev_bpb and project_id < prev_id):
                i -= 1
            else:
                break
        
        # Check if we can get a voter to contribute at this price
        if i < len(L_Op) and ell < len(L_Op[i]):
            v, L_val = L_Op[i][ell]
            
            if L_val >= PvP:
                # This voter can afford it
                pass
            else:
                # Need increase of PvP - L_val
                required = PvP - L_val
                if required > 0:
                    if d is None or required < d:
                        d = required
        
        ell += 1
    
    return d


def compute_L_lists(
    election: Election,
    outcome: EESOutcome,
    utility: Callable[[Project], Fraction],
) -> List[List[Tuple[int, Fraction]]]:
    """
    Compute the L_1, ..., L_{w+1} lists used by Algorithm 4.
    
    L_{w+1}[v] = r_v (leftover budget)
    L_i[v] = L_{i+1}[v] + x_{v,p_i} for i <= w
    
    This represents the total budget voter v has contributed to projects
    p_i, ..., p_w plus their leftover budget.
    
    Args:
        election: The election
        outcome: The EES outcome with selection_order
        utility: The utility function
        
    Returns:
        List of L lists, where L[i] is the i-th list (0-indexed, so L[0] = L_1)
        Each L[i] is a list of (voter_id, value) sorted by value.
    """
    selection_order = outcome.selection_order
    w = len(selection_order)
    voters = election.voters
    
    # L_{w+1} = leftover budgets
    L_w_plus_1 = [(v, outcome.leftover_budgets[v]) for v in voters]
    L_w_plus_1.sort(key=lambda x: x[1])
    
    # Build L lists from L_{w+1} back to L_1
    L_lists: List[List[Tuple[int, Fraction]]] = [[] for _ in range(w + 1)]
    L_lists[w] = L_w_plus_1
    
    # Current values for each voter
    current_vals = {v: outcome.leftover_budgets[v] for v in voters}
    
    # Build L_w, L_{w-1}, ..., L_1
    for k in range(w - 1, -1, -1):
        proj_id, _ = selection_order[k]
        # Add payment for project k to each voter's value
        for v in voters:
            current_vals[v] += outcome.payment(v, proj_id)
        
        L_k = [(v, current_vals[v]) for v in voters]
        L_k.sort(key=lambda x: x[1])
        L_lists[k] = L_k
    
    return L_lists
