import pandas as pd


def make_norm(features, reco_features=None, get_norm_info=False):
    norm_info = dict()
    feature_cols = [features.columns[1:].values]

    if reco_features is None:
        norm_features = features.copy()
    else:
        norm_features = pd.concat(
            [features, reco_features], ignore_index=True).copy()
    for col in feature_cols[0]:
        _min = norm_features[col].min()
        _max = norm_features[col].max()
        norm_info[col] = {
            "min": _min,
            "max": _max
        }
        norm_features[col] = (norm_features[col] - _min) / \
            (_max - _min)

    if get_norm_info:
        return norm_info, norm_features
    else:
        return norm_features
