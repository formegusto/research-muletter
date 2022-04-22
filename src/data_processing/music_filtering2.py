import pandas as pd
import numpy as np


def music_filtering2(sel_tracks, norm_features, kmeans):
    # music filtering
    ids = norm_features['id'].values
    sel_ids = sel_tracks['id'].values

    labels = kmeans.labels_

    cluster_info = pd.DataFrame(np.column_stack(
        [ids, labels]), columns=['id', 'label'])
    cluster_info.set_index("id", inplace=True)

    sel_cluster_info = cluster_info.loc[sel_ids]

    cluster_info.drop(sel_ids, inplace=True)
    sel_labels = np.unique(sel_cluster_info['label'])
    reco_ids = np.array([])

    for label in sel_labels:
        filtering = cluster_info[cluster_info['label'] == label].index.values
        reco_ids = np.append(reco_ids, filtering)

    return reco_ids
