import pytest
import datetime

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from db.models import (
    Actor,
    Genre,
    Movie,
    MovieSession,
    CinemaHall,
    Order,
    Ticket
)
from services.movie_session import (
    get_tickets_of_taken_seats
)
from services.user import create_user, get_user, update_user
from services.order import create_order, get_orders


@pytest.fixture()
def database_data():
    action = Genre.objects.create(name="Action")
    drama = Genre.objects.create(name="Drama")
    western = Genre.objects.create(name="Western")

    reeves = Actor.objects.create(first_name="Keanu", last_name="Reeves")
    johansson = Actor.objects.create(first_name="Scarlett",
                                     last_name="Johansson")
    clooney = Actor.objects.create(first_name="George", last_name="Clooney")

    matrix = Movie.objects.create(title="Matrix", description="Matrix movie")
    matrix.actors.add(reeves)
    matrix.actors.add(johansson)
    matrix.genres.add(action)

    batman = Movie.objects.create(title="Batman", description="Batman movie")
    batman.genres.add(drama)
    batman.actors.add(clooney)

    titanic = Movie.objects.create(title="Titanic",
                                   description="Titanic movie")
    titanic.genres.add(drama, action)

    good_bad = Movie.objects.create(
        title="The Good, the Bad and the Ugly",
        description="The Good, the Bad and the Ugly movie",
    )
    good_bad.genres.add(western)

    blue = CinemaHall.objects.create(name="Blue", rows=10, seats_in_row=12)
    vip = CinemaHall.objects.create(name="VIP", rows=4, seats_in_row=6)
    cheap = CinemaHall.objects.create(name="Cheap", rows=15, seats_in_row=27)

    MovieSession.objects.create(
        show_time=datetime.datetime(2019, 8, 19, 20, 30),
        cinema_hall=blue,
        movie=matrix
    )
    MovieSession.objects.create(
        show_time=datetime.datetime(2017, 8, 19, 11, 10),
        cinema_hall=cheap,
        movie=titanic,
    )
    MovieSession.objects.create(
        show_time=datetime.datetime(2021, 4, 3, 13, 50),
        cinema_hall=vip,
        movie=good_bad
    )

    MovieSession.objects.create(
        show_time=datetime.datetime(2021, 4, 3, 16, 30),
        cinema_hall=cheap,
        movie=matrix
    )

    get_user_model().objects.create_user(username="user1",
                                         password="pass1234")
    get_user_model().objects.create_user(username="user2",
                                         password="pass1234")

    Order.objects.create(user_id=1)
    Order.objects.create(user_id=1)
    Order.objects.create(user_id=2)

    Ticket.objects.create(movie_session_id=1,
                          order_id=1,
                          row=7,
                          seat=10)
    Ticket.objects.create(movie_session_id=1,
                          order_id=1,
                          row=7,
                          seat=11)
    Ticket.objects.create(movie_session_id=2,
                          order_id=2,
                          row=9,
                          seat=5)
    Ticket.objects.create(movie_session_id=2,
                          order_id=2,
                          row=9,
                          seat=6)


def test_auth_user_models():
    assert settings.AUTH_USER_MODEL == "db.User"


@pytest.mark.django_db
def test_order_str(database_data):
    order = Order.objects.get(id=1)
    assert str(order) == str(order.created_at)
    order = Order.objects.get(id=2)
    assert str(order) == str(order.created_at)


@pytest.mark.django_db
def test_order_ordering(database_data):
    assert list(Order.objects.all().values_list("id")) == [
        (3,),
        (2,),
        (1,)
    ]


@pytest.mark.django_db
def test_ticket_str(database_data):
    movie = Movie.objects.create(title="Speed", description="Speed desc")
    cinema_hall = CinemaHall.objects.create(name="Blue",
                                            rows=10,
                                            seats_in_row=15)
    movie_session = MovieSession.objects.create(
        show_time=datetime.datetime(2020, 11, 10, 20, 30),
        cinema_hall=cinema_hall,
        movie=movie
    )
    ticket = Ticket.objects.create(
        order_id=1,
        movie_session=movie_session,
        row=9,
        seat=9
    )
    assert str(ticket) == "Speed 2020-11-10 20:30:00 (row: 9, seat: 9)"


@pytest.mark.django_db
def test_ticket_unique_together(database_data):
    movie = Movie.objects.create(title="Speed", description="Speed desc")
    cinema_hall = CinemaHall.objects.create(name="Blue", rows=10,
                                            seats_in_row=15)
    movie_session = MovieSession.objects.create(
        show_time=datetime.datetime(2020, 11, 10, 20, 30),
        cinema_hall=cinema_hall,
        movie=movie
    )
    Ticket.objects.create(
        order_id=1,
        movie_session=movie_session,
        row=9,
        seat=9
    )
    with pytest.raises(IntegrityError):
        Ticket.objects.create(
            order_id=1,
            movie_session=movie_session,
            row=9,
            seat=9
        )


@pytest.mark.django_db
def test_movie_session_service_get_taken_seats(database_data):
    assert list(get_tickets_of_taken_seats(movie_session_id=1).values_list(
        "order", "row", "seat"
    )) == [
        (1, 7, 10),
        (1, 7, 11)
    ]

    assert list(get_tickets_of_taken_seats(movie_session_id=2).values_list(
        "order", "row", "seat"
    )) == [(2, 9, 5), (2, 9, 6)]


@pytest.mark.django_db
def test_user_service_create_user():
    create_user(username="User1",
                password="Password1234")
    create_user(username="User2",
                password="Password5678",
                first_name="Johnny",
                last_name="Depp",
                email="j_depp@gmail.com")
    assert list(get_user_model().objects.all().values_list(
        "username", "first_name", "last_name", "email")) == [
        ("User1", "", "", ""),
        ("User2", "Johnny", "Depp", "j_depp@gmail.com")
    ]
    assert get_user_model().objects.get(
        username="User1"
    ).password != "Password1234", "Password should be encrypted"
    assert get_user_model().objects.get(
        username="User2"
    ).password != "Password5678", "Password should be encrypted"


@pytest.mark.django_db
def test_user_service_get_user(database_data):
    user = get_user(user_id=1)
    assert user.username == "user1"
    user = get_user(user_id=2)
    assert user.username == "user2"


@pytest.mark.django_db
def test_user_service_update_user_with_no_data(database_data):
    user1_password = get_user_model().objects.get(id=1).password
    update_user(1)
    assert list(get_user_model().objects.filter(id=1).values_list(
        "username", "first_name", "last_name", "email")) == [
        ("user1", "", "", ""),
    ]
    assert get_user_model().objects.get(id=1).password == user1_password


@pytest.mark.django_db
def test_user_service_update_user_with_email(database_data):
    user1_password = get_user_model().objects.get(id=1).password
    update_user(1, email="user1@gmail.com")
    assert list(get_user_model().objects.filter(id=1).values_list(
        "username", "first_name", "last_name", "email")) == [
        ("user1", "", "", "user1@gmail.com"),
    ]
    assert get_user_model().objects.get(id=1).password == user1_password


@pytest.mark.django_db
def test_user_service_update_user_with_password(database_data):
    update_user(1, password="new_password1234")
    assert list(get_user_model().objects.filter(id=1).values_list(
        "username", "first_name", "last_name", "email")) == [
        ("user1", "", "", ""),
    ]
    assert get_user_model().objects.get(id=1).check_password(
        "new_password1234"
    )


@pytest.mark.django_db
def test_user_service_update_user_with_whole_data(database_data):
    update_user(1,
                password="new_password1234",
                email="user1_@gmail.com",
                first_name="Johnny",
                last_name="Depp")
    assert list(get_user_model().objects.filter(id=1).values_list(
        "username", "first_name", "last_name", "email")) == [
        ("user1", "Johnny", "Depp", "user1_@gmail.com"),
    ]
    assert get_user_model().objects.get(id=1).check_password(
        "new_password1234"
    )


@pytest.mark.django_db
def test_order_service_get_orders_without_user(database_data):
    assert list(get_orders().values_list("user__username")) == [
        ("user2",),
        ("user1",),
        ("user1",)
    ]


@pytest.mark.django_db
def test_order_service_get_orders_with_user(database_data):
    assert list(get_orders(username="user1").values_list(
        "user__username"
    )) == [("user1",), ("user1",)]


@pytest.fixture()
def tickets():
    return [
        {
            "row": 10,
            "seat": 8,
            "movie_session": 1
        },
        {
            "row": 10,
            "seat": 9,
            "movie_session": 1
        }
    ]


@pytest.fixture()
def create_order_data():
    movie = Movie.objects.create(title="Speed", description="Description")
    cinema_hall = CinemaHall.objects.create(name="Blue", rows=14,
                                            seats_in_row=12)
    MovieSession.objects.create(
        show_time=datetime.datetime.now(),
        movie=movie,
        cinema_hall=cinema_hall,
    )
    get_user_model().objects.create_user(username="user_1")


@pytest.mark.django_db
def test_order_service_create_order_without_date(create_order_data, tickets):
    create_order(tickets=tickets, username="user_1")
    assert list(Order.objects.all().values_list("user__username")) == [
        ("user_1",)
    ]
    assert list(Ticket.objects.filter(movie_session=1).values_list(
        "row", "seat", "movie_session"
    )) == [
        (10, 8, 1),
        (10, 9, 1)
    ]


@pytest.mark.django_db
def test_order_service_create_order_with_date(create_order_data, tickets):
    create_order(tickets=tickets, username="user_1", date="2020-11-10 14:40")
    assert list(Order.objects.all().values_list("user__username")) == [
        ("user_1",)
    ]
    assert list(Ticket.objects.filter(movie_session=1).values_list(
        "row", "seat", "movie_session"
    )) == [(10, 8, 1), (10, 9, 1)]
    assert Order.objects.first().created_at == datetime.datetime(
        2020, 11, 10, 12, 40, tzinfo=datetime.timezone.utc
    )


@pytest.mark.django_db
def test_ticket_clean_row_out_of_range(database_data):
    ticket = Ticket.objects.create(
        movie_session_id=1,
        order_id=1,
        row=11,
        seat=5.
    )
    with pytest.raises(ValidationError) as e_info:
        ticket.clean()

    assert str(e_info.value) == "{'row': ['row number must be in available " \
                                "range: (1, rows): (1, 10)']}"


@pytest.mark.django_db
def test_ticket_clean_seat_out_of_range(database_data):
    ticket = Ticket.objects.create(
        movie_session_id=1,
        order_id=1,
        row=10,
        seat=13.
    )
    with pytest.raises(ValidationError) as e_info:
        ticket.clean()

    assert str(e_info.value) == ("{'seat': ['seat number must be in "
                                 "available range: (1, seats_in_row): "
                                 "(1, 12)']}")
