import greedy
import utils
import time
import copy
from itertools import product
import random
import numpy as np
import pandas as pd 

KROA = "kroA200"
KROB = "kroB200"

class ILS():
    def __init__(self, distances, perts=20, vertex=False):
        self.distances = distances
        self.dist_len = len(distances)
        self.vertex = vertex # or edge
        self.perts = perts

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


    def _steepest(self, iter):
        solution, time1, better_out, better_in = self._init_params(iter)
        init_solutions = []
        results = {}
       
        count = 0
        while time.time() - time1 <= 200:
            count += 1
            solution = utils.perturbate(self.dist_len, solution, self.perts)

            while better_in or better_out:
                current = None
                complementary_solution = list(set(range(self.dist_len)) - set(solution))

                # 1 - change
                better_out = False
                best = 0

                for remove_id, insert_id in product(range(int(self.dist_len/2)), repeat=2):
                    diff = utils.get_value_of_change_vertices(self.distances, solution, complementary_solution, remove_id, insert_id)
                    if diff < best:
                        current = copy.deepcopy(solution)
                        current[remove_id] = complementary_solution[insert_id]
                        best = diff
                        better_out = True
                        # break

                if better_out is False:
                    current = copy.deepcopy(solution)

            
                # 2 - swap
                better_in = False
                best = 0
                bswap = (0,0)
                for swap_a_id, swap_b_id in product(range( int(self.dist_len/2)), repeat=2):
                    if swap_b_id <= swap_a_id:
                        continue

                    if self.vertex:
                        diff = utils.get_value_of_swap_vertices(self.distances, current, swap_a_id, swap_b_id)
                    else:
                        diff = utils.get_value_of_swap_edges(self.distances, current, swap_a_id, swap_b_id)

                    if diff < best:
                        bswap = (swap_a_id, swap_b_id)
                        best = diff
                        better_in = True               

                if better_in:
                    if self.vertex:
                        current[bswap[0]], current[bswap[1]] = current[bswap[1]], current[bswap[0]]

                    else:
                        current = current[:bswap[0] + 1] + current[bswap[0] + 1:bswap[1] + 1][::-1] + \
                                    current[bswap[1] + 1:]
                
                # final
                if better_in or better_out:
                    solution = current
        
            results[count] = {
                    'path': copy.deepcopy(solution + [solution[0]]),
                    'cost': self._solution_cost(solution + [solution[0]]),
                    'i': count
                }

        best_solution = min(results, key=lambda key: results[key]['cost'])
        
        path = results[best_solution]['path'] 
        cost = results[best_solution]['cost']
        final_time = time.time() - time1

        return path, cost, final_time

    def run(self, run_times=100):
        self.solutions = []
        for i in range(run_times):
            print(i)
            self.solutions.append(self._steepest(i))
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
        
        ls = ILS(distances)
        ls.run(10)
        for s, cost, time in ls.solutions:
            df = df.append(
                pd.DataFrame([[instance, cost, time]], 
                columns=['instance', 'cost', 'time']))

        costs = list(map(lambda x: x[1], ls.solutions))
        label = f'ILS | {instance} | distance: {ls.best_cost}'
        save_name = f'ils_{instance}'

        greedy.show_on_plot(coords, ls.best_solution, label=label, save=True, savename=save_name)
        df['cost'] = df['cost'].astype(float)
        df_cost = df.groupby(['instance']).agg({'cost' : ['min','mean','max']}).astype(int)
        print(df_cost)
        df_time = df.groupby(['instance']).agg({'time' : ['min','mean', 'max']}).round(4)
        print(df_time)
        print(" --- --- --- --- ---")


if __name__ == "__main__":
    main()