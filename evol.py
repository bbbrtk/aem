import greedy
import utils
import time
import copy
from itertools import product
import random
import numpy as np
import pandas as pd 
import localsearch

KROA = "kroA200"
KROB = "kroB200"

class Evol():
    def __init__(self, distances, population=20, perts=6, vertex=False):
        self.distances = distances
        self.dist_len = len(distances)
        self.vertex = vertex # or edge
        self.perts = perts
        self.population = population

        self.best_solution = []
        self.best_cost = 0
        self.solutions = []
        
        self.path = []
        self.path_length = 0

    def _init_params(self, iter):
        t1 = time.time()
        solution = random.sample(list(range(self.dist_len)), int(self.dist_len/2))
        better_out = True
        better_in = True
        return solution, t1, better_out, better_in


    def _evol_run(self, iter):
        solution3, time1, better_out, better_in = self._init_params(iter)
        pop = np.array([np.random.permutation(self.dist_len) for _ in range(self.population)])[:, :self.dist_len // 2]
        costs = np.zeros(self.population)
        init_solutions = []
        results = {}
        local = localsearch.LocalSearch(self.distances,False,False)
        for i in range(self.population):
            pop[i], costs[i] = local.solve(pop[i], iter)
       
        count = 0
        while time.time() - time1 <= 200:
            idx_1, idx_2 = np.random.randint(0, len(pop), 2)
            parent_1, parent_2 = pop[idx_1], pop[idx_2]
            child = utils.crossover(parent_1, parent_2)
            child = utils.perturbate(self.dist_len, self.perts, child)
            child, cost = local.solve(pop[i], iter)
            in_list = False

            for p in range(len(pop)):
                if len(set(child) & set(pop[p])) == len(set(child)) and cost == costs[p]:
                    in_list = True
                    break

            if not in_list:
                max_id = np.argmax(costs)
                if costs[max_id] > cost:
                    pop[max_id] = child
                    costs[max_id] = cost
                    # print(time.time() - start, np.min(costs), np.mean(costs), np.max(costs))

        best_id = np.argmin(costs)
        solution = list(pop[best_id])
        solution += [solution[0]]
        cost= self._solution_cost(solution)
        print(cost)
        return solution, cost, time.time() - time1


    def run(self, run_times=100):
        self.solutions = []
        for i in range(run_times):
            print(i)
            self.solutions.append(self._evol_run(i))
        s, c, _ = min(self.solutions, key=lambda x: x[1])
        self.best_solution = s
        self.best_cost = c

    def _solution_cost(self, solution):
        return sum([self.distances[id_source, id_destination] for id_source, id_destination in zip(solution, solution[1:])])


def main():
    print(" --- --- start --- ---")
    for instance in [KROA, KROB]:
        instance_file = f"instances/{instance}.tsp"
        coords, distances = greedy.load_instance_tsplib(instance_file)

        df = pd.DataFrame(columns=['instance', 'cost', 'time'])
        
        ls = Evol(distances)
        ls.run(10) # 10
        for s, cost, time in ls.solutions:
            df = df.append(
                pd.DataFrame([[instance, cost, time]], 
                columns=['instance', 'cost', 'time']))

        costs = list(map(lambda x: x[1], ls.solutions))
        label = f'Evol | {instance} | distance: {ls.best_cost}'
        save_name = f'Evol_{instance}'

        greedy.show_on_plot(coords, ls.best_solution, label=label, save=True, savename=save_name)
        df['cost'] = df['cost'].astype(float)
        df_cost = df.groupby(['instance']).agg({'cost' : ['min','mean','max']}).astype(int)
        print(df_cost)
        df_time = df.groupby(['instance']).agg({'time' : ['min','mean', 'max']}).round(4)
        print(df_time)
        print(" --- --- --- --- ---")


if __name__ == "__main__":
    main()