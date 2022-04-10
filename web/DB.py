from pymongo import MongoClient as mc
import pandas as pd
from bson import ObjectId


class DB:
    def __init__(self):
        mongo_uri = "mongodb://localhost:27017"
        self.conn = mc(mongo_uri).TestMuLetter
        self.mail_box = self.conn.MailBox

    def get_mailbox(self, _obj_id):
        obj_id = ObjectId(_obj_id)

        mail_box = self.mail_box.find_one({
            "_id": obj_id
        })
        self.tracks = mail_box['tracks']
