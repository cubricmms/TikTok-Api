import csv
from peewee import (
    CharField,
    Model,
)
from tqdm import tqdm

from core import db


class User(Model):
    id = CharField()
    username = CharField()
    sec_uid = CharField()

    class Meta:
        database = db


# Connect to the SQLite database
db.connect()

query = User.select().order_by(User.id).dicts()

# Calculate the total number of records
total = query.count()

# Open the CSV file
with open("./Combined.csv", "w", newline="") as f:
    writer = csv.writer(f)
    # Write the header
    writer.writerow(["id", "username", "sec_uid"])
    # Iterate over the query in chunks
    for chunk in tqdm(query, total=total):
        writer.writerow(chunk.values())

# Close the connection
db.close()
