import asyncio
import logging
import os
import time
from pprint import pprint as print

from peewee import CharField, Model, SqliteDatabase
from playwright.async_api import ProxySettings
from TikTokApi import TikTokApi

db = SqliteDatabase("infulencer.db")

if os.environ["HTTP_PROXY"]:
    print(f"Using HTTP_PROXY {os.environ.get('HTTP_PROXY')}")
    proxy_settings = ProxySettings(server=os.environ["HTTP_PROXY"])


class User(Model):
    name = CharField()

    class Meta:
        database = db  # This model uses the "people.db" database.


ms_token = os.environ.get(
    "ms_token", ""
)  # get your own ms_token from your cookies on tiktok.com

channels = set()


async def trending_videos():
    async with TikTokApi(logging_level=logging.DEBUG) as api:
        try:
            await api.create_sessions(
                ms_tokens=[ms_token],
                num_sessions=1,
                sleep_after=3,
                headless=True,
                proxies=[proxy_settings],
            )

            tag = api.hashtag(name="lifestyle")
            tag_info = await tag.info()
            video_count = int(
                tag_info.get("challengeInfo", {})
                .get("statsV2", {})
                .get("viewCount", {})
            )

            print(video_count)
            start = 0
            while video_count > 0:
                # async for video in tag.videos(count=30, cursor=start):
                async for video in api.trending.videos(count=30, cursor=start):
                    username = video.author.username
                    if username not in channels:
                        channels.add(username)
                        print(username)
                    video_count -= 30
                    start += 30

                    print(f"Remaining videos: {video_count}")
        finally:
            await api.close_sessions()
            await api.stop_playwright()


if __name__ == "__main__":
    # db.connect()
    # db.create_tables([User])

    # user = User(name='John Doe')
    # user.save()

    try:
        # Start the timer
        start_time = time.time()

        # Run the async function and wait for it to complete
        asyncio.run(trending_videos())

        # Calculate the elapsed time
        elapsed_time = time.time() - start_time
    except KeyboardInterrupt:
        pass
    finally:
        print(
            f"The function took {elapsed_time} seconds to complete."
            f"{len(channels)} of them."
        )
