import pandas as pd
import requests as req
from urllib.parse import urlencode
import math as mt


def get_genres(token, sel_tracks):
    artists_uri = "https://api.spotify.com/v1/artists"

    cnt = mt.floor((len(sel_tracks) - 1) / 50) + 1
    genres = pd.DataFrame(columns=['count'])

    _ids = ""
    for artist_id in sel_tracks['artists']:
        split_data = artist_id.split(",")

        for _ in split_data:
            _ids += "{},".format(_)

    _ids = _ids[:-1].split(",")

    for _cnt in range(0, cnt):
        ids = ""
        for artist_id in _ids[_cnt * 50: (_cnt + 1) * 50]:
            ids += "{},".format(artist_id)

        ids = ids[:-1]
        query = urlencode({
            "ids": ids
        })
        headers = {
            "authorization": "Bearer {}".format(token['access_token'])
        }

        res = req.get("{}?{}".format(artists_uri, query), headers=headers)

        result = res.json()
        artists = result['artists']

        for artist in artists:
            _genres = artist['genres']

            for genre in _genres:
                if genre in genres.index:
                    genres.loc[genre]['count'] += 1
                else:
                    genres.loc[genre] = 1

    get_available_genres_uri = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    res = req.get(get_available_genres_uri, headers=headers)
    result = res.json()

    genres = genres[[_ in result['genres'] for _ in genres.index.values]]

    return genres.sort_values(by=['count'], ascending=False)
