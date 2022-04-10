from web import DB, Spotify
import pandas as pd


class Recommender:
    def __init__(self, _id):
        self.mail_box_id = _id
        self.db = DB()

    def init_setting(self):
        self.db.get_mailbox(_obj_id=self.mail_box_id)

        _sel_tracks = self.db.tracks
        _sel_tracks = pd.DataFrame(_sel_tracks)
        sel_tracks = _sel_tracks[_sel_tracks.columns.difference(["_id"])]

        spotify = Spotify(sel_tracks)
        spotify.get_genres
        spotify.get_features()
        spotify.get_reco_tracks
        spotify.get_features(target="reco")

        self.spotify = spotify

        print("[ML Program] Spotify Setting Okay :)")
