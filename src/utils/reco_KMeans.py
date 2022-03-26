from IPython.display import clear_output
from src.data_processing import music_filtering
from src.utils import KMeans


def reco_KMeans(norm_features, sel_tracks):
    kmeans = KMeans(
        datas=norm_features
    )
    kmeans.run(early_stop_cnt=5)
    clear_output(wait=True)

    _filtering_music_list = music_filtering(sel_tracks, kmeans)

    if len(_filtering_music_list) <= (100 + len(sel_tracks)):
        return _filtering_music_list, kmeans
    else:
        filter_music = norm_features.set_index(
            "id").loc[_filtering_music_list].reset_index()
    while True:
        kmeans = KMeans(
            datas=filter_music
        )
        kmeans.run(early_stop_cnt=5)
        clear_output(wait=True)

        _filtering_music_list = music_filtering(sel_tracks, kmeans)

        if len(_filtering_music_list) <= (100 + len(sel_tracks)):
            break
        else:
            filter_music = norm_features.set_index(
                "id").loc[_filtering_music_list].reset_index()

    return _filtering_music_list, kmeans
