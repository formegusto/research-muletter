from web.KMeans import KMeans
from web.DataPreprocessing import make_norm
import pandas as pd
import datetime as dt
from pymongo import MongoClient as mc


class CoordGenerator:
    def __init__(self):
        mongo_uri = "mongodb://localhost:27017"
        self.conn = mc(mongo_uri).TestMuLetter
        self.seed_zone = self.conn.SeedZone
        self.mail_box = self.conn.MailBox
        self.cluster_zone = self.conn.ClusterZone

        print("Coord Generator Init :)")

    def make_new_cluster(self):
        _seed_features = self.seed_zone.find({}, {
            "_id": 0,
            "label": 0
        })
        seed_features = pd.DataFrame([_ for _ in _seed_features])
        self.seed_features = seed_features

        norm_info, norm_features = make_norm(seed_features, get_norm_info=True)
        self.norm_info = norm_info
        self.norm_features = norm_features

        kmeans = KMeans(
            datas=norm_features
        )
        kmeans.run(early_stop_cnt=5,
                   ecv_check_count=20)
        kmeans.sorting_ver_2()
        music_label = pd.DataFrame(norm_features['trackId'])
        music_label['label'] = kmeans.clusters
        self.music_label = music_label
        self.kmeans = kmeans

        _k_features = list()
        for k_pat in kmeans.K_pattern:
            _k_features.append(k_pat.tolist())

        # Save Cluster Info
        cluster_zone_doc = dict({
            "version": self.cluster_zone.estimated_document_count() + 1,
            "features": _k_features,
            "ecv": kmeans.ecv,
            "K": len(_k_features),
            "createdAt": dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        })
        self.cluster_zone.insert_one(cluster_zone_doc)

        for _, label_info in music_label.iterrows():
            track_id, label = label_info

            self.seed_zone.update_one({
                "track_id": track_id
            }, {
                "$set": {
                    "label": label
                }
            })
