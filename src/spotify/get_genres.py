import pandas as pd
import requests as req
from urllib.parse import urlencode


def get_genres(token, sel_tracks):
    artists_uri = "https://api.spotify.com/v1/artists"

    ids = ""
    for artist_id in sel_tracks['artists id']:
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

    res = req.get("{}?{}".format(artists_uri, query), headers=headers)

    result = res.json()

    artists = result['artists']
    genres = pd.DataFrame(columns=['count'])

    for artist in artists:
        _genres = artist['genres']

        for genre in _genres:
            if genre in genres.index:
                genres.loc[genre]['count'] += 1
            else:
                genres.loc[genre] = 1

    return genres.sort_values(by=['count'], ascending=False)
