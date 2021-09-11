import datetime
import mongoengine

from data.bookings import Booking


class Toy(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    toy_name = mongoengine.StringField(required=True)
    toy_price = mongoengine.FloatField(required=True)
    experience_level = mongoengine.FloatField(required=True)
    toy_rating = mongoengine.IntField(required=False)
    toy_review = mongoengine.StringField(required=False)

    bookings = mongoengine.EmbeddedDocumentListField(Booking)

    meta = {
        'db_alias': 'core',
        'collection': 'toys'
    }
