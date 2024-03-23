import asyncio
import os
import time

from peewee import CharField, Model
from playwright.async_api import ProxySettings
from tenacity import retry

from core import db, tk_api as api

ms_token = os.environ.get("MSTOKEN", "")

if os.environ.get("HTTP_PROXY", ""):
    print(f"Using HTTP_PROXY {os.environ['HTTP_PROXY']}")
    proxy_settings = ProxySettings(server=os.environ["HTTP_PROXY"])

headless_mode = os.environ.get("HEADLESS", "true").lower() in ("true", "1")
print(f"Headless mode: {headless_mode}")


class User(Model):
    id = CharField()
    username = CharField()
    sec_uid = CharField()

    class Meta:
        database = db


async def get_trending_vids(api):
    return api.trending.videos(count=30)


@retry
async def crawl():
    await api.create_sessions(
        ms_tokens=[ms_token],
        num_sessions=1,
        sleep_after=3,
        headless=headless_mode,
        proxies=[proxy_settings],
    )

    while True:
        videos = await get_trending_vids(api)
        async for video in videos:
            user_id = video.author.user_id
            username = video.author.username
            sec_uid = video.author.sec_uid

            if not User.get_or_none(id=user_id):
                User.create(id=user_id, username=username, sec_uid=sec_uid)
                print(f"Added user {username} to the database.")


if __name__ == "__main__":
    try:
        db.connect()
        db.create_tables([User])
        print(f"Begin with {User.select().count()}")
        start_time = time.time()
        asyncio.run(crawl())
    except KeyboardInterrupt:
        elapsed_time = time.time() - start_time
        print(f"The function took {elapsed_time} seconds to complete. ")
        print("Nicely shutting down...")
        print(f"End with {User.select().count()}")
        os._exit(42)
