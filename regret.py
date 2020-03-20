import scipy.spatial as spt
import numpy as np
import pickle
import random, math, statistics

KROA = "kroA100.tsp"
KROB = "kroB100.tsp"
BATCH = 0.5
# zmienic kryterium na cala sciezke!

class Regret():
    def __init__(self, distances, first):
        self.distances = distances
        self.first = first
        self.current = first
        self.stop = 0
        self.path = []
        self.path_length = 0
        self.nodes_first = {}

    def listToDict(self, lst):
        nodes = { i : lst[i] for i in range(0, len(lst) ) }
        for n in nodes.copy().keys():
            if n in self.path: del nodes[n]
        return nodes      

    def findNextNode(self):
        self.path.append(self.current)
        nodes = self.listToDict(self.distances[self.current])
        # print(f"{self.current}: path:\t {self.path_length}")
        
        self.stop -= 1
        if self.stop > 0:
            regrets = {}
            for nkey in nodes.keys():
                regret_values = []
                regret = 0
                for nkey2 in nodes.keys():
                    regret_values.append(self.distances[nkey2][nkey] + self.distances[self.first][nkey]) # EUC(first, A) + EUC(B, A)

                min_regret_value = min(regret_values)       
                for each in regret_values:
                    regret += abs(each-min_regret_value)
                
                regrets[nkey] = regret

            self.current = max(nodes.keys(), key=(lambda k: regrets[k]))
            self.path_length += nodes[self.current]  
            self.findNextNode()


    def start(self):
        self.stop = math.ceil(len(self.distances) * BATCH)
        self.findNextNode()

        # close cycle (last to first node)
        self.path.append(self.first)
        self.path_length += self.distances[self.current][self.first]

        # print(f"LAST: {self.current} :\t {self.path_length}")

        return self.path_length, self.path


def serialize(item):
    with open('serialized', 'wb') as fp:
        pickle.dump(item, fp)


def deserialize():
    with open ('serialized', 'rb') as fp:
        itemlist = pickle.load(fp)  
    return itemlist


def getInctances(path):
    takeCoords = False
    coords = []
    with open(path) as fp: 
        lines = fp.readlines() 
        for line in lines: 
            l_elems = line.split(' ')
            if l_elems[0] == 'EOF\n': takeCoords = False
            elif takeCoords: coords.append((int(l_elems[1]), int(l_elems[2].replace("\\n",""))))
            elif l_elems[0] == 'NODE_COORD_SECTION\n': takeCoords = True
    return np.array(coords)


def calculateDistances(coords):
    distances = []
    for a in coords:
        temp = []
        for b in coords:
            temp.append( int(round(spt.distance.euclidean(a,b))) )
        distances.append(temp)
    return distances


def main():
    coords = getInctances(KROB)
    distances = calculateDistances(coords)
    path_lengths = []
    paths = []

    # check for starting in each node
    # for i in range(len(distances)):
    #     reg = Regret(distances, i)
    #     p_len, path = reg.start()
    #     path_lengths.append(p_len)
    #     paths.append(path)
    #     print(f"{i} :\t {p_len}")

    for i in range(10):
        r = random.randint(0,99)
        reg = Regret(distances, r)
        p_len, path = reg.start()
        path_lengths.append(p_len)
        paths.append(path)
        print(f"{r} :\t {p_len}")

    min_path_length = min(path_lengths)
    min_path = paths[path_lengths.index(min_path_length)]

    max_path_length = max(path_lengths)
    max_path = paths[path_lengths.index(max_path_length)]

    avg_path_length = statistics.mean(path_lengths)

    print(min_path_length)
    print(min_path)

    print(max_path_length)
    print(max_path)

    print(avg_path_length)


if __name__ == "__main__":
    main()
    