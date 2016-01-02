import re
import os

from mongoengine import connect
from mongoengine import Document
from mongoengine import IntField
from mongoengine import BooleanField
from mongoengine import StringField

try:
    mongo_uri = os.environ.get("MONGOLAB_URI")
    if not mongo_uri:
        import secrets
        mongo_uri = secrets.MONGO_URI

    dividers = re.compile(r"[/:@]")
    split_url = dividers.split(mongo_uri)
    username = split_url[3]
    password = split_url[4]
    host = split_url[5]
    port = int(split_url[6])

    print "Database connection with", username

    connect(
        username,
        username=username,
        password=password,
        host=host,
        port=port
    )
except Exception, e:
    print "Couldn't connect to remote database:", e
    connect("bookscraper")
    print "Connected with local database"


class Book(Document):
    title = StringField()
    link = StringField()
    year = IntField()
    read = BooleanField()
    author = StringField()


class Author(Document):
    name = StringField()
    year = IntField()
