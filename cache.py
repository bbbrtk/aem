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

class LocalSearchCache():
    def __init__(self, distances, greedy=True, vertex=True):
        self.distances = distances
        self.dist_len = len(distances)
        self.greedy = greedy # or steepest
        self.vertex = vertex # or edge

        self.best_solution = []
        self.best_cost = 0
        self.solutions = []
        
        self.path = []
        self.path_length = 0

    def _init_params(self, iter):
        t1 = time.time()
        # same random numbers to ease debug
        # np.random.seed(iter)
        # random.seed(iter)
        # random solution
        solution = random.sample(list(range(self.dist_len)), int(self.dist_len/2))
        better_out = True
        better_in = True
        return solution, t1, better_out, better_in


    def _steepest(self, iter):
        solution, time1, better_out, better_in = self._init_params(iter)
        cache_list = []

        for swap_a_id, swap_b_id in product(range(int(self.dist_len/2)), repeat=2):
            if swap_b_id <= swap_a_id:
                continue

            diff = utils.get_value_of_swap_edges(self.distances, solution, swap_a_id, swap_b_id)

            if diff < 0:
                cache_list.append((swap_a_id, swap_b_id, diff))

        cache_list.sort(key=lambda tup: tup[2])

        
        while better_in or better_out:
            current = None
            complementary_solution = list(set(range(self.dist_len)) - set(solution))

            # 1 - change
            better_out = False
            best = 0
            best_id = 0
            for remove_id, insert_id in product(range(int(self.dist_len/2)), repeat=2):
                diff = utils.get_value_of_change_vertices(self.distances, solution, complementary_solution, remove_id, insert_id)
                if diff < best:
                    current = copy.deepcopy(solution)
                    current[remove_id] = complementary_solution[insert_id]
                    best = diff
                    best_id = remove_id
                    better_out = True
                    # break

            if better_out is False:
                current = copy.deepcopy(solution)

            if better_out:
                cache_list = utils.remove_vertex_from_cache(cache_list, [best_id])
                cache_list = utils.cache_append_every_possible_pair_with_vertex(self.distances, cache_list, current, [best_id])
                

            
            # 2 - swap
            better_in = False
            bswap = (0,0)

            for elem in range(len(cache_list)):
                poss_insrt = cache_list[elem]
                diff = utils.get_value_of_swap_edges(self.distances, current, poss_insrt[0], poss_insrt[1])
                if poss_insrt[2] == diff:
                    bswap = [poss_insrt[0], poss_insrt[1]]
                    current = current[:bswap[0] + 1] + current[bswap[0] + 1:bswap[1] + 1][::-1] + \
                                current[bswap[1] + 1:]
                    better_in = True
                    x = self._solution_cost(current + [current[0]])
                    break

            for elem1, elem2 in enumerate(cache_list):
                if elem1 <= elem:
                    # print("HAPPEN")
                    cache_list.remove(cache_list[elem1])
                 

            if better_in:
                indices_to_change = [bswap[0], bswap[1], (bswap[0] + 1) % int(self.dist_len/2),
                                     (bswap[1] + 1) % int(self.dist_len/2) ]
                cache_list = utils.remove_vertex_from_cache(cache_list, indices_to_change)
                cache_list = utils.cache_append_every_possible_pair_with_vertex(self.distances, cache_list, current, indices_to_change)
            
            # final
            if better_in or better_out:
                solution = current
        
        solution += [solution[0]]
        cost = self._solution_cost(solution)
        final_time = time.time() - time1

        return solution, cost, final_time

    def run(self, run_times=100):
        self.solutions = []
        for i in range(run_times):
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
        
        ls = LocalSearchCache(distances)
        ls.run(100)
        for s, cost, time in ls.solutions:
            df = df.append(
                pd.DataFrame([[instance, cost, time]], 
                columns=['instance', 'cost', 'time']))

        costs = list(map(lambda x: x[1], ls.solutions))
        label = f'Cache | {instance} | distance: {ls.best_cost}'
        save_name = f'cache_{instance}'

        greedy.show_on_plot(coords, ls.best_solution, label=label, save=True, savename=save_name)

        # print(df.head())
        # print("min_cost: ", min(costs))
        df['cost'] = df['cost'].astype(float)
        df_cost = df.groupby(['instance']).agg({'cost' : ['min','mean','max']}).astype(int)
        print(df_cost)
        df_time = df.groupby(['instance']).agg({'time' : ['min','mean', 'max']}).round(4)
        print(df_time)
        print(" --- --- --- --- ---")


if __name__ == "__main__":
    main()