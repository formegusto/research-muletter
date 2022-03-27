import matplotlib
import matplotlib.pyplot as plt


def visual_norm_data(sel_tracks, norm_features):
    matplotlib.rc('font', family='AppleGothic')
    plt.rcParams['axes.unicode_minus'] = False

    is_general = False
    if sel_tracks is None:
        is_general = True

    plt.figure(figsize=(16, 8))
    x_ticks_labels = norm_features.columns.difference(['id']).values

    if is_general:
        for _idx in range(len(norm_features)):
            feature = norm_features.iloc[_idx]

            plt.plot(
                x_ticks_labels, feature.values[1:], color="g", linewidth=0.15)
    else:
        for _idx in range(len(norm_features)):
            feature = norm_features.iloc[_idx]
            _id = feature['id']
            if _id in sel_tracks['id'].values:
                plt.plot(
                    x_ticks_labels, feature.values[1:], color="g", linewidth=2, label="사용자 음악성향 데이터")
            else:
                plt.plot(
                    x_ticks_labels, feature.values[1:], color="g", linewidth=0.15, label="Spotify 추천 데이터")

        plt.legend(
            labels=['사용자 음악성향 데이터', 'Spotify 추천 데이터'], loc='upper right')
    plt.show()
