from cProfile import label
import math as mt
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances as euc

import matplotlib
import matplotlib.pyplot as plt


@property
def tss(self):
    _mean = self.datas.mean(axis=0)
    _mean = np.expand_dims(_mean, axis=0)

    return (euc(_mean, self.datas) ** 2).sum()


@property
def wss(self):
    wss = 0

    for c_id in range(self.K):
        cluster = np.expand_dims(self.clusters_[c_id], axis=0)
        datas = self.datas[self.labels_ == c_id]

        wss += (euc(cluster, datas) ** 2).sum()

    return wss


@property
def ecv(self):
    return 1 - (self.wss / self.tss)


class KMeans2:
    def __init__(self, features, K=None):
        self.cols = features.columns[1:].values
        self.datas = features.values[:, 1:]

        if K is None:
            self.K = round(mt.sqrt(len(features) / 2))
        else:
            self.K = K

    def init_setting(self):
        datas = self.datas.copy()

        _clusters = datas[np.random.randint(len(datas))]
        _clusters = np.expand_dims(_clusters, axis=0)

        for c_id in range(self.K - 1):
            dist = euc(datas, _clusters).min(axis=1)
            next_centroid = datas[dist.argmax(), :]
            _clusters = np.append(_clusters, [next_centroid], axis=0)

        self.labels_ = np.zeros(self.K) - 1
        self.clusters_ = _clusters

    def move_centroid(self):
        datas = self.datas
        labels = self.labels_
        clusters = self.clusters_

        for c_id in range(self.K):
            _datas = datas[labels == c_id]
            clusters[c_id] = _datas.mean(axis=0)

        self.clusters_ = clusters

    def next(self):
        self.labels_ = euc(self.datas, self.clusters_).argmin(axis=1)
        self.move_centroid()

        print("ECV {}%".format(round(self.ecv * 100)))

    def fit(self, early_stop_cnt=3):
        self.init_setting()
        _early_stop_cnt = 0
        while True:
            bak_label = self.labels_.copy()
            self.next()

            if np.array_equiv(bak_label, self.labels_):
                _early_stop_cnt += 1

            if _early_stop_cnt == early_stop_cnt:
                break

    def all_plot(self):
        matplotlib.rc('font', family='AppleGothic')
        plt.rcParams['axes.unicode_minus'] = False

        plt.figure(figsize=(16, 4))

        plt.plot(self.cols, self.datas.T, color='g',
                 linewidth=0.05, label="데이터")
        plt.plot(self.cols, self.clusters_.T,
                 color='g', linewidth=0.5, label="클러스터")

        plt.show()

    def cluster_plot(self):
        COL_SIZE = 4

        datas = self.datas
        clusters = self.clusters_
        labels = self.labels_
        K = self.K

        r = mt.floor((K - 1) / COL_SIZE) + 1
        plt.figure(figsize=(20, COL_SIZE*r))

        for ax_idx in range(r * COL_SIZE):
            ax = plt.subplot(r, COL_SIZE, ax_idx + 1)

            if ax_idx >= K:
                ax.set_visible(False)
            else:
                _cluster = clusters[ax_idx]
                _datas = datas[labels == ax_idx]

                ax.plot(_datas.T, c='g', linewidth=0.4)
                ax.plot(_cluster, c='b', linewidth=1)
                ax.text(0.02, 0.925, "{}번 클러스터".format(ax_idx),
                        ha="left",
                        va="center",
                        transform=ax.transAxes,
                        fontsize=8,
                        )

        plt.show()


KMeans2.tss = tss
KMeans2.wss = wss
KMeans2.ecv = ecv
