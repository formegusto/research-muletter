import requests as req
from functools import reduce
from urllib.parse import urlencode
import pandas as pd


def direct_sel(token, id):
    search_uri = "https://api.spotify.com/v1/tracks/{}".format(id)

    query = urlencode({
        "market": "KR"
    })

    headers = {
        "authorization": "Bearer {}".format(token['access_token'])
    }

    res = req.get("{}?{}".format(search_uri, query), headers=headers)

    item = res.json()

    _id = item["id"]
    _name = item["name"]

    artist_list = item['album']['artists']
    artists = reduce(
        lambda acc, cur: cur[1]['name'] if cur[0] == 0 else acc +
        "," + cur[1]['name'],
        enumerate(artist_list),
        ""
    )
    artists_id = reduce(
        lambda acc, cur: cur[1]['id'] if cur[0] == 0 else acc +
        "," + cur[1]['id'],
        enumerate(artist_list),
        ""
    )

    _row = pd.Series({
        "id": _id,
        "name": _name,
        # "artists": artists_id,
        # "artists_name": artists
        "artists": artists_id.split(",")[0],
        "artists_name": artists.split(",")[0],
    })

    return _row
