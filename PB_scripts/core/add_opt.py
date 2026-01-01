"""
ADD-OPT and Greedy Project Change implementations.

This module contains the algorithms for computing the minimum budget increase
needed to change the EES outcome, for both cardinal (approval) and uniform (cost) utilities.
"""

from typing import Callable, Dict, List, Set, Tuple, Any
import copy

from .utils import profile_preprocessing, cost_utility, cardinal_utility


def greedy_project_change_approvals(
    instance,
    profile,
    selected_projects: List,
    payments: Dict,
    project
) -> float:
    """
    Compute the minimum budget increase for a project to certify instability (cardinal utilities).
    
    This implements Algorithm 2 from the paper for approval/cardinal utilities.
    
    Args:
        instance: Pabulib instance
        profile: Preprocessed voter profile
        selected_projects: Currently selected projects
        payments: Current payment allocations
        project: Project to consider for change
        
    Returns:
        Minimum budget increase d, or infinity if project cannot certify instability
    """
    num_voters = len(profile)
    project_cost = project.cost
    initial_budget = instance.budget_limit
    profile = profile_preprocessing(profile)

    # Identify supporters of the project
    supporters = [voter['name'] for voter in profile if project in voter['approved']]
    supporters_not_paying = [
        voter for voter in supporters 
        if payments.get((voter, project), 0) == 0
    ]

    if not supporters_not_paying:
        return float("inf")

    # Compute leftover budgets for supporters not paying
    leftover_budgets = {
        voter: ((initial_budget / num_voters)
                - sum(payments.get((voter, p), 0) for p in selected_projects))
        for voter in supporters_not_paying
    }

    # Compute max payment each supporter is making (project, payment)
    max_payments = {
        voter: max(
            ((p, payments.get((voter, p), 0)) for p in selected_projects),
            key=lambda x: x[1],
            default=(None, 0)
        )
        for voter in supporters_not_paying
    }

    # Sort supporters by leftover budgets and max payments
    sorted_leftovers = sorted(leftover_budgets.items(), key=lambda x: x[1])
    sorted_max_payments = sorted(max_payments.items(), key=lambda x: (x[1][1], x[1][0]))

    min_increase = float("inf")
    solvent: Set = set()  # Voters who would deviate from current projects
    liquid: Set = set(supporters_not_paying)  # Voters willing to allocate leftover budget
    
    i, j = 0, 0
    
    while liquid or solvent:
        if i >= len(sorted_leftovers):
            break

        # Calculate per-voter price
        total_voters = (
            len(liquid) + len(solvent) +
            len([voter for voter in supporters if payments.get((voter, project), 0) > 0])
        )
        
        if total_voters == 0:
            break
            
        pvp = project_cost / total_voters

        # Check if current max payment is less than pvp (deviant case)
        if j < len(sorted_max_payments):
            max_pay_amount = sorted_max_payments[j][1][1]
            max_pay_project = sorted_max_payments[j][1][0]
            
            if max_pay_amount < pvp or (max_pay_amount == pvp and max_pay_project is not None and max_pay_project.name > project.name):
                solvent.discard(sorted_max_payments[j][0])
                j += 1
                continue
            
            # Check if voter should move from liquid to solvent
            current_voter = sorted_leftovers[i][0]
            if current_voter in liquid:
                voter_max_pay = max_payments[current_voter][1]
                voter_max_proj = max_payments[current_voter][0]
                
                if voter_max_pay > pvp or (voter_max_pay == pvp and voter_max_proj is not None and voter_max_proj.name < project.name):
                    solvent.add(current_voter)
                    liquid.remove(current_voter)
                    i += 1
                    continue
                else:
                    # Calculate required budget increment
                    required_increase = pvp - sorted_leftovers[i][1]
                    min_increase = min(min_increase, required_increase)
                    liquid.remove(current_voter)
                    i += 1
                    continue
        
        # Handle case when j >= len(sorted_max_payments)
        current_voter = sorted_leftovers[i][0]
        if current_voter in liquid:
            voter_max_pay = max_payments[current_voter][1]
            voter_max_proj = max_payments[current_voter][0]
            
            if voter_max_pay > pvp or (voter_max_pay == pvp and voter_max_proj is not None and voter_max_proj.name < project.name):
                solvent.add(current_voter)
                liquid.remove(current_voter)
                i += 1
            else:
                required_increase = pvp - sorted_leftovers[i][1]
                min_increase = min(min_increase, required_increase)
                liquid.remove(current_voter)
                i += 1
        else:
            i += 1

    return min_increase


def greedy_project_change_uniform(
    instance,
    profile,
    selected_projects_with_bpb: List[Tuple],
    payments: Dict,
    project,
    L: List[List],
    utility_function: Callable = cost_utility
) -> float:
    """
    Compute the minimum budget increase for a project to certify instability (uniform utilities).
    
    This implements Algorithm 4 from the paper for uniform/cost utilities.
    
    Args:
        instance: Pabulib instance
        profile: Preprocessed voter profile
        selected_projects_with_bpb: List of (project, bpb) tuples in selection order
        payments: Current payment allocations
        project: Project to consider
        L: Pre-computed L lists for budget aggregation
        utility_function: Utility function (default: cost_utility)
        
    Returns:
        Minimum budget increase d, or infinity if project cannot certify instability
    """
    voter_list = profile
    d = float("inf")
    ell = 0
    i = len(selected_projects_with_bpb)
    N_p = sum(1 for voter in voter_list if project in voter['approved'])

    # Calculate O_p(X): supporters not currently paying
    O_p_X = [
        voter['name']
        for voter in voter_list
        if project in voter['approved'] and payments.get((voter['name'], project), 0) == 0
    ]

    while i > 0 and ell < len(O_p_X):
        remaining_buyers = N_p - ell
        if N_p == 0:
            PvP = float("inf")
        else:
            PvP = project.cost / (N_p - ell)

        # Check priority ordering
        while i > 0:
            prev_bpb = selected_projects_with_bpb[i - 1][1]
            prev_name = selected_projects_with_bpb[i - 1][0].name
            current_bpb = utility_function(project) / PvP if PvP > 0 else 0
            
            if current_bpb < prev_bpb or (current_bpb == prev_bpb and prev_name < project.name):
                i -= 1
            else:
                break

        if i > 0 and ell < len(L[i]):
            L_val = L[i][ell]
            d = min(d, PvP - L_val[1])
        
        ell += 1

    return d


def add_opt_approval(
    instance,
    profile,
    selected_projects: List,
    payments: Dict,
    shares: Dict
) -> float:
    """
    Compute minimum budget increase for outcome instability (cardinal utilities).
    
    This implements Algorithm 3 from the paper.
    
    Args:
        instance: Pabulib instance
        profile: Voter profile
        selected_projects: Currently selected projects
        payments: Payment allocations
        shares: Remaining voter budgets
        
    Returns:
        Minimum d > 0 such that outcome becomes unstable
    """
    profile = profile_preprocessing(profile)
    projects = instance.project_meta
    d = float("inf")

    for p in projects:
        gp = greedy_project_change_approvals(
            instance, profile, selected_projects, payments, p
        )
        if gp > 0:
            d = min(d, gp)

    return d


def add_opt_approval_heuristic(
    instance,
    profile,
    selected_projects: List,
    payments: Dict,
    shares: Dict
) -> float:
    """
    ADD-OPT heuristic: only consider unselected projects (cardinal utilities).
    
    This is the ADD-OPT-SKIP variant that skips already-selected projects.
    """
    profile = profile_preprocessing(profile)
    projects = instance.project_meta
    d = float("inf")

    for p in projects:
        if p in selected_projects:
            continue
        gp = greedy_project_change_approvals(
            instance, profile, selected_projects, payments, p
        )
        if gp > 0:
            d = min(d, gp)

    return d


def _compute_L_lists(
    profile: List,
    sorted_selected_with_bpb: List[Tuple],
    payments: Dict,
    shares: Dict
) -> List[List]:
    """
    Compute the L_1, ..., L_{w+1} lists for uniform utilities.
    
    L[i] contains (voter, cumulative_budget) pairs sorted by budget.
    """
    budget_list = [[v, shares[v['name']]] for v in profile]
    budget_list.sort(key=lambda x: x[1])
    L0 = copy.deepcopy(budget_list)

    L = [copy.deepcopy(L0)]
    
    for k in range(1, len(sorted_selected_with_bpb) + 1):
        L_curr = copy.deepcopy(L[-1])
        project = sorted_selected_with_bpb[k - 1][0]
        
        for i in range(len(L_curr)):
            voter_name = L_curr[i][0]['name']
            L_curr[i][1] += payments.get((voter_name, project), 0)
        
        L_curr.sort(key=lambda x: x[1])
        L.append(L_curr)

    return L


def _get_L_Op(L: List[List], project, payments: Dict) -> List[List]:
    """
    Filter L lists to only include supporters of project not paying for it.
    """
    new_list = []
    for project_list in L:
        new_proj_list = []
        for pair in project_list:
            if (project in pair[0]['approved'] and 
                payments.get((pair[0]['name'], project), 0) == 0):
                new_proj_list.append(pair)
        new_proj_list.sort(key=lambda x: x[1])
        new_list.append(new_proj_list)
    return new_list


def add_opt_cost(
    instance,
    profile,
    sorted_selected_with_bpb,
    payments: Dict,
    shares: Dict
) -> float:
    """
    Compute minimum budget increase for outcome instability (uniform/cost utilities).
    
    This implements Algorithm 5 from the paper.
    """
    profile = profile_preprocessing(profile)
    
    # Handle both dict and list inputs
    if isinstance(sorted_selected_with_bpb, dict):
        sorted_selected_with_bpb = list(sorted_selected_with_bpb.items())
    
    projects = instance.project_meta
    d = float("inf")

    # Compute L lists
    L = _compute_L_lists(profile, sorted_selected_with_bpb, payments, shares)

    for p in projects:
        L_Op = _get_L_Op(L, p, payments)
        gp = greedy_project_change_uniform(
            instance, profile, sorted_selected_with_bpb, payments, p, L_Op, cost_utility
        )
        if gp > 0:
            d = min(d, gp)

    return d


def add_opt_cost_heuristic(
    instance,
    profile,
    sorted_selected_with_bpb,
    payments: Dict,
    shares: Dict
) -> float:
    """
    ADD-OPT heuristic: only consider unselected projects (uniform/cost utilities).
    """
    profile = profile_preprocessing(profile)
    
    if isinstance(sorted_selected_with_bpb, dict):
        sorted_selected_with_bpb = list(sorted_selected_with_bpb.items())
    
    selected_projects = {p for p, _ in sorted_selected_with_bpb}
    projects = instance.project_meta
    d = float("inf")

    L = _compute_L_lists(profile, sorted_selected_with_bpb, payments, shares)

    for p in projects:
        if p in selected_projects:
            continue
        L_Op = _get_L_Op(L, p, payments)
        gp = greedy_project_change_uniform(
            instance, profile, sorted_selected_with_bpb, payments, p, L_Op, cost_utility
        )
        if gp > 0:
            d = min(d, gp)

    return d

