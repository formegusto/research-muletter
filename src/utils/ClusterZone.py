from pymongo import MongoClient as mc
import pandas as pd
from src.utils import KMeans
from src.data_processing import make_norm


class ClusterZone:
    def __init__(self):
        mongo_uri = "mongodb://localhost:27017"
        self.conn = mc(mongo_uri).MuLetter
        self.seed_zone = self.conn.SeedZone
        self.cluster_zone = self.conn.ClusterZone

    def restore(self):
        _seed_features = self.seed_zone.find({})

        seed_features = pd.DataFrame([_ for _ in _seed_features])

        seed_features.drop(["_id"], axis=1, inplace=True)
        seed_features.rename({"track_id": "id"}, axis=1, inplace=True)

        _labels = seed_features['label'].values
        seed_features.drop(["label"], axis=1, inplace=True)
        self.seed_features = seed_features

        print("Seed Zone Restore Success.")
        norm_features = make_norm(seed_features)
        self.norm_features = norm_features

        k_info = pd.DataFrame([_ for _ in self.cluster_zone.find({})])

        k_info.sort_values(by=['label'], inplace=True)
        k_info.drop(["_id", "label"], axis=1, inplace=True)

        kmeans = KMeans(
            datas=norm_features
        )
        kmeans.clusters = _labels
        kmeans.K_pattern = k_info.values
        print("Cluster Zone Restore Success.")

        self.kmeans = kmeans
