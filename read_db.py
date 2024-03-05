from peewee import (
    BooleanField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
    OperationalError,
    SqliteDatabase,
    TextField,
)

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


if __name__ == "__main__":
    with db:
        try:
            db.connect()
        except OperationalError:
            pass
        print(User.select().count())
