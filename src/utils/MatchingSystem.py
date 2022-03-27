import pandas as pd


class MatchingSystem:
    def __init__(self, norm_features, kmeans):
        music_label = pd.DataFrame(norm_features['id'])
        music_label['label'] = kmeans.clusters
        music_label.rename({"id": "track_id"}, axis=1, inplace=True)

        self.music_label = music_label
