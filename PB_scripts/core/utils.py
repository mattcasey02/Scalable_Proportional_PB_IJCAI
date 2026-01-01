"""
Common utility functions for Participatory Budgeting experiments.

This module contains shared helper functions used across multiple experiment scripts.
"""

from typing import List, Dict, Any, Callable
from collections import OrderedDict


def profile_preprocessing(profile) -> List[Dict[str, Any]]:
    """
    Preprocess a pabutools profile into a standardized format.
    
    Converts a profile (list of voter ballots) into a list of dictionaries
    with 'approved' (list of approved projects) and 'name' (voter ID) keys.
    
    Args:
        profile: A pabutools profile or already-processed list of dicts
        
    Returns:
        List of dicts with 'approved' and 'name' keys
    """
    # Check if the input is already processed
    if profile and isinstance(profile[0], dict) and "approved" in profile[0] and "name" in profile[0]:
        return profile

    to_return = []
    
    for i, voter in enumerate(profile):
        voter_id = i + 1  # Using 1-based indexing for IDs
        
        to_return.append({
            "approved": list(voter),  # Convert set to list
            "name": voter_id
        })
    
    return to_return


def cardinal_utility(project) -> int:
    """
    Cardinal utility function: u(p) = 1 for all projects.
    
    Used for approval-based voting where each approved project
    has equal utility.
    
    Args:
        project: A pabutools Project object
        
    Returns:
        1 (constant utility)
    """
    return 1


def cost_utility(project):
    """
    Cost utility function: u(p) = cost(p).
    
    Used for cost-based voting where utility equals project cost.
    
    Args:
        project: A pabutools Project object with .cost attribute
        
    Returns:
        The project's cost
    """
    return project.cost


def filter_sd(sd: List, keys_to_keep: List) -> List:
    """
    Filter a sorted list of (key, value) pairs to keep only specified keys.
    
    Args:
        sd: Sorted list of (key, value) tuples
        keys_to_keep: List of keys to retain
        
    Returns:
        Filtered list maintaining original order
    """
    return [item for item in sd if item[0] in keys_to_keep]


def calculate_bang_per_buck(project, number_paying_voters: int, utility_function: Callable) -> float:
    """
    Calculate the bang-per-buck ratio for a project.
    
    Bang-per-buck = utility(project) * number_of_payers / cost(project)
    
    Args:
        project: A pabutools Project object
        number_paying_voters: Number of voters who will pay for the project
        utility_function: Function that returns utility for a project
        
    Returns:
        The bang-per-buck ratio
    """
    return utility_function(project) * number_paying_voters / project.cost


def get_project_support(projects, profile: List[Dict]) -> Dict:
    """
    Compute which voters support each project.
    
    Args:
        projects: Iterable of project objects
        profile: Preprocessed profile (list of voter dicts)
        
    Returns:
        Dict mapping project -> list of supporting voter names
    """
    return {
        project: [voter['name'] for voter in profile if project in voter['approved']]
        for project in projects
    }


def initialize_payments(profile: List[Dict], projects) -> Dict:
    """
    Initialize payment matrix with zeros.
    
    Args:
        profile: Preprocessed profile
        projects: Iterable of projects
        
    Returns:
        Dict mapping (voter_name, project) -> 0
    """
    return {(voter['name'], project): 0 for voter in profile for project in projects}


def initialize_shares(profile: List[Dict], budget: float) -> Dict:
    """
    Initialize voter budget shares.
    
    Args:
        profile: Preprocessed profile
        budget: Total budget to divide equally
        
    Returns:
        Dict mapping voter_name -> budget/num_voters
    """
    num_voters = len(profile)
    return {voter['name']: budget / num_voters for voter in profile}

