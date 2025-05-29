import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

TREE = 0      
BURNING = 1   
EMPTY = 2     

GRID_SIZE = 50
P_BURN = 0.3        
T_BURN = 3          

grid = np.full((GRID_SIZE, GRID_SIZE), TREE, dtype=int)
burn_time = np.zeros_like(grid)


mid = GRID_SIZE // 2
grid[mid, mid] = BURNING
burn_time[mid, mid] = T_BURN


colors = ['green', 'red', 'black']
cmap = plt.cm.colors.ListedColormap(colors)

def step_forest_fire(grid, burn_time, p_burn=P_BURN, t_burn=T_BURN):
    """
    Оновлює стан сітки та часу горіння для одного кроку моделі лісової пожежі.
    Повертає нові grid та burn_time.
    """
    if grid.shape != burn_time.shape:
        raise ValueError("grid і burn_time повинні мати однакову форму")
    new_grid = grid.copy()
    new_burn_time = burn_time.copy()
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] == TREE:
                neighbors = grid[max(0, x-1):min(x+2, grid.shape[0]),
                                 max(0, y-1):min(y+2, grid.shape[1])]
                if np.any(neighbors == BURNING) and np.random.rand() < p_burn:
                    new_grid[x, y] = BURNING
                    new_burn_time[x, y] = t_burn
            elif grid[x, y] == BURNING:
                new_burn_time[x, y] -= 1
                if new_burn_time[x, y] <= 0:
                    new_grid[x, y] = EMPTY
    return new_grid, new_burn_time

def update(frame):
    global grid, burn_time
    grid, burn_time = step_forest_fire(grid, burn_time)
    mat.set_data(grid)
    return [mat]


fig, ax = plt.subplots()
mat = ax.matshow(grid, cmap=cmap)
mat.set_clim(0, 2)
plt.title("Модель лісової пожежі")
ani = animation.FuncAnimation(fig, update, interval=300)
plt.show()
