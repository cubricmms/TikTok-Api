import csv
from peewee import (
    BooleanField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)
from tqdm import tqdm

# Define your database and models
db = SqliteDatabase("infulencer.db")


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


# Connect to the SQLite database
db.connect()

query = (
    Stats.select(
        User.unique_id,
        User.nickname,
        User.bio_link,
        Stats.follower_count,
        Stats.heart_count,
        Stats.video_count,
        User.sec_uid,
        User.id,
    )
    .join(User)
    .order_by(Stats.follower_count.desc())
    .dicts()
)

# Calculate the total number of records
total = query.count()

# Open the CSV file
with open("./Combined.csv", "w", newline="") as f:
    writer = csv.writer(f)
    # Write the header
    writer.writerow(
        [
            "unique_id",
            "nickname",
            "bio_link",
            "follower_count",
            "heart_count",
            "video_count",
            "sec_uid",
            "id",
        ]
    )
    # Iterate over the query in chunks
    for chunk in tqdm(query, total=total):

        writer.writerow(chunk.values())

# Close the connection
db.close()
