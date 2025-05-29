import numpy as np
import random
from multiprocessing import Process, Queue

class GAIsland(Process):
    def __init__(self, island_id, graph, pop_size, epochs, mut_prob, cross_prob, result_queue):
        super().__init__()
        self.island_id = island_id
        self.graph = graph
        self.n = graph.shape[0]
        self.pop_size = pop_size
        self.epochs = epochs
        self.mut_prob = mut_prob
        self.cross_prob = cross_prob
        self.result_queue = result_queue

    def run(self):
        try:
            pop = [self.random_path() for _ in range(self.pop_size)]
            stats = []
            for gen in range(self.epochs):
                if len(pop) == 0:
                    raise ValueError("Популяція порожня! Перевірте параметри популяції.")
                fitness = [self.path_length(p) for p in pop]
                idx_sorted = np.argsort(fitness)
                best = pop[idx_sorted[0]]
                second = pop[idx_sorted[1]]
                worst = pop[idx_sorted[-1]]
                avg = float(np.mean(fitness))
                stats.append({
                    'generation': gen,
                    'best': {'path': best.copy(), 'length': fitness[idx_sorted[0]]},
                    'second': {'path': second.copy(), 'length': fitness[idx_sorted[1]]},
                    'worst': {'path': worst.copy(), 'length': fitness[idx_sorted[-1]]},
                    'avg': avg
                })
                new_pop = [best.copy()]
                while len(new_pop) < self.pop_size:
                    p1 = self.tournament(pop, fitness)
                    p2 = self.tournament(pop, fitness)
                    if random.random() < self.cross_prob:
                        c1, c2 = self.order_crossover(p1, p2)
                    else:
                        c1, c2 = p1.copy(), p2.copy()
                    if random.random() < self.mut_prob:
                        self.swap_mutation(c1)
                    if random.random() < self.mut_prob:
                        self.swap_mutation(c2)
                    new_pop.extend([c1, c2])
                pop = new_pop[:self.pop_size]
            self.result_queue.put({'island': self.island_id, 'stats': stats})
        except Exception as e:
            self.result_queue.put({'island': self.island_id, 'error': str(e)})

    def random_path(self):
        path = list(range(self.n))
        random.shuffle(path)
        return path

    def path_length(self, path):
        return sum(self.graph[path[i], path[(i+1)%self.n]] for i in range(self.n))

    def tournament(self, pop, fitness, k=3):
        idxs = random.sample(range(len(pop)), k)
        best = min(idxs, key=lambda i: fitness[i])
        return pop[best].copy()

    def order_crossover(self, p1, p2):
        a, b = sorted(random.sample(range(self.n), 2))
        c1 = [None]*self.n
        c1[a:b] = p1[a:b]
        fill = [x for x in p2 if x not in c1[a:b]]
        ptr = 0
        for i in range(self.n):
            if c1[i] is None:
                c1[i] = fill[ptr]
                ptr += 1
        c2 = [None]*self.n
        c2[a:b] = p2[a:b]
        fill = [x for x in p1 if x not in c2[a:b]]
        ptr = 0
        for i in range(self.n):
            if c2[i] is None:
                c2[i] = fill[ptr]
                ptr += 1
        return c1, c2

    def swap_mutation(self, path):
        i, j = random.sample(range(self.n), 2)
        path[i], path[j] = path[j], path[i]

class ParallelGA:
    def __init__(self, graph, pop_size, epochs, mut_prob, cross_prob, n_islands):
        self.graph = graph
        self.pop_size = pop_size
        self.epochs = epochs
        self.mut_prob = mut_prob
        self.cross_prob = cross_prob
        self.n_islands = n_islands

    def run(self):
        result_queue = Queue()
        islands = [GAIsland(i, self.graph, self.pop_size, self.epochs, self.mut_prob, self.cross_prob, result_queue)
                   for i in range(self.n_islands)]
        for island in islands:
            island.start()
        all_stats = [result_queue.get() for _ in islands]
        for island in islands:
            island.join()
        # Перевірка на помилки з островів
        for stat in all_stats:
            if 'error' in stat:
                raise ValueError(f"GAIsland {stat['island']} error: {stat['error']}")
        merged_stats = []
        for gen in range(self.epochs):
            gen_best = None
            gen_second = None
            gen_worst = None
            best_len = float('inf')
            second_len = float('inf')
            worst_len = -float('inf')
            avg_sum = 0
            for island_stat in all_stats:
                s = island_stat['stats'][gen]
                if s['best']['length'] < best_len:
                    second_len = best_len
                    gen_second = gen_best
                    best_len = s['best']['length']
                    gen_best = s['best']
                elif s['best']['length'] < second_len:
                    second_len = s['best']['length']
                    gen_second = s['best']
                if s['worst']['length'] > worst_len:
                    worst_len = s['worst']['length']
                    gen_worst = s['worst']
                avg_sum += s['avg']
            avg = avg_sum / self.n_islands
            merged_stats.append({
                'generation': gen,
                'best': gen_best,
                'second': gen_second,
                'worst': gen_worst,
                'avg': avg
            })
        return merged_stats 