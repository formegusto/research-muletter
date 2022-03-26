import numpy as np
import math as mt
from sklearn.metrics.pairwise import euclidean_distances as euc
import random as ran
import pandas as pd


def tss(mean_pattern, df):
    A = np.expand_dims(mean_pattern.values, axis=0)
    tss = 0
    for idx in df.index:
        B = np.expand_dims(df.loc[idx].values, axis=0)
        tss += euc(
            B,
            A
        )[0][0] ** 2
    return tss


class KMeans:
    def __init__(self, datas):
        self.datas = datas.set_index("id")
        self.init_setting()

    def init_setting(self):
        datas_cnt = len(self.datas)

        self.K = round(mt.sqrt(datas_cnt / 2))

        mean_pattern = np.expand_dims(self.datas.mean().values, axis=0)
        norm_pattern = self.datas.values

        # TSS Logic
        self.tss = (euc(mean_pattern, norm_pattern) ** 2).sum()

    def run(self, early_stop_cnt=3):
        ecv_check = 0
        _round = 0
        _early_stop_cnt = 0

        prev_clusters = None
        K_pattern = None
        datas = self.datas.copy()
        idxes = datas.index

        while True:
            clusters = np.array([])
            # 초기 K 셋팅
            if _round == 0:
                init_K = np.array([])
                K_pattern = np.array([])
                datas_cnt = len(self.datas)

                while len(init_K) < self.K:
                    _K = ran.randrange(0, datas_cnt)
                    idx = idxes[int(_K)]
                    pattern = datas.loc[idx].values

                    if (_K not in init_K):
                        init_K = np.append(init_K, _K)
                        K_pattern = np.append(
                            K_pattern,
                            pattern
                        )
                r, c = datas.shape
                K_pattern = K_pattern.reshape(-1, c)

            for idx in datas.index:
                _pat = datas.loc[idx].values
                # euclidean distance based
                if _pat.ndim == 2:
                    _pat = _pat[0]
                _pat = np.expand_dims(_pat, axis=0)
                cluster = euc(_pat, K_pattern).argmin()
                clusters = np.append(clusters, cluster).astype("int")

                # improved similarity based
#                 cluster = np.array(
#                     [improved_similarity(_, _pat, w) for _ in K_pattern]
#                 ).argmax()
#                 clusters = np.append(clusters, cluster).astype("int")

            label_info = pd.DataFrame(clusters, columns=['label'])
            label_info.index = idxes

            wss = 0
            for label in range(0, self.K):
                cluster_in_idxes = label_info[
                    label_info['label'] == label
                ].index
                cluster_pat = np.expand_dims(
                    K_pattern[label],
                    axis=0
                )
                pattern = datas.loc[cluster_in_idxes].values
                wss += (euc(pattern, cluster_pat) ** 2).sum()

            ecv = (1 - (wss / self.tss)) * 100

            print("{} round : ECV {}%".format(
                _round + 1, round(ecv * 100) / 100))

            if _early_stop_cnt != early_stop_cnt:
                if ecv < 80:
                    if ecv_check == ecv:
                        _early_stop_cnt += 1
                    ecv_check = ecv
                    _round += 1
                    # K 조정
                    for label in range(0, self.K):
                        cluster_in_idxes = label_info[
                            label_info['label'] == label
                        ].index
                        pattern = datas.loc[cluster_in_idxes].values.mean(
                            axis=0)
                        K_pattern[label] = pattern
                    continue
                else:
                    self.K_pattern = K_pattern
                    self.clusters = clusters
                    print("Clustering End.")
                    break
            else:
                self.K_pattern = K_pattern
                self.clusters = clusters
                print("Clustering End.")
                break
