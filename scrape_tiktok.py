import asyncio
import json
import os
import time

from peewee import (
    BooleanField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)
from playwright.async_api import ProxySettings
from TikTokApi import TikTokApi
from tenacity import Retrying, RetryError, stop_after_attempt, retry

db = SqliteDatabase("infulencer.db")
ms_token = os.environ.get("MSTOKEN", "")

if os.environ.get("HTTP_PROXY", ""):
    print(f"Using HTTP_PROXY {os.environ['HTTP_PROXY']}")
    proxy_settings = ProxySettings(server=os.environ["HTTP_PROXY"])


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


@retry
async def trending_videos():
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=2,
            sleep_after=3,
            headless=False,
            proxies=[proxy_settings],
        )

        cursor = 0
        while True:
            # async for video in api.trending.videos(count=30, cursor=cursor):
            async for video in api.trending.videos(count=30):
                username = video.author.username
                if not User.get_or_none(unique_id=username):
                    user = api.user(username)

                    try:
                        for attempt in Retrying(stop=stop_after_attempt(5)):
                            with attempt:
                                data = await user.info()
                    except RetryError:
                        print(f"ERROR: fail to pull {username} from tiktok.")
                        continue

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

                    print(f"Added {username} to the database")
                cursor += 30


if __name__ == "__main__":
    try:
        db.connect()
        db.create_tables([User, Stats])
        print(User.select().count())

        start_time = time.time()
        asyncio.run(trending_videos())
    except KeyboardInterrupt:
        elapsed_time = time.time() - start_time
        print(f"The function took {elapsed_time} seconds to complete. ")
        print("Nicely shutting down...")
        os._exit(42)
