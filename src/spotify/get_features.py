import pandas as pd
import requests as req
from urllib.parse import urlencode


def get_features(token, sel_tracks):
    features_uri = "https://api.spotify.com/v1/audio-features"

    ids = ""
    for artist_id in sel_tracks['id']:
        split_data = artist_id.split(",")

        for _ in split_data:
            ids += "{},".format(_)

    ids = ids[:-1]

    query = urlencode({
        "ids": ids
    })
    headers = {
        "authorization": "Bearer {}".format(token['access_token'])
    }

    res = req.get("{}?{}".format(features_uri, query), headers=headers)

    result = res.json()

    target_cols = ['id', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                   'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']

    features = pd.DataFrame(result['audio_features'])[target_cols]

    return features
