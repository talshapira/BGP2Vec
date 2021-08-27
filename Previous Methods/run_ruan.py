from collections import defaultdict
import numpy as np
import sys
import pickle
from sklearn.model_selection import train_test_split
from collections import Counter
import random
import networkx as nx

np.random.seed(7)

# we'll use infinity as a default distance to nodes.
inf = float('inf')


# TIER1= [7018, 209, 3356, 3549, 4323, 3320, 3257, 286, 6830, 2914, 5511, 3491, 1239, 6453, 6762, 12956, 701, 702, 703, 2828, 6461]
TIER1 = ["174", "209", "286", "701", "1239", "1299", "2828", "2914", "3257", "3320", "3356",
         "3491", "5511", "6453", "6461", "6762", "6830", "7018", "12956"]
    
class Ruan:
    TOR_ORIG_LABELS_DICT = {'P2P':0, 'C2P': 1,'Siblings': 2, 'P2C': 3}

    def __init__(self, routing_tables, ASN_list):
        self.TIER1 = TIER1
        self.s1_cnt = self.__count_as_in_s1(routing_tables)
        print("Finished __count_as_in_s1")
        self.tor_dict = self.__get_s1_tor()
        print("Finished __get_s1_tor")
        self.S2 = self.__get_S2(routing_tables)
        print("Finished __get_S2")
        self.graph = nx.Graph()
        self.graph.add_edges_from(self.__get_pairs_list(routing_tables))
        print("Finished __get_pairs_list and creating graph")
        self.distances = self.__calcultae_distances_from_tier1(routing_tables, ASN_list)
        print("Finished __calcultae_distances_from_tier1")
        self.s2_cnt, self.s2_top_providers = self.__count_as_in_s2()
        print("Finished __count_as_in_s2")
        self.__get_s2_tor()
        print("Finished __get_s2_tor")
    
    def __count_as_in_s1(self, P):
        cnt = defaultdict(lambda:0)
        for route in P:
            for j, asn in enumerate(route):
                if asn in self.TIER1:
                    for i in range(1, j+1):
                        cnt[(route[i],route[i-1])] += 1
                    for i in range(j, len(route)-1):
                        cnt[(route[i],route[i+1])] += 1
                    break
        return cnt

    
    def __get_s1_tor(self):
        tor_dict = dict()
        for pair in self.s1_cnt:
            if self.s1_cnt[pair] > 0 and (pair[1], pair[0]) not in self.s1_cnt:
                tor_dict[pair] = 3
                tor_dict[(pair[1], pair[0])] = 1
            elif self.s1_cnt[pair] > 0 and self.s1_cnt[(pair[1], pair[0])] > 0:
                if pair[0] in self.TIER1 or pair[1] in self.TIER1:
                    tor_dict[pair] = 0
                    tor_dict[(pair[1], pair[0])] = 0
                else:
                    tor_dict[pair] = 2
                    tor_dict[(pair[1], pair[0])] = 2
                    
        return tor_dict
    
    
    def __get_S2(self, P):
        S2 = []
        for path in P:
            for asn in path:
                if asn not in self.tor_dict:
                    S2.append(path)
                    break
        return S2
    
    
    def __get_pairs_list(self, P):
        pairs_list = []
        for route in P:
            for edge in zip(route[:-1], route[1:]):
                pairs_list.append(edge)
        return list(set(pairs_list))
    
    
#     def __get_distance_from_Tier1(self, vertex):
#         min_distance = inf
#         for tier1_as in self.TIER1:
#             min_distance = min(min_distance, len(self.graph.dijkstra(vertex, tier1_as)))
#         return min_distance
    
    
    def __get_best_path_from_Tier1(self, vertex):
        min_distance = inf
        best_path = []
        for tier1_as in self.TIER1:
            path = nx.shortest_path(self.graph,source=vertex,target=tier1_as)
            if len(path) < min_distance:
                min_distance = len(path)
                best_path = path
                
        return best_path
    
    
    def __calcultae_distances_from_tier1(self, P, vertecs):
#         vertecs = set()
        distances = dict()
#         for i, route in enumerate(P):
#             for asn in route:
#                 vertecs.add(asn)
        print("Number of vertecs " + str(len(vertecs)))
        for i, vertex in enumerate(vertecs):
            if i%1000 ==0:
                print(i)
            if vertex not in distances:
                path = self.__get_best_path_from_Tier1(vertex)
                for i in range(len(path)):
                    distances[path[i]] = len(path) - i
        return distances
    
    def __find_top_provider_ind(self, path):
        distances = list() 
        for asn in path:
            distances.append(self.distances[asn])
        
        distances = np.arange(len(distances))[distances == np.min(distances)]
        if len(distances) == 1:
            return distances[0]
        else:
            distances = distances[::-1]
            for i in range(1, len(distances)):
                if distances[i-1] - distances[i] > 1:
                    return distances[i-1]
            return distances[-1]
                             
    
    def __count_as_in_s2(self):
        cnt = defaultdict(lambda:0)
        top_providers = list()
        for i, route in enumerate(self.S2):
            if i%100000 == 0:
                print(i)
            j = self.__find_top_provider_ind(route)
            top_providers.append(j)
            for i in range(1, j+1):
                if (route[i],route[i-1]) not in self.tor_dict:
                    cnt[(route[i],route[i-1])] += 1
            for i in range(j, len(route)-1):
                if (route[i],route[i+1]) not in self.tor_dict:
                    cnt[(route[i],route[i+1])] += 1
        return cnt, top_providers                  
                               
    
    def __get_s2_tor(self):
        tor_dict_s2 = dict()                 
        for pair in self.s2_cnt:
            if self.s2_cnt[pair] > 0 and (pair[1], pair[0]) not in self.s2_cnt:
                tor_dict_s2[pair] = 3
                tor_dict_s2[(pair[1], pair[0])] = 1
            elif self.s2_cnt[pair] > 0 and self.s2_cnt[(pair[1], pair[0])] > 0:
                tor_dict_s2[pair] = 0
                tor_dict_s2[(pair[1], pair[0])] = 0
        for i, path in enumerate(self.S2):
            j = self.s2_top_providers[i]
            if j > 1 and (path[j-2], path[j-1]) in tor_dict_s2 and tor_dict_s2[(path[j-2], path[j-1])] == 0:
                tor_dict_s2[(path[j-2], path[j-1])] == 2
                tor_dict_s2[(path[j-1], path[j-2])] == 2
            if j + 2 < len(path) and (path[j+1], path[j+2]) in tor_dict_s2 and tor_dict_s2[(path[j+1], path[j+2])] == 0:
                tor_dict_s2[(path[j+1], path[j+2])] == 2 
                tor_dict_s2[(path[j+2], path[j+1])] == 2              
        
        self.tor_dict.update(tor_dict_s2) 
                               
                               
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
    # Define parameters and load bgp_routes and ToR datasets

    ToR_MODEL_NAME = "Orig_ToR_Classification_SARK"

    TEST_SIZE = 0.2
    TOR_ORIG_LABELS_DICT = {'P2P':0, 'C2P': 1,'Siblings': 2, 'P2C': 3}
    class_names = ['P2P', 'C2P','Siblings', 'P2C']
    DATA_PATH = '../Data/'
    MODELS_PATH = '../Models/'
    RESULTS_PATH = '../Results/'

    with open(DATA_PATH + 'ASN_index_map.pickle', 'rb') as handle:
        ASN_index_map = pickle.load(handle)
    bgp_routes = np.load(DATA_PATH + "bgp_routes_indexed_dataset.npy")
    bgp_routes_labels = np.load(DATA_PATH + "bgp_routes_labels.npy")
    print(bgp_routes.shape, bgp_routes_labels.shape)

    tor_dataset = np.load(DATA_PATH + "tor_dataset_indexed_orig_cleaned.npy")
    tor_labels = np.load(DATA_PATH + "tor_labels_indexed_orig_cleaned.npy")
    print(tor_dataset.shape, tor_labels.shape)

    from sklearn.utils import shuffle
    dataset, labels = shuffle(tor_dataset, tor_labels, random_state=7)

    x_training, x_test, y_training, y_test = train_test_split(dataset, labels, test_size=TEST_SIZE)

    del dataset, labels

    ruan = Ruan(bgp_routes, ASN_index_map)
    with open(MODELS_PATH + ToR_MODEL_NAME + '_tor_dict.pickle', 'wb') as handle:
        pickle.dump(ruan.tor_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    y_test_prediction = ruan.generate_labels_for_set(x_test)
    with open(MODELS_PATH + ToR_MODEL_NAME + '_y_test_prediction.pickle', 'wb') as handle:
        pickle.dump(y_test_prediction, handle, protocol=pickle.HIGHEST_PROTOCOL)