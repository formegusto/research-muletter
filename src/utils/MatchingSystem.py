import pandas as pd
import math as mt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

from math import pi
from IPython.display import clear_output

from src.utils import KMeans
from src.data_processing import make_norm
from pymongo import MongoClient as mc
from bson import ObjectId
from sklearn.decomposition import PCA

quadrant_check = [[1, 1], [1, -1], [-1, -1], [-1, 1]]


def get_quadrant(angle):
    chk_angle = [0, 90, 180, 270]
    if angle in chk_angle:
        return -1
    else:
        if angle < 90:
            return 0
        elif angle < 180:
            return 1
        elif angle < 270:
            return 2
        elif angle < 360:
            return 3


def check_guadrant(angle, point):
    if angle == 0:
        return [0, point[1]]
    elif angle == 90:
        return [point[1], 0]
    elif angle == 180:
        return [0, point[1] * -1]
    elif angle == 270:
        return [point[1] * -1, 0]


def get_coord(datas):
    cent_points = list()
    r, c = datas.shape
    angles = np.array([x/float(c)*(2*pi) for x in range(c)])

    for data in datas:
        non_zero_labels = data != 0

        x = angles[non_zero_labels]
        y = data[non_zero_labels]

        point = np.array([[x[i], y[i]] for i, _ in enumerate(x)])
        point = point.reshape(-1, 2)

        for idx, pt in enumerate(point):
            rad = pt[0]
            ang = rad / pi * 180

            dis = pt[1]
            quad = get_quadrant(ang)
            if quad == -1:
                point[idx] = check_guadrant(ang, pt)
            else:
                if (ang < 90) or \
                        (ang > 180 and ang < 270):
                    ang = 90 - (ang % 90)
                else:
                    ang = ang % 90
                rad = ang * pi / 180

                quad = quadrant_check[quad]
                x = dis * mt.cos(rad) * quad[0]  # get X
                y = dis * mt.sin(rad) * quad[1]  # get Y

                point[idx] = [x, y]

        cent_points.append(point.sum(axis=0))
    return np.array(cent_points)


class MatchingSystem:
    def __init__(self):
        mongo_uri = "mongodb://localhost:27017"
        self.conn = mc(mongo_uri).MuLetter
        self.seed_zone = self.conn.SeedZone
        self.mail_box = self.conn.MailBox
        self.cluster_zone = self.conn.ClusterZone
        self.is_run = False

    def check(self):
        seed_musics = self.seed_zone.estimated_document_count()
        K = round(mt.sqrt(seed_musics / 2))

        print("현재 seed 음악 갯수 : {}".format(seed_musics))
        print("K 갯수 : {} (후에 체크 방식으로 진행)".format(K))

        self.is_run = True

    def kmeans_run(self):
        _seed_features = self.seed_zone.find({}, {
            "label": 0
        })
        seed_features = pd.DataFrame([_ for _ in _seed_features])

        seed_features.drop(["_id"], axis=1, inplace=True)
        seed_features.rename({"track_id": "id"}, axis=1, inplace=True)
        self.seed_features = seed_features

        norm_features = make_norm(seed_features)

        kmeans = KMeans(
            datas=norm_features
        )
        kmeans.run(early_stop_cnt=5)
        kmeans.sorting_ver_2()

        self.norm_features = norm_features
        self.kmeans = kmeans

        music_label = pd.DataFrame(norm_features['id'])
        music_label['label'] = kmeans.clusters
        music_label.rename({"id": "track_id"}, axis=1, inplace=True)

        self.music_label = music_label
        self.cluster_zone.delete_many({})

        for label, k_pat in enumerate(self.kmeans.K_pattern):
            in_db = dict()

            in_db = {
                "label": label,
            }

            _k_pat = k_pat.tolist()
            feature_cols = norm_features.columns[1:-1].values
            for idx, col in enumerate(feature_cols):
                in_db[col] = _k_pat[idx]

            self.cluster_zone.insert_one(
                in_db
            )
        print("Cluster Zone DB update Success.")

        for _, label_info in music_label.iterrows():
            track_id, label = label_info

            self.seed_zone.update_one({
                "track_id": track_id
            }, {
                "$set": {
                    "label": label
                }
            })

        print("Seed Zone DB update Success.")

    def box_matching(self):
        _label = self.kmeans.clusters
        _mail_boxes = self.mail_box.find()
        mail_boxes = [_ for _ in _mail_boxes]
        self.mail_boxes = mail_boxes

        mail_box_radar = pd.DataFrame(columns=set(_label))

        for target_mail_box in mail_boxes:
            target = pd.DataFrame(target_mail_box['tracks'])
            target_label_info = pd.merge(target, self.music_label,
                                         on='track_id')
            group_cnt = target_label_info.groupby(
                ['label']).count()['track_id']

            mail_box_radar.loc[str(target_mail_box['_id'])] = (
                group_cnt / len(target_label_info) * 100).round().astype("int")

        mail_box_radar.fillna(0, inplace=True)
        mail_box_radar = mail_box_radar.astype("int")

        self.mail_box_radar = mail_box_radar

    def make_coord(self):
        mail_box_datas = self.mail_box_radar.values
        max_points = np.identity(len(self.mail_box_radar.columns)) * 100

        mail_box_coord, max_coord = get_coord(
            mail_box_datas), get_coord(max_points)

        self.mail_box_coord = mail_box_coord
        self.max_coord = max_coord

        self.mail_box_points = pd.DataFrame(mail_box_coord, columns=['x', 'y'],
                                            index=self.mail_box_radar.index)

        for box_id, values in self.mail_box_points.iterrows():
            x, y = values

            in_dict = {
                "x": x,
                "y": y
            }
            self.mail_box.update_one({
                "_id": ObjectId(box_id)
            }, {
                "$set": {
                    "coord": in_dict
                }
            })

        print("Mail Box Points Save Success.")

    def make_coord_ver_2(self):
        mail_box_datas = self.mail_box_radar.values
        max_points = np.identity(len(self.mail_box_radar.columns)) * 100

        pca = PCA(n_components=2)
        fit_datas = pca.fit_transform(np.concatenate(
            (mail_box_datas, max_points), axis=0))

        self.mail_box_points = pd.DataFrame(
            fit_datas[:len(self.mail_box_radar.columns) * -1], columns=['x', 'y'], index=self.mail_box_radar.index)
        self.max_points = fit_datas[len(self.mail_box_radar.columns) * -1:]

        for box_id, values in self.mail_box_points.iterrows():
            x, y = values

            in_dict = {
                "x": x,
                "y": y
            }
            self.mail_box.update_one({
                "_id": ObjectId(box_id)
            }, {
                "$set": {
                    "coord": in_dict
                }
            })

        print("Mail Box Points Save Success.")

    def visual_coord(self):
        plt.figure(figsize=(20, 15))

        my_palette = plt.cm.get_cmap("rainbow", len(self.mail_box_radar))
        for idx, pt in enumerate(self.mail_box_coord):
            color = my_palette(idx)
            x = pt[0]
            y = pt[1]
            plt.scatter(x, y, s=600, color=color,
                        label=self.mail_box_radar.index[idx])

        for idx, pt in enumerate(self.max_coord):
            plt.text(pt[0], pt[1], "{} 클러스터 성향".format(idx + 1), fontsize=20,
                     ha="center")

        plt.xticks([
            self.max_coord[:, 0].min(),
            self.max_coord[:, 0].max()
        ])
        plt.yticks([
            self.max_coord[:, 1].min(),
            self.max_coord[:, 1].max()
        ])

        plt.axhline(
            0, color='black'
        )
        plt.axvline(
            0, color='black'
        )
        plt.axis("off")
        # plt.legend()

        plt.show()

    def visual_radar_step(self):
        # 따로 그리기
        mail_box_radar = self.mail_box_radar

        labels = mail_box_radar.columns
        num_labels = len(labels)

        angles = [x/float(num_labels)*(2*pi)
                  for x in range(num_labels)]  # 각 등분점
        angles += angles[:1]  # 시작점으로 다시 돌아와야하므로 시작점 추가

        my_palette = plt.cm.get_cmap("rainbow", len(mail_box_radar))
        cnt = 0
        while True:
            fig = plt.figure(figsize=(16, 8))
            fig.set_facecolor('white')

            start_idx = cnt * 2
            end_idx = (cnt + 1) * 2
            for i, row in enumerate(mail_box_radar.values[start_idx:end_idx]):
                color = my_palette(start_idx + i)
                data = row.tolist()
                data += data[:1]  # 원점 데이터

                ax = plt.subplot(1, 2, i+1, polar=True)
                ax.set_theta_offset(pi / 2)  # 시작점
                ax.set_theta_direction(-1)  # 그려지는 방향 시계방향

                plt.xticks(angles[:-1], labels, fontsize=13)  # x축 눈금 라벨
                # x축과 눈금 사이에 여백을 준다.
                ax.tick_params(axis='x', which='major', pad=15)

                ax.set_rlabel_position(0)  # y축 각도 설정(degree 단위)
                plt.yticks(range(0, 100, 10), [str(_) for _ in range(
                    0, 100, 10)], fontsize=10)  # y축 눈금 설정
                plt.ylim(0, 100)

                ax.plot(angles, data, color=color, linewidth=2,
                        linestyle='solid')  # 레이더 차트 출력
                # 도형 안쪽에 색을 채워준다.
                ax.fill(angles, data, color=color, alpha=0.4)

                # 타이틀은 캐릭터 클래스로 한다.
                plt.title(mail_box_radar.index[start_idx + i],
                          size=20, color=color, x=-0.2, y=1.2, ha='left')

            plt.tight_layout(pad=5)  # subplot간 패딩 조절
            plt.show()

            action = input("계속 진행하시려면 next, 종료는 아무거나 입력해주세요.")

            if action == "next":
                cnt += 1
                clear_output(wait=True)
            else:
                break

    def visual_radar(self):
        mail_box_radar = self.mail_box_radar

        labels = mail_box_radar.columns
        num_labels = len(labels)

        angles = [x/float(num_labels)*(2*pi)
                  for x in range(num_labels)]  # 각 등분점
        angles += angles[:1]  # 시작점으로 다시 돌아와야하므로 시작점 추가

        my_palette = plt.cm.get_cmap("rainbow", len(mail_box_radar))

        fig = plt.figure(figsize=(15, 20))
        fig.set_facecolor('white')
        ax = fig.add_subplot(polar=True)

        for i, row in enumerate(mail_box_radar.values):
            color = my_palette(i)
            data = row.tolist()
            data += data[:1]  # 원점 데이터

            ax.set_theta_offset(pi / 2)  # 시작점
            ax.set_theta_direction(-1)  # 그려지는 방향 시계방향

            plt.xticks(angles[:-1], labels, fontsize=13)  # x축 눈금 라벨
            # x축과 눈금 사이에 여백을 준다.
            ax.tick_params(axis='x', which='major', pad=15)
            ax.set_rlabel_position(0)  # y축 각도 설정(degree 단위)
            plt.yticks(range(0, 100, 10), [str(_) for _ in range(
                0, 100, 10)], fontsize=10)  # y축 눈금 설정
            plt.ylim(0, 100)

            ax.plot(angles, data, color=color, linewidth=2, linestyle='solid',
                    label=mail_box_radar.index[i])  # 레이더 차트 출력
            ax.fill(angles, data, color=color, alpha=0.4)  # 도형 안쪽에 색을 채워준다.

        for g in ax.yaxis.get_gridlines():  # grid line
            g.get_path()._interpolation_steps = len(labels)

        spine = Spine(axes=ax,
                      spine_type='circle',
                      path=Path.unit_regular_polygon(len(labels)))

        # Axes의 중심과 반지름을 맞춰준다.
        spine.set_transform(
            Affine2D().scale(.5).translate(.5, .5)+ax.transAxes)

        ax.spines = {'polar': spine}  # frame의 모양을 원에서 폴리곤으로 바꿔줘야한다.

        # plt.legend(loc=(0.9,0.9))
        plt.show()
