import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math as mt


def visual_cluster_data(sel_tracks, kmeans):
    matplotlib.rc('font', family='AppleGothic')
    plt.rcParams['axes.unicode_minus'] = False

    plot_r, plot_c = 1 * mt.ceil(kmeans.K / 4), 4
    fig, ax = plt.subplots(plot_r, plot_c, figsize=(16, 3 * plot_r))
    sel_tracks_ids = sel_tracks['id'].values
    r, c = ax.shape

    label_info = pd.DataFrame(kmeans.clusters, columns=['label'])
    label_info.index = kmeans.datas.index

    for _r in range(0, r):

        for _c in range(0, c):
            label = _r * 4 + _c
            if label < kmeans.K:
                cluster_in_idxes = label_info[
                    label_info['label'] == label
                ].index

                Mem_patterns = kmeans.datas.loc[cluster_in_idxes].T.values
                in_sel = False

                # 사용자가 선택했던 음악이 군집에 속해있는지 확인
                for chk_id in cluster_in_idxes:
                    if chk_id in sel_tracks_ids:
                        in_sel = True

                ax[_r][_c].plot(
                    Mem_patterns, color='b' if in_sel else 'g', linewidth=0.15)
                ax[_r][_c].text(0.02, 0.925, "{}번 클러스터".format(label + 1),
                                ha="left",
                                va="center",
                                transform=ax[_r][_c].transAxes,
                                fontsize=8,
                                )
            else:
                ax[_r][_c].axis("off")

    plt.show()
