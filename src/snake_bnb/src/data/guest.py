import datetime
import mongoengine


class Guest(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    gender = mongoengine.StringField(required=False)

    fun_level = mongoengine.FloatField(required=True)
    name = mongoengine.StringField(required=True)
    is_new = mongoengine.BooleanField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'guests'
    }
