import math, statistics, random
import scipy.spatial as spt
import numpy as np
import matplotlib.pyplot as plt 

from tsplib95 import Problem, load_problem
from tsplib95.distances import euclidean
from collections import OrderedDict
from operator import itemgetter
from copy import deepcopy

KROA = "instances/kroA100.tsp"
KROB = "instances/kroB100.tsp"
PART_OF_POPULATION = 0.5


class Greedy():
    def __init__(self, distances, first, regret=False):
        self.distances = distances
        self.first = first
        self.current = first
        self.regret = regret
        self.stop = 0
        self.path = []
        self.path_length = 0
        self.nodes_first = {}

    def list_to_dict(self, lst):
        nodes = { i : lst[i] for i in range(0, len(lst) ) }
        for n in nodes.copy().keys():
            if n in self.path: del nodes[n]
        return nodes      

    def find_next_node(self):
        self.path.append(self.current)
        nodes = self.list_to_dict(self.distances[self.current])
        # print(f"{self.current} :\t {self.path_length}")
        
        self.stop -= 1
        if self.stop > 0: 
            self.current = min(
                nodes.keys(), key=(lambda k: \
                    self.distances[self.current][k] + \
                    self.distances[self.first][k] - \
                    self.distances[self.current][self.first]
                    )
                )
            self.path_length += nodes[self.current]  
            self.find_next_node()

    def find_next_node_wtih_regret(self):
        self.path.append(self.current)
        nodes = self.list_to_dict(self.distances[self.current])
        # print(f"{self.current}: path:\t {self.path_length}")
        
        self.stop -= 1
        if self.stop > 0:
            regrets = {}
            for nkey in nodes.keys():
                regret_values = []
                for nkey2 in nodes.keys():
                    regret_values.append(
                        self.distances[nkey][self.first] + \
                        self.distances[nkey][nkey2] + \
                        self.distances[nkey2][self.first]
                        ) 
                
                min_regret_value = min(regret_values) 

                regret = 0     
                for each in regret_values:
                    regret += each - min_regret_value  

                regrets[nkey] = regret

            self.current = max(nodes.keys(), key=(lambda k: regrets[k]))
            self.path_length += nodes[self.current]  
            self.find_next_node_wtih_regret()


    def start(self):
        self.stop = math.ceil(len(self.distances) * PART_OF_POPULATION)

        if self.regret: self.find_next_node_wtih_regret()
        else:           self.find_next_node()

        # close cycle (last to first node)
        self.path.append(self.first)
        self.path_length += self.distances[self.current][self.first]
        
        return self.path_length, self.path


def load_instance_tsplib(path):
    problem = load_problem(path)
    coords = problem.node_coords
    d = problem.dimension

    dimension_matrix = np.zeros(shape=(d, d), dtype=np.int)
    for i in range(d):
        for j in range(d):
            dimension_matrix[i, j] = int(round(euclidean(coords[i + 1], coords[j + 1])))

    final_coords = np.array(list(coords.values()))
    return final_coords, dimension_matrix


def calculate_distances(coords):
    distances = []
    for a in coords:
        temp = []
        for b in coords:
            temp.append( int(round(spt.distance.euclidean(a,b))) )
        distances.append(temp)
    return distances


def load_instances(path):
    takeCoords = False
    coords = []
    with open(path) as fp: 
        lines = fp.readlines() 
        for line in lines: 
            l_elems = line.split(' ')
            if l_elems[0] == 'EOF\n': takeCoords = False
            elif takeCoords: coords.append((int(l_elems[1]), int(l_elems[2].replace("\\n",""))))
            elif l_elems[0] == 'NODE_COORD_SECTION\n': takeCoords = True

    final_coords =  np.array(coords)
    dimension_matrix = calculate_distances(final_coords)
    return final_coords, dimension_matrix


def show_on_plot(coords, path, label="", save=False, savename="plot"):
    c0 = [row[0] for row in coords]
    c1 = [row[1] for row in coords]
    c_num = [i for i in range(len(coords))]

    lines = itemgetter(*path)(coords)
    lines0 = [row[0] for row in lines]
    lines1 = [row[1] for row in lines]

    fig, ax = plt.subplots()
    plt.plot(lines0, lines1, '-r')

    ax.scatter(c0, c1)

    for i, txt in enumerate(c_num):
        ax.annotate(txt, (c0[i], c1[i]))
    plt.title(label)
    if save: plt.savefig(savename)
    # plt.show()


def run_multiple_times(distances, repeat=10, regret=False, show_paths=False):
    path_lengths = []
    paths = []

    for i in range(repeat):
        r = random.randint(0,99)
        greed = Greedy(distances, i, regret)
        p_len, path = greed.start()
        path_lengths.append(p_len)
        paths.append(path)
        # print(f"{r} :\t {p_len}")

    min_path_length = min(path_lengths)
    min_path = paths[path_lengths.index(min_path_length)]

    max_path_length = max(path_lengths)
    max_path = paths[path_lengths.index(max_path_length)]

    avg_path_length = statistics.mean(path_lengths)

    print(f"__regret: \t {regret}")
    print(f"__run: \t\t {repeat} times")
    print(f"__population:\t {PART_OF_POPULATION*len(distances)} of {len(distances)}")
    print("MIN path len: \t", min_path_length)
    if show_paths: print("path: ", min_path)

    print("MAX path len: \t", max_path_length)
    if show_paths: print("path: ", max_path)

    print("AVG path len: \t", avg_path_length, "\n")

    return min_path


def main():
    for instance in [KROA, KROB]:
        print(f"__instance: \t {instance}")

        # if tsplib not installed:
        # coords, distances = load_instances(KROA)
        coords, distances = load_instance_tsplib(instance)

        for regret in [False, True]:
            min_path = run_multiple_times(distances, 100, regret, True)
            show_on_plot(coords, min_path)


if __name__ == "__main__":
    main()
    