import pandas as pd
import numpy as np
import requests as req
from urllib.parse import urlencode
from functools import reduce


def get_recommend(sel_tracks, features, genres, token, og=None):
    seed_info = pd.merge(left=sel_tracks, right=features, how='inner', on='id')

    del seed_info['artists']
    del seed_info['name']
    seed_info.rename(columns={"artists id": "artists",
                              "id": "tracks"}, inplace=True)

    _genres = genres.index[:5].values
    seed_genres = reduce(lambda acc, cur: acc + cur + ",", _genres, "")
    seed_genres = seed_genres[:-1]

    # target cols 13 (except popularity)
    feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                    'key', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
    target_cols = list()
    rename_cols = dict()

    for col in feature_cols:
        target_col = "target_{}".format(col)
        rename_cols[col] = target_col

        target_cols.append(target_col)

    seed_cols = ['tracks', 'artists']
    for col in seed_cols:
        seed_col = "seed_{}".format(col)
        seed_info.rename(columns={
            col: seed_col
        }, inplace=True)

    seed_info.rename(columns=rename_cols, inplace=True)

    feature_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                    'key', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
    target_cols = list()
    rename_cols = dict()

    for col in feature_cols:
        target_col = "target_{}".format(col)
        rename_cols[col] = target_col

        target_cols.append(target_col)

    seed_cols = ['tracks', 'artists']
    for col in seed_cols:
        seed_col = "seed_{}".format(col)
        seed_info.rename(columns={
            col: seed_col
        }, inplace=True)

    seed_info.rename(columns=rename_cols, inplace=True)

    _reco_tracks = np.array([])

    for seed_idx in range(len(seed_info)):
        reco_uri = "https://api.spotify.com/v1/recommendations"

        seed_dict = seed_info.iloc[seed_idx].to_dict()
        seed_dict['seed_genres'] = seed_genres
        seed_dict['market'] = "KR"
        seed_dict['limit'] = 100

        query = urlencode(seed_dict)
        headers = {
            "authorization": "Bearer {}".format(token['access_token'])
        }

        res = req.get("{}?{}".format(reco_uri, query), headers=headers)
        result = res.json()

        _tmp = np.array([])
        for track in result['tracks']:
            _id = track['id']
            _name = track['name']

            artist_list = track['album']['artists']
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

            _reco_tracks = np.append(_reco_tracks,
                                     [_id, _name, artists_id, artists]
                                     )

    _reco_tracks = _reco_tracks.reshape(-1, 4)
    reco_tracks = pd.DataFrame(_reco_tracks, columns=[
                               'id', 'name', 'artists', 'artists_name'])

    # 중복제거
    except_overlap_cols = [
        _ not in sel_tracks['id'].values for _ in reco_tracks['id']]
    reco_tracks = reco_tracks[except_overlap_cols]
    reco_tracks.drop_duplicates("id", inplace=True)

    if og is not None:
        reco_tracks = reco_tracks[[
            _ not in og['id'].values for _ in reco_tracks['id']]]

    return reco_tracks
