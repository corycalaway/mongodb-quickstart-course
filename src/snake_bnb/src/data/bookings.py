import mongoengine


class Booking(mongoengine.EmbeddedDocument):
    patreon_vip_id = mongoengine.ObjectIdField()
    patreon_guest_id = mongoengine.ObjectIdField()

    booked_date = mongoengine.DateTimeField()
    check_in_date = mongoengine.DateTimeField(required=True)
    check_out_date = mongoengine.DateTimeField(required=True)

    room_review = mongoengine.StringField()
    room_rating = mongoengine.IntField(default=0)

    @property
    def duration_in_days(self):
        dt = self.check_out_date - self.check_in_date
        return dt.days
