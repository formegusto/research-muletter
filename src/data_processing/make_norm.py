import pandas as pd


def make_norm(features, reco_features):
    feature_cols = [features.columns[1:].values]

    norm_features = pd.concat(
        [features, reco_features], ignore_index=True).copy()
    for col in feature_cols:
        norm_features[col] = (norm_features[col] - norm_features[col].min()) / \
            (norm_features[col].max() - norm_features[col].min())

    norm_features.head()

    return norm_features
