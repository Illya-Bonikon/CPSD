import numpy as np
import random

class GraphGenerator:
    def __init__(self, n_vertices: int, weight_min: int, weight_max: int):
        if n_vertices < 3:
            raise ValueError("Кількість вершин має бути не менше 3")
        if weight_min < 1:
            raise ValueError("Мінімальна вага має бути не менше 1")
        if weight_max < weight_min:
            raise ValueError("Максимальна вага має бути не менше мінімальної")
        self.n = n_vertices
        self.w_min = weight_min
        self.w_max = weight_max

    def generate(self):
        mat = np.zeros((self.n, self.n), dtype=int)
        for i in range(self.n):
            for j in range(i+1, self.n):
                w = random.randint(self.w_min, self.w_max)
                mat[i, j] = mat[j, i] = w
        return mat 