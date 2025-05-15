import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Стан клітини
TREE = 0      # незаймана
BURNING = 1   # горить
EMPTY = 2     # згоріла

# Параметри моделі
GRID_SIZE = 50
P_BURN = 0.3        # Ймовірність загоряння сусідньої клітини
T_BURN = 3          # Кількість кроків, поки клітина горить

# Ініціалізація сітки та часу горіння
grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
burn_time = np.zeros_like(grid)

# Початкові умови – клітина в центрі горить
mid = GRID_SIZE // 2
grid[mid, mid] = BURNING
burn_time[mid, mid] = T_BURN

# Колірна мапа для візуалізації
colors = ['green', 'red', 'black']
cmap = plt.cm.colors.ListedColormap(colors)

def update(frame):
    global grid, burn_time

    new_grid = grid.copy()
    new_burn_time = burn_time.copy()

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x, y] == TREE:
                # Перевірка сусідів
                neighbors = grid[max(0, x-1):min(x+2, GRID_SIZE),
                                 max(0, y-1):min(y+2, GRID_SIZE)]
                if np.any(neighbors == BURNING) and np.random.rand() < P_BURN:
                    new_grid[x, y] = BURNING
                    new_burn_time[x, y] = T_BURN

            elif grid[x, y] == BURNING:
                new_burn_time[x, y] -= 1
                if new_burn_time[x, y] <= 0:
                    new_grid[x, y] = EMPTY

    grid = new_grid
    burn_time = new_burn_time
    mat.set_data(grid)
    return [mat]

# Візуалізація
fig, ax = plt.subplots()
mat = ax.matshow(grid, cmap=cmap)
plt.title("Модель лісової пожежі")
ani = animation.FuncAnimation(fig, update, interval=300)
plt.show()
