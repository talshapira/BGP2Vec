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

## Code & Dataset

* bgp2vec.py + oix_utils.py --> please use these files to train the BGP2Vec model. For this end you will have to download an oix file from http://archive.routeviews.org/oix-route-views/
* CAIDA....ipynb --> use this to train neural network for ToR predictions - for this you need to download the CAIDA as relationships data from https://publicdata.caida.org/datasets/as-relationships/

## Publications

* Tal Shapira and Yuval Shavitt. 2020. A Deep Learning Approach for IP Hijack Detection Based on ASN Embedding. In Proceedings of the Workshop on Network Meets AI & ML (NetAI ’20). Association for Computing Machinery, New York, NY, USA, 35–41. [Download paper here](https://dl.acm.org/doi/abs/10.1145/3405671.3405814)
* T. Shapira and Y. Shavitt, "Unveiling the Type of Relationship Between Autonomous Systems Using Deep Learning," NOMS 2020 - 2020 IEEE/IFIP Network Operations and Management Symposium, 2020, pp. 1-6, doi: 10.1109/NOMS47738.2020.9110358. [Download paper here](https://ieeexplore.ieee.org/document/9110358)
