from collections import defaultdict
import numpy as np
import sys
import pickle
from sklearn.model_selection import train_test_split
from collections import Counter
import random

np.random.seed(7)

# Define parameters and load bgp_routes and ToR datasets

ToR_MODEL_NAME = "CAIDA_s1_ToR_Classification_SARK"

TEST_SIZE = 0.2
TOR_LABELS_DICT = {'P2P':0, 'C2P': 1,'P2C': 2}
class_names = ['P2P', 'C2P', 'P2C']
DATA_PATH = '../../Data/'
MODELS_PATH = '../../Models/'
RESULTS_PATH = '../../Results/'


    
class SARK:
    TOR_ORIG_LABELS_DICT = {'P2P':0, 'C2P': 1,'Siblings': 2, 'P2C': 3}
    
    def __init__(self, routing_tables, delta_0=3, delta_1=2):
        self.P_splitted_by_vantages = self.__split_P_by_vantages(routing_tables)
        self.N = len(self.P_splitted_by_vantages)
        print(self.N)
        self.delta_0 = delta_0
        self.delta_1 = delta_1
        
        self.ranking = self.__get_ranking_vector()
        self.pairs_list = self.__get_pairs_list(routing_tables)
        self.tor_dict = self.__get_tor()
        with open(MODELS_PATH + ToR_MODEL_NAME + '_tor_dict.pickle', 'wb') as handle:
            pickle.dump(self.tor_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def __split_P_by_vantages(self, P):
        P_splitted_by_vantages = defaultdict(list)
        for route in P:
            P_splitted_by_vantages[route[0]].append(route)
        return P_splitted_by_vantages
    
    
    def __get_graph_for_vantage(self, P_v):
        edges = []
        vertecs = []
        for route in P_v:
            for edge in zip(route[:-1], route[1:]):
                edges.append(edge)
            vertecs +=  route
        return set(vertecs), set(edges)
    
    
    def __get_leaves(self, edges):
        e_vertecs = set()
        m_vertecs = set()
        vertecs_dict = defaultdict(set)
        for edge in edges:
            e_vertecs.add(edge[1])
            m_vertecs.add(edge[0])
            vertecs_dict[edge[1]].add(edge)
            vertecs_dict[edge[0]].add(edge)

        return list(e_vertecs - m_vertecs), vertecs_dict
            
    
    def __remove_leaves_edges(self, edges, leaves, vertecs_dict):
        for leave in leaves:
            edges = edges - vertecs_dict[leave]
        return edges
    
    def __get_ranking_for_vantage_garaph(self, P_v):
        rank = dict()
        r = 1
        vertecs, edges = self.__get_graph_for_vantage(P_v)
        leaves, vertecs_dict = self.__get_leaves(edges)
        
        while len(leaves) > 0:
            print("Start Iteration on " + str(len(leaves)) + " Leaves")
            for leaf in leaves:
                rank[leaf] = r
            r += 1
            edges = self.__remove_leaves_edges(edges, leaves, vertecs_dict)
            print("Number of remaining edges: " + str(len(edges)))
            leaves, vertecs_dict = self.__get_leaves(edges)
            print("Number of leaves: " + str(len(leaves)))
            print()
        
        for v in vertecs:
            if v not in rank:
                rank[v] = r
        
        return rank
            
        
    def __get_ranking_vector(self):
        def intialize_ranking_vector():
            return [0]*self.N
        
        ranking_vector = defaultdict(intialize_ranking_vector)
        for i, vantage in enumerate(self.P_splitted_by_vantages):
            print('Working on vantage number ' + str(i))
            rank = self.__get_ranking_for_vantage_garaph(self.P_splitted_by_vantages[vantage])
            for v in rank:
                ranking_vector[v][i] = rank[v]
            print('Finished __get_ranking_for_vantage_garaph number ' + str(i))
#             with open(MODELS_PATH + ToR_MODEL_NAME + '_ranking_vector_' + str(i) + '.pickle', 'wb') as handle:
#                 pickle.dump(ranking_vector, handle, protocol=pickle.HIGHEST_PROTOCOL)
  
        return ranking_vector
            
        
    def __get_pairs_list(self, P):
        pairs_list = []
        for route in P:
            for edge in zip(route[:-1], route[1:]):
                pairs_list.append(edge)
        return list(set(pairs_list))
        
    
    def __get_tor(self):
        tor_dict = dict()
        for pair in self.pairs_list:
            v0_ranking = self.ranking[pair[0]]
            v1_ranking = self.ranking[pair[1]]
            e_0_1 = sum([1 for i in range(self.N) if (v0_ranking[i] != 0 and v0_ranking[i] == v1_ranking[i])])
            l_0_1 = sum([1 for i in range(self.N) if v0_ranking[i] > v1_ranking[i]])
            l_1_0 = sum([1 for i in range(self.N) if v1_ranking[i] > v0_ranking[i]])
            
            if e_0_1 > self.N/2.0:
                tor_dict[pair] = 0
            elif l_1_0*l_0_1 > 0 and 1.0/self.delta_1 <= 1.0*l_0_1/l_1_0 <= self.delta_1:
                tor_dict[pair] = 0
            elif l_0_1 > self.N/2.0 and l_1_0 == 0:
                tor_dict[pair] = 3
            elif l_1_0 > self.N/2.0 and l_0_1 == 0:
                tor_dict[pair] = 1
            elif l_1_0 == 0 or 1.0*l_0_1/l_1_0 > self.delta_0:
                tor_dict[pair] = 3
            elif l_0_1 == 0 or 1.0*l_1_0/l_0_1 > self.delta_0:
                tor_dict[pair] = 1
        return tor_dict
                
        
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


if __name__ == "__main__":

    
    bgp_routes = np.load(DATA_PATH + "bgp_routes_dataset.npy")
    bgp_routes_labels = np.load(DATA_PATH + "bgp_routes_labels.npy")
    print(bgp_routes.shape, bgp_routes_labels.shape)

    DATA = "caida_s1_tor"
    tor_dataset = np.load(DATA_PATH + DATA + "_dataset.npy")
    tor_labels = np.load(DATA_PATH + DATA + "_labels.npy")

    print(tor_dataset.shape, tor_labels.shape)

    from sklearn.utils import shuffle
    dataset, labels = shuffle(tor_dataset, tor_labels, random_state=7)

    x_training, x_test, y_training, y_test = train_test_split(dataset, labels, test_size=TEST_SIZE)

    del dataset, labels

    sark = SARK(bgp_routes)
    
    with open(MODELS_PATH + ToR_MODEL_NAME + '_tor_dict.pickle', 'wb') as handle:
        pickle.dump(sark.tor_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
            
    y_test_prediction = sark.generate_labels_for_set(x_test)
    with open(MODELS_PATH + ToR_MODEL_NAME + '_y_test_prediction.pickle', 'wb') as handle:
        pickle.dump(y_test_prediction, handle, protocol=pickle.HIGHEST_PROTOCOL)