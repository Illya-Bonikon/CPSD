import numpy as np
import pytest
from main import TREE, BURNING, EMPTY, step_forest_fire

def test_tree_ignites_from_burning_neighbor():
    grid = np.array([
        [TREE, BURNING],
        [TREE, TREE]
    ])
    burn_time = np.array([
        [0, 2],
        [0, 0]
    ])
    
    new_grid, new_burn_time = step_forest_fire(grid, burn_time, p_burn=1.0, t_burn=2)
    assert new_grid[0,0] == BURNING
    assert new_burn_time[0,0] == 2
    print("Testing test_tree_ignites_from_burning_neighbor passed")

def test_burning_tree_becomes_empty():
    grid = np.array([
        [BURNING]
    ])
    burn_time = np.array([
        [1]
    ])
    new_grid, new_burn_time = step_forest_fire(grid, burn_time, p_burn=0.0, t_burn=1)
    assert new_grid[0,0] == EMPTY
    assert new_burn_time[0,0] == 0
    print("Testing test_burning_tree_becomes_empty passed")

def test_tree_does_not_ignite_without_burning_neighbor():
    grid = np.array([
        [TREE, TREE],
        [TREE, TREE]
    ])
    burn_time = np.zeros_like(grid)
    new_grid, new_burn_time = step_forest_fire(grid, burn_time, p_burn=1.0, t_burn=2)
    assert np.all(new_grid == TREE)
    assert np.all(new_burn_time == 0)
    print("Testing test_tree_does_not_ignite_without_burning_neighbor passed")

def test_empty_remains_empty():
    grid = np.array([
        [EMPTY]
    ])
    burn_time = np.array([
        [0]
    ])
    new_grid, new_burn_time = step_forest_fire(grid, burn_time)
    assert new_grid[0,0] == EMPTY
    assert new_burn_time[0,0] == 0
    print("Testing test_empty_remains_empty passed")

def test_invalid_grid_shape():
    grid = np.array([TREE, BURNING])  
    burn_time = np.array([0, 1])
    with pytest.raises(IndexError):
        step_forest_fire(grid, burn_time)
    print("Testing test_invalid_grid_shape passed")

def test_invalid_burn_time_shape():
    grid = np.array([[TREE, BURNING], [TREE, TREE]])
    burn_time = np.array([[0, 1]])  
    with pytest.raises(ValueError):
        step_forest_fire(grid, burn_time)
    print("Testing test_invalid_burn_time_shape passed")

def test_probabilistic_ignition():
    
    grid = np.array([[TREE, BURNING]])
    burn_time = np.array([[0, 2]])
    new_grid, new_burn_time = step_forest_fire(grid, burn_time, p_burn=0.0, t_burn=2)
    assert new_grid[0,0] == TREE
    assert new_burn_time[0,0] == 0 
    print("Testing test_probabilistic_ignition passed") 