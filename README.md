# BGP2VEC

We introduce a novel approach for Autonomous System (AS) embedding using deep learning based on only BGP announcments. Using these vectors we able to solve multiple important classification problem such as AS business types, AS Types of Relationship (ToR) and even IP hijack detection.  Similar to natural language processing (NLP) models, the embedding represents latent characteristics of the ASN and its interactions on the Internet.  The embedding coordinates of each AS are represented by a vector; thus, we call our method BGP2VEC.

<p align="center">
<img src='http://talshapira.github.io/files/ToR_Gao.png' width="400">
</p>

## Method

Our method works as follows: first, using a shallow neural network, we map each AS number (ASN) to an embedded vector. 

The training procedure is done by feeding the network with the ASN pairs; the input is a one-hot vector representing the input ASN and the training outputs, which are also one-hot vectors representing the output ASNs (the context ASNs). Then applying gradient descent learning to adjust the weights of the network in order to maximize the log probability of any context word given the input word.

<img src='http://talshapira.github.io/files/as_route_ngram_example_fixed.png'>

Then, for each task; AS classification or ToR classification task, we activate Artificial Neural Network (ANN) that receives the vectors from the previous stage.

<img src='http://talshapira.github.io/files/BGP2VEC_sys_0.png'>

## Exploration of ASN Embedding

BGP announcements hold latent information about the Internet Autonomous Systems (ASes) and their functional position within the Internet eco-system. This information can aid us in understanding the Internet structure and also in solving many practical problems. BGP2Vec,is a novel approach to revealing the latent characteristics of ASes using neural-network-based embedding. We show that our embedding indeed captures important characteristics of ASes, such as: distance from Tier-1, business type of AS, ToR, geographical similarity, etc.

<p align="center">
<img src='http://talshapira.github.io/files/BGP2Vec_Analysis_all_graph_by_region_1.png' width="400">
</p>


<p align="center">
<img src='http://talshapira.github.io/files/bgp2vec_equinix_vectors.png' width="400">
</p>


<p align="center">
<img src='http://talshapira.github.io/files/bgp2vec_siblings_analogies.png' width="400">
</p>

## Code & Dataset

* bgp2vec.py + oix_utils.py --> please use these files to train the BGP2Vec model. For this end you will have to download an oix file from http://archive.routeviews.org/oix-route-views/
* Generate_ToR_Dataset.ipynb - use this to convert the [CAIDA dataset](https://publicdata.caida.org/datasets/as-relationships/) to np arrays. Please be aware that there could be ASNs that are presented in the CAIDA dataset but not in [RouteView](http://archive.routeviews.org/oix-route-views/). So you have to find these ToRs and remove them for the next step.
* CAIDA....ipynb --> use this to train a neural network for ToR predictions - for this you need to download the CAIDA as relationships data from https://publicdata.caida.org/datasets/as-relationships/

## Publications

* T. Shapira and Y. Shavitt, "BGP2Vec: Unveiling the Latent Characteristics of Autonomous Systems," in IEEE Transactions on Network and Service Management, 2022, doi: 10.1109/TNSM.2022.3169638. [Download paper here](https://ieeexplore.ieee.org/document/9761992)
* T. Shapira and Y. Shavitt. 2020. A Deep Learning Approach for IP Hijack Detection Based on ASN Embedding. In Proceedings of the Workshop on Network Meets AI & ML (NetAI ’20). Association for Computing Machinery, New York, NY, USA, 35–41. [Download paper here](https://dl.acm.org/doi/abs/10.1145/3405671.3405814)
* T. Shapira and Y. Shavitt, "Unveiling the Type of Relationship Between Autonomous Systems Using Deep Learning," NOMS 2020 - 2020 IEEE/IFIP Network Operations and Management Symposium, 2020, pp. 1-6, doi: 10.1109/NOMS47738.2020.9110358. [Download paper here](https://ieeexplore.ieee.org/document/9110358)

# Check our new paper

AP2Vec: an Unsupervised Approach for BGP Hijacking Detection

In this paper, we extend the work done in BGP2Vec and introduce a novel approach for BGP hijacking detection that is based on the observation that during a hijack attack, the functional roles of ASNs along the route change. To identify a functional change, we build on previous work that embeds ASNs to vectors based on BGP routing announcements and embed each IP address prefix (AP) to a vector representing its latent characteristics, we call it AP2Vec. Then, we compare the embedding of a new route with the AP embedding that is based on the old routes to identify large differences.

* T. Shapira and Y. Shavitt, "AP2Vec: an Unsupervised Approach for BGP Hijacking Detection," in IEEE Transactions on Network and Service Management, doi: 10.1109/TNSM.2022.3166450. [Download paper here](https://ieeexplore.ieee.org/document/9754706)
