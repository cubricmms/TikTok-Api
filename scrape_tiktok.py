from TikTokApi import TikTokApi
import asyncio
import os
import time
from  pprint import pprint as print

from peewee import *

db = SqliteDatabase('infulencer.db')

class User(Model):
    name = CharField()

    class Meta:
        database = db # This model uses the "people.db" database.


ms_token = os.environ.get("ms_token", '') # get your own ms_token from your cookies on tiktok.com

channels = set()

async def trending_videos():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)

        tag = api.hashtag(name="lifestyle")
        tag_info = await tag.info()
        video_count = int(tag_info['challengeInfo']['statsV2']['viewCount'])

        print(video_count)
        start_cursor = 0
        while video_count > 0:
            # async for video in tag.videos(count=30, cursor=start_cursor):
            async for video in api.trending.videos(count=30, cursor=start_cursor):
                username = video.author.username
                if username not in channels:
                    channels.add(username)
                    print(username)
                video_count -= 30
                start_cursor += 30

                print(f"Remaining videos: {video_count}")


if __name__ == "__main__":
    # db.connect()
    # db.create_tables([User])

    # user = User(name='John Doe')
    # user.save()

    # Start the timer
    start_time = time.time()

    try:
        # Run the async function and wait for it to complete
        asyncio.run(trending_videos())
    except:
        print(f'find {len(channels)} brands.  Saving to database.')

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time

    print(f"The function took {elapsed_time} seconds to complete.  {len(channels)} of them.")
