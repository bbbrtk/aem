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

class LocalSearch():
    def __init__(self, distances, greedy=True, vertex=True):
        self.distances = distances
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
        solution = random.sample(list(range(100)), 50)
        better_out = True
        better_in = True
        return solution, t1, better_out, better_in

    def _out(self, current, solution, best_value=0):
        better_out = False
        complementary_solution = list(set(range(100)) - set(solution))
        for remove_id, insert_id in product(range(50), repeat=2):
            diff = utils.get_value_of_change_vertices(solution, complementary_solution, remove_id, insert_id)
            if diff < best_value:
                current = copy.deepcopy(solution)
                current[remove_id] = complementary_solution[insert_id]
                better_out = True
                break

        return current, better_out

    def _in(self, current, solution, best_value=0):
        better_in = False
        for swap_a_id, swap_b_id in product(range(50), repeat=2):
            if swap_b_id <= swap_a_id:
                continue

            if self.vertex:
                diff = utils.get_value_of_swap_vertices(current, swap_a_id, swap_b_id)
            else:
                diff = utils.get_value_of_swap_edges(current, swap_a_id, swap_b_id)

            if diff < 0:
                better_in = True
                if self.vertex:
                    current[swap_a_id], current[swap_b_id] = current[swap_b_id], current[
                        swap_a_id]
                else:
                    current = current[:swap_a_id + 1] + current[swap_a_id + 1:swap_b_id + 1][::-1] + \
                                current[swap_b_id + 1:]    

    def _greedy(self, iter):
        solution, time1, better_out, better_in = self._init_params(iter)

        while better_in or better_out:
            current = copy.deepcopy(solution)

            #out
            better_out = False
            complementary_solution = list(set(range(100)) - set(solution))
            for remove_id, insert_id in product(range(50), repeat=2):
                diff = utils.get_value_of_change_vertices(self.distances, solution, complementary_solution, remove_id, insert_id)
                if diff < 0:
                    current = copy.deepcopy(solution)
                    current[remove_id] = complementary_solution[insert_id]
                    better_out = True
                    break
            #in
            better_in = False
            for swap_a_id, swap_b_id in product(range(50), repeat=2):
                if swap_b_id <= swap_a_id:
                    continue

                if self.vertex:
                    diff = utils.get_value_of_swap_vertices(self.distances, current, swap_a_id, swap_b_id)
                else:
                    diff = utils.get_value_of_swap_edges(self.distances, current, swap_a_id, swap_b_id)

                if diff < 0:
                    better_in = True
                    if self.vertex:
                        current[swap_a_id], current[swap_b_id] = current[swap_b_id], current[swap_a_id]
                    else:
                        current = current[:swap_a_id + 1] + current[swap_a_id + 1:swap_b_id + 1][::-1] + \
                                    current[swap_b_id + 1:]
            # final
            if better_in or better_out:
                solution = current
        
        solution += [solution[0]]
        cost = self._solution_cost(solution)
        final_time = time.time() - time1

        return solution, cost, final_time


    def _steepest(self, iter):
        solution, time1, better_out, better_in = self._init_params(iter)
        while better_in or better_out:
            current = copy.deepcopy(solution) # or None
            complementary_solution = list(set(range(100)) - set(solution))

            # 1 - change
            better_out = False
            best = 0
            for remove_id, insert_id in product(range(50), repeat=2):
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
            for swap_a_id, swap_b_id in product(range(50), repeat=2):
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
        
        solution += [solution[0]]
        cost = self._solution_cost(solution)
        final_time = time.time() - time1

        return solution, cost, final_time

    def run(self, run_times=100):
        self.solutions = list()
        for i in range(run_times):
            if self.greedy:
                self.solutions.append(self._greedy(i))
            else:
                self.solutions.append(self._steepest(i))
        s, c, _ = min(self.solutions, key=lambda x: x[1])
        self.best_solution = s
        self.best_cost = c

    def _solution_cost(self, solution):
        return sum([self.distances[id_source, id_destination] for id_source, id_destination in zip(solution, solution[1:])])


def main():
    
    for isVertex in [True, False]:
        # for isGreedy in [True, False]:
        isGreedy = False
        
        for instance in [KROA, KROB]:
            instance_file = f"instances/{instance}.tsp"
            coords, distances = greedy.load_instance_tsplib(instance_file)

            df = pd.DataFrame(columns=['isGreedy', 'isVertex','instance', 'cost', 'time'])
            
            ls = LocalSearch(distances, greedy=isGreedy, vertex=isVertex)
            ls.run(100)
            for s, cost, time in ls.solutions:
                df = df.append(
                    pd.DataFrame([[isGreedy, isVertex, instance, cost, time]], 
                    columns=['isGreedy', 'isVertex','instance', 'cost', 'time']))

            costs = list(map(lambda x: x[1], ls.solutions))
            label = f'isGreedy: {isGreedy} | isVertex: {isVertex} | {instance} | distance: {ls.best_cost}'
            save_name = f'random_{instance}_V-{isVertex}_G-{isGreedy}'

            greedy.show_on_plot(coords, ls.best_solution, label=label, save=True, savename=save_name)

            # print(df.head())
            # print("min_cost: ", min(costs))
            df['cost'] = df['cost'].astype(float)
            df_cost = df.groupby(['instance', 'isVertex', 'isGreedy']).agg({'cost' : ['min','mean','max']}).astype(int)
            print(df_cost)
            df_time = df.groupby(['instance', 'isVertex', 'isGreedy']).agg({'time' : ['min','mean', 'max']}).round(4)
            print(df_time)
            print(" --- --- --- --- --- --- ---")



if __name__ == "__main__":
    main()