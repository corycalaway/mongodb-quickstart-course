import datetime
import mongoengine


class Vip(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)

    guest_ids = mongoengine.ListField()
    toy_ids = mongoengine.ListField()

    meta = {
        'db_alias': 'core',
        'collection': 'vips'
    }
