from mongoengine import connect
from mongoengine import Document
from mongoengine import IntField
from mongoengine import BooleanField
from mongoengine import StringField

try:
    import secrets
    dividers = re.compile(r"[/:@]")
    split_url = dividers.split(secrets.MONGO_URI)
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
except:
    print "Database connection with local database"
    connect("bookscraper")


class Book(Document):
    title = StringField()
    year = IntField()
    read = BooleanField()
    author = StringField()


class Author(Document):
    name = StringField()
