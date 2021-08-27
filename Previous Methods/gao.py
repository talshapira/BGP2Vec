from collections import defaultdict
import numpy as np

class Gao:
    
    TOR_ORIG_LABELS_DICT = {'P2P':0, 'C2P': 1,'Siblings': 2, 'P2C': 3}
    L = 1
    R = float("inf")
    
    def __init__(self, routing_tables, l=L, r=R):
        self.routing_tables = routing_tables
        self.L = l
        self.R = r
        self.degrees = dict()
        self.transit = defaultdict(lambda:0)
        self.tor_dict = dict()
        self.not_peering = defaultdict(lambda:0)
        
        self.__gao()


    def __compute_as_degree(self):
        neighbors = defaultdict(set)
        
        for as_path in self.routing_tables:
            for i in range(len(as_path)-1):
                neighbors[as_path[i]].add(as_path[i+1])
                neighbors[as_path[i+1]].add(as_path[i])
        for asn, asn_neighbors in neighbors.items():
            self.degrees[asn] = len(asn_neighbors)
        print("Finished __compute_as_degree")
    

    def __compute_as_transit_rank(self):
        for as_path in self.routing_tables:
            j = 0
            max_degree = 0
            for i in range(len(as_path)):
                if self.degrees[as_path[i]] > max_degree:
                    j = i
                    max_degree = self.degrees[as_path[i]]
            for i in range(j):
                self.transit[(as_path[i], as_path[i+1])] += 1
            for i in range(j, len(as_path)-1):
                self.transit[(as_path[i+1], as_path[i])] += 1
        print("Finished __compute_as_transit_rank")


    def __assign_p2c_c2p_siblings_tors(self):
        for as_path in self.routing_tables:
            for i in range(len(as_path)-1):
                if (self.transit[(as_path[i+1], as_path[i])] > self.L and self.transit[(as_path[i], as_path[i+1])] > self.L) or (0 < self.transit[(as_path[i], as_path[i+1])] <= self.L and 0 < self.transit[(as_path[i+1], as_path[i])] <= self.L):
                    self.tor_dict[(as_path[i], as_path[i+1])] = 2
                elif self.transit[(as_path[i+1], as_path[i])] > self.L or self.transit[(as_path[i], as_path[i+1])] == 0:
                    self.tor_dict[(as_path[i], as_path[i+1])] = 3
                elif self.transit[(as_path[i], as_path[i+1])] > self.L or self.transit[(as_path[i+1], as_path[i])] == 0:
                    self.tor_dict[(as_path[i], as_path[i+1])] = 1
        print("Finished __assign_p2c_c2p_siblings_tors")
            
        
    def __identify_not_peering(self):
        for as_path in self.routing_tables:
            j = 0
            max_degree = 0
            for i in range(len(as_path)):
                if self.degrees[as_path[i]] > max_degree:
                    j = i
                    max_degree = self.degrees[as_path[i]]
            for i in range(j - 1):
                self.not_peering[(as_path[i], as_path[i+1])] = 1
            for i in range(j+1, len(as_path)-1):
                self.not_peering[(as_path[i], as_path[i+1])] = 1
            if ((as_path[j-1], as_path[j]) not in self.tor_dict or self.tor_dict[(as_path[j-1], as_path[j])] != 2) and ((as_path[j], as_path[j-1]) not in self.tor_dict or  self.tor_dict[(as_path[j], as_path[j-1])] != 2):
                if j != len(as_path) - 1 and self.degrees[as_path[j-1]] > self.degrees[as_path[j+1]]:
                    self.not_peering[(as_path[j], as_path[j+1])] = 1
                else:
                    self.not_peering[(as_path[j-1], as_path[j])] = 1
        print("Finished __identify_not_peering")


    def __assign_p2p_tors(self):
        for as_path in self.routing_tables:
            for i in range(len(as_path)-1):
                if self.not_peering[(as_path[i], as_path[i+1])] != 1 and self.not_peering[(as_path[i+1], as_path[i])] != 1 and 1.0/self.R < 1.0*self.degrees[as_path[i]]/self.degrees[as_path[i+1]] < self.R:
                    self.tor_dict[(as_path[i], as_path[i+1])] = 0
        print("Finished __assign_p2p_tors")
    
        
    def __gao(self):
        self.__compute_as_degree()
        self.__compute_as_transit_rank()
        self.__assign_p2c_c2p_siblings_tors()
        self.__identify_not_peering()
        self.__assign_p2p_tors()
    
    
    def tor_dict2dataset(self):
        dataset = []
        labels = []
        for pair, label in self.tor_dict.iteritems():
            dataset.append(np.asarray(pair))
            labels.append(label)
        print("Finished __tor_dict2dataset")
        return np.asarray(dataset), np.asarray(labels)
        
        
    def generate_labels_for_set(self, pairs):
        labels = []
        for pair in pairs:
            if (pair[0], pair[1]) in self.tor_dict:
                labels.append(self.tor_dict[(pair[0], pair[1])])
            elif (pair[1], pair[0]) in self.tor_dict:
                if self.tor_dict[(pair[1], pair[0])] == 0 or self.tor_dict[(pair[1], pair[0])] == 2:
                    labels.append(self.tor_dict[(pair[1], pair[0])])
                else:
                    labels.append((self.tor_dict[(pair[1], pair[0])] + 2)%4)
            else:
                labels.append(-1)
        return np.asarray(labels)
    
