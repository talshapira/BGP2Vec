from gensim.models import Word2Vec
import multiprocessing
import logging
import os
import numpy as np
import random
random.seed(7)

from oix_utils import *

try:
    print('PYTHONHASHSEED', os.environ['PYTHONHASHSEED'])
except:
    print("Warning! PYTHONHASHSEED is not defined")

# Note that for a fully deterministically-reproducible run, you must also limit the model to a single worker thread (workers=1), to eliminate ordering jitter from OS thread scheduling.


class BGP2VEC:
    def __init__(self, model_path, oix_path=None, rewrite=False, embedding_size=32, negative=5, epochs=3, window=2,
                 shuffle=True, word_fq_dict=None, mode=None, test_limit=None, asn_list=None, ap_list=None):

        self.model_path = model_path
        self.model = None
        self.embedding_size = embedding_size
        self.word_fq_dict = word_fq_dict

        if rewrite or not self.import_model():
            logging.info(("Start generating BGP2VEC model for ", oix_path))
            self.routes = get_routes_from_oix(oix_path, by_vantage=False, mode=mode, test_limit=test_limit,
                                              asn_list=asn_list, ap_list=ap_list)
            if shuffle:
                random.shuffle(self.tagged_routes)
            self.build_model(embedding_size, window, negative, epochs)
            self.export_model()

    def build_model(self, embedding_size, window, negative, epochs):
        self.model = Word2Vec(size=embedding_size, min_count=1, window=window, sg=1, hs=0, negative=negative,
                              workers=1, iter=1, seed=7)
        if self.word_fq_dict:
            self.model.build_vocab_from_freq(self.word_fq_dict)
        else:
            self.model.build_vocab(self.routes, progress_per=1000000)
        logging.info(("Vocabulary size:", len(self.model.wv.vocab)))

        logging.info("Start training model")
        self.model.train(self.routes, total_examples=len(self.routes), epochs=epochs, report_delay=30)

    def export_model(self):
        self.model.save(self.model_path)
        logging.info(('Exported:', self.model_path))

    def import_model(self):
        if os.path.exists(self.model_path):
            self.model = Word2Vec.load(self.model_path)
            logging.info(('Imported:', self.model_path))
            return True
        else:
            logging.info(("No exist:", self.model_path))
            return False

    def asn2idx(self, asn):
        return self.model.wv.vocab[asn].index

    def idx2asn(self, idx):
        return self.model.wv.index2word[idx]

    def asn2vec(self, asn):
        return self.model.wv.__getitem__(asn)

    def vec2asn(self, vec):
        return self.model.wv.similar_by_vector(vec, topn=1)[0][0]

    def routes_asn2idx(self, routes, max_len):
        routes_idx = np.zeros([len(routes), max_len], dtype=np.int32)

        for i, route in enumerate(routes):
            for t, asn in enumerate(route):
                routes_idx[i, t] = self.asn2idx(asn)
        return routes_idx

    def asns_asn2vec(self, asns):
        asns_vec = np.zeros([len(asns), self.embedding_size])

        for i, asn in enumerate(asns):
            asns_vec[i, :] = self.asn2vec(asn)

        return asns_vec
