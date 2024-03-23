from tenacity import Retrying, stop_after_attempt
from peewee import (
    BooleanField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)
import json
from core import db


class User(Model):
    id = CharField()
    bio_link = CharField()
    nickname = CharField()
    sec_uid = CharField()
    secret = BooleanField()
    signature = TextField()
    unique_id = CharField(primary_key=True)
    verified = BooleanField()

    class Meta:
        database = db


class Stats(Model):
    user = ForeignKeyField(User, backref="stats")
    follower_count = IntegerField()
    heart_count = IntegerField()
    video_count = IntegerField()

    class Meta:
        database = db


async def get_user_info(api, username):
    for attempt in Retrying(stop=stop_after_attempt(5)):
        with attempt:
            data = await api.user(username).info()
    return data


def parse_and_save_user_info(data):
    # Parse the user info from the JSON data
    user_info = data["userInfo"]["user"]
    stats_info = data["userInfo"]["stats"]

    # Create a new User instance and save it to the database
    _user = User.create(
        id=user_info["id"],
        bio_link=json.dumps(user_info.get("bioLink", "{}")),
        nickname=user_info["nickname"],
        sec_uid=user_info["secUid"],
        secret=user_info["secret"],
        signature=user_info["signature"],
        unique_id=user_info["uniqueId"],
        verified=user_info["verified"],
    )

    # Create a new Stats instance and save it to the database
    Stats.create(
        user=_user,
        follower_count=stats_info["followerCount"],
        heart_count=stats_info["heartCount"],
        video_count=stats_info["videoCount"],
    )

    return _user
