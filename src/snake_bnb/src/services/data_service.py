from typing import List, Optional

import datetime

import bson

from data.bookings import Booking
from data.toys import Toy
from data.vip import Vip
from data.guests import Guest


def create_account(name: str, email: str) -> Vip:
    vip = Vip()
    vip.name = name
    vip.email = email

    vip.save()

    return vip


def find_account_by_email(email: str) -> Vip:
    vip = Vip.objects(email=email).first()
    return vip


def register_toy(active_account: Vip,
                  name, allow_dangerous, has_toys,
                  carpeted, meters, price) -> Toy:
    toy = Toy()

    toy.name = name
    toy.square_meters = meters
    toy.is_carpeted = carpeted
    toy.has_toys = has_toys
    toy.allow_dangerous_guests = allow_dangerous
    toy.price = price

    toy.save()

    account = find_account_by_email(active_account.email)
    account.toy_ids.append(toy.id)
    account.save()

    return toy


def find_toys_for_user(account: Vip) -> List[Toy]:
    query = Toy.objects(id__in=account.toy_ids)
    toys = list(query)

    return toys


def add_available_date(toy: Toy,
                       start_date: datetime.datetime, days: int) -> Toy:
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    toy = Toy.objects(id=toy.id).first()
    toy.bookings.append(booking)
    toy.save()

    return toy


def add_guest(account, name, length, species, is_venomous) -> Guest:
    guest = Guest()
    guest.name = name
    guest.length = length
    guest.species = species
    guest.is_venomous = is_venomous
    guest.save()

    vip = find_account_by_email(account.email)
    vip.guest_ids.append(guest.id)
    vip.save()

    return guest


def get_guests_for_user(user_id: bson.ObjectId) -> List[Guest]:
    vip = Vip.objects(id=user_id).first()
    guests = Guest.objects(id__in=vip.guest_ids).all()

    return list(guests)


def get_available_toys(checkin: datetime.datetime,
                        checkout: datetime.datetime, guest: Guest) -> List[Toy]:
    min_size = guest.length / 4

    query = Toy.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    if guest.is_venomous:
        query = query.filter(allow_dangerous_guests=True)

    toys = query.order_by('price', '-square_meters')

    final_toys = []
    for c in toys:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.patreon_guest_id is None:
                final_toys.append(c)

    return final_toys


def book_toy(account, guest, toy, checkin, checkout):
    booking: Optional[Booking] = None

    for b in toy.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.patreon_guest_id is None:
            booking = b
            break

    booking.patreon_vip_id = account.id
    booking.patreon_guest_id = guest.id
    booking.check_in_date = checkin
    booking.check_out_date = checkout
    booking.booked_date = datetime.datetime.now()

    toy.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)

    booked_toys = Toy.objects() \
        .filter(bookings__guest_vip_id=account.id) \
        .only('bookings', 'name')

    def map_toy_to_booking(toy, booking):
        booking.toy = toy
        return booking

    bookings = [
        map_toy_to_booking(toy, booking)
        for toy in booked_toys
        for booking in toy.bookings
        if booking.patreon_vip_id == account.id
    ]

    return bookings
