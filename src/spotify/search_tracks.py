import requests as req
from functools import reduce
from urllib.parse import urlencode
from IPython.display import clear_output
import pandas as pd


def search_tracks(token):
    search_uri = "https://api.spotify.com/v1/search"
    sel_tracks = pd.DataFrame(
        columns=['id', 'name', 'artists', 'artists_name'])

    while True:
        q = input("검색어를 입력해주세요.")
        offset = 0
        limit = 10

        while True:
            query = urlencode({
                "q": q,
                "type": "track",
                "market": "KR",
                "limit": limit,
                "offset": offset
            })
            headers = {
                "authorization": "Bearer {}".format(token['access_token'])
            }

            res = req.get("{}?{}".format(search_uri, query), headers=headers)

            result = res.json()['tracks']

            _result = list()

            for item in result['items']:
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

                _result.append({
                    "id": _id,
                    "name": _name,
                    # "artists": artists_id,
                    # "artists_name": artists,
                    "artists": artists_id.split(",")[0],
                    "artists_name": artists.split(",")[0],
                })

            for idx, _ in enumerate(_result):
                print("\t{}.{} - {} ({})".format(idx + 1, _['artists_name'],
                                                 _['name'], _['id']))

            print("{}/{}".format(limit * (offset + 1), result['total']))

            _action = input("선택은 번호입력을 해주세요." +
                            "\n종료는 exit, 다음페이지는 next를 입력해주세요.")

            if _action == "exit":
                clear_output()
                break
            elif _action == "next":
                offset += 1
                clear_output()
            else:
                _action = int(_action) - 1
                sel_tracks = sel_tracks.append(
                    _result[_action], ignore_index=True)
                clear_output()
                break

        _action = input("계속하시려면 next, 종료는 exit를 입력해주세요.")

        if _action == "exit":
            break

    return sel_tracks
