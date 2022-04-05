from pymongo import MongoClient as mc
import pandas as pd
from bson import ObjectId


class DB:
    def __init__(self):
        mongo_uri = "mongodb://localhost:27017"
        self.conn = mc(mongo_uri).MuLetter
        self.mail_box = self.conn.MailBox
        self.mail = self.conn.Mail
        self.seed_zone = self.conn.SeedZone

    def regist_mail_box(self, sel_tracks):
        tracks = sel_tracks.copy()
        tracks.rename({"id": "track_id"}, axis=1, inplace=True)

        _tracks = list()
        cols = tracks.columns
        for track in tracks.values:
            _track = dict()

            for col_idx, _ in enumerate(track):
                _track[cols[col_idx]] = _

            _tracks.append(_track)

        mail_box = {
            "title": "Test",
            "tracks": _tracks
        }

        return self.mail_box.insert_one(mail_box)

    def new_mail_box_seed(self, mail_box_id, sel_tracks):
        tracks = sel_tracks.copy()
        tracks.rename({"id": "track_id"}, axis=1, inplace=True)

        _tracks = list()
        cols = tracks.columns

        for track in tracks.values:
            _track = dict()

            for col_idx, _ in enumerate(track):
                _track[cols[col_idx]] = _

            _tracks.append(_track)

        self.mail_box.update_one({
            "_id": ObjectId(mail_box_id)
        }, {
            "$addToSet": {"tracks": {"$each": _tracks}}
        })

    def new_mail(self, box_id, reco_tracks):
        tracks = reco_tracks.sample(frac=1).copy()
        tracks.rename({"id": "track_id"}, axis=1, inplace=True)

        _tracks = list()
        cols = tracks.columns
        for track in tracks.values:
            _track = dict()

            for col_idx, _ in enumerate(track):
                _track[cols[col_idx]] = _

            _tracks.append(_track)

        mail = {
            "$set": {
                "tracks": _tracks
            }
        }

        self.mail.update_one({"box_id": box_id}, mail)

    def observe_seed_zone(self, sel_features):
        features = sel_features.copy()
        features.rename({"id": "track_id"}, axis=1, inplace=True)

        _features = list()
        cols = features.columns
        for track in features.values:

            _track = dict()

            for col_idx, _ in enumerate(track):
                _track[cols[col_idx]] = _

            res = self.seed_zone.find_one({
                "track_id": _track['track_id']
            })

            if res is None:
                _features.append(_track)

        if len(_features) != 0:
            self.seed_zone.insert_many(_features)

    def regist_mail(self, box_id, reco_tracks):
        tracks = reco_tracks.copy()
        tracks.rename({"id": "track_id"}, axis=1, inplace=True)

        _tracks = list()
        cols = tracks.columns
        for track in tracks.values:
            _track = dict()

            for col_idx, _ in enumerate(track):
                _track[cols[col_idx]] = _

            _tracks.append(_track)

        mail = {
            "box_id": box_id,
            "tracks": _tracks
        }

        return self.mail.insert_one(mail)

    def get_mail_box(self, box_id):
        _mail_box_db_datas = self.mail_box.find_one({
            "_id": ObjectId(box_id)
        })
        _tracks = _mail_box_db_datas['tracks']

        cols = list(_tracks[0].keys())
        tracks = list()

        for track in _tracks:
            tracks.append(list(
                track.values())
            )

        return pd.DataFrame(tracks, columns=cols).rename({"track_id": "id"}, axis=1)

    def get_mail(self, box_id):
        _reco_db_datas = self.mail.find_one({
            "box_id": box_id
        })
        _reco_tracks = _reco_db_datas['tracks']

        cols = list(_reco_tracks[0].keys())
        tracks = list()

        for track in _reco_tracks:
            tracks.append(list(
                track.values())
            )

        return pd.DataFrame(tracks, columns=cols).rename({"track_id": "id"}, axis=1)
