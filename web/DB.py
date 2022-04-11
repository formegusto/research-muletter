from pymongo import MongoClient as mc
from bson import ObjectId
import datetime as dt


class DB:
    def __init__(self):
        mongo_uri = "mongodb://localhost:27017"
        self.conn = mc(mongo_uri).TestMuLetter
        self.mail = self.conn.Mail
        self.mail_box = self.conn.MailBox

    def get_mailbox(self, _obj_id):
        obj_id = ObjectId(_obj_id)

        mail_box = self.mail_box.find_one({
            "_id": obj_id
        })
        self.tracks = mail_box['tracks']

    def save_mail(self, reco):
        mail = {
            "mailBoxId": ObjectId(reco.mail_box_id),
            "tracks": [row.to_dict() for idx, row in reco.reco_musics.iterrows()],
            "visualImage": reco.visual_image,
            "ecv": reco.kmeans.ecv,
            "createdAt": dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }

        return self.mail.insert_one(mail)
