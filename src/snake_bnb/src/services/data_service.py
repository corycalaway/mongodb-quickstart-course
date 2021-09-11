from typing import List, Optional

import datetime

import bson

from data.bookings import Booking
from data.cages import Cage
from data.vip import Vip
from data.snakes import Snake


def create_account(name: str, email: str) -> Vip:
    vip = Vip()
    vip.name = name
    vip.email = email

    vip.save()

    return vip


def find_account_by_email(email: str) -> Vip:
    vip = Vip.objects(email=email).first()
    return vip


def register_cage(active_account: Vip,
                  name, allow_dangerous, has_toys,
                  carpeted, meters, price) -> Cage:
    cage = Cage()

    cage.name = name
    cage.square_meters = meters
    cage.is_carpeted = carpeted
    cage.has_toys = has_toys
    cage.allow_dangerous_snakes = allow_dangerous
    cage.price = price

    cage.save()

    account = find_account_by_email(active_account.email)
    account.cage_ids.append(cage.id)
    account.save()

    return cage


def find_cages_for_user(account: Vip) -> List[Cage]:
    query = Cage.objects(id__in=account.cage_ids)
    cages = list(query)

    return cages


def add_available_date(cage: Cage,
                       start_date: datetime.datetime, days: int) -> Cage:
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    cage = Cage.objects(id=cage.id).first()
    cage.bookings.append(booking)
    cage.save()

    return cage


def add_snake(account, name, length, species, is_venomous) -> Snake:
    snake = Snake()
    snake.name = name
    snake.length = length
    snake.species = species
    snake.is_venomous = is_venomous
    snake.save()

    vip = find_account_by_email(account.email)
    vip.snake_ids.append(snake.id)
    vip.save()

    return snake


def get_snakes_for_user(user_id: bson.ObjectId) -> List[Snake]:
    vip = Vip.objects(id=user_id).first()
    snakes = Snake.objects(id__in=vip.snake_ids).all()

    return list(snakes)


def get_available_cages(checkin: datetime.datetime,
                        checkout: datetime.datetime, snake: Snake) -> List[Cage]:
    min_size = snake.length / 4

    query = Cage.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    if snake.is_venomous:
        query = query.filter(allow_dangerous_snakes=True)

    cages = query.order_by('price', '-square_meters')

    final_cages = []
    for c in cages:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.patreon_guest_id is None:
                final_cages.append(c)

    return final_cages


def book_cage(account, snake, cage, checkin, checkout):
    booking: Optional[Booking] = None

    for b in cage.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.patreon_guest_id is None:
            booking = b
            break

    booking.patreon_vip_id = account.id
    booking.patreon_guest_id = snake.id
    booking.check_in_date = checkin
    booking.check_out_date = checkout
    booking.booked_date = datetime.datetime.now()

    cage.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)

    booked_cages = Cage.objects() \
        .filter(bookings__guest_vip_id=account.id) \
        .only('bookings', 'name')

    def map_cage_to_booking(cage, booking):
        booking.cage = cage
        return booking

    bookings = [
        map_cage_to_booking(cage, booking)
        for cage in booked_cages
        for booking in cage.bookings
        if booking.patreon_vip_id == account.id
    ]

    return bookings
