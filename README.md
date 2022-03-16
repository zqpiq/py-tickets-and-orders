# Tickets and orders

- Read [the guideline](https://github.com/mate-academy/py-task-guideline/blob/main/README.md) before start

In `db/models.py` you already have tables you created earlier. Now
you have to create tables:
1. `Order`, with such fields:
    - datetime field `created_at`, the datetime when the order was created,
set `auto_add_now` to fill this field automatically during the creation.
    - foreign key `user`, the user that created the order.
   
There should be implemented the string representation of the order:
```python
print(Order.objects.first())
<Order: 2022-03-15 15:59:50.009379+00:00>
```
Orders should be ordered from the newest to the oldest by default.
2. `Ticket`, with such fields:
   - foreign key `movie_session`, is related to the table `MovieSession`
   - foreign key `order`, is related to the table `Order`
   - integer field `row`, the row of the seat 
   - integer field `seat`, number of the seat in row

There should be implemented the string representation of the ticket, show
information about movie session, row and seat:
```python
print(Ticket.objects.first())
<Ticket: Speed 2020-11-11 09:30:00+00:00 (row: 6, seat: 12)>
```
Ticket should implement method `clean()`. This method should check if 
`row` and `seat` are correct and are not greater than values in 
`ticket.movie_session.cinema_hall`, if they are - ValidationError should
be raised.

```python
import datetime

cinema_hall = CinemaHall.objects.create(name="Blue", rows=18, seats_in_row=24)
movie_session = MovieSession.objects.create(
    show_time=datetime.datetime(2022, 3, 20, 19, 30),
    movie_id=1, 
    cinema_hall=cinema_hall)
order = Order.objects.create(user_id=1)

ticket = Ticket.objects.create(
    movie_session=movie_session,
    order=order,
    row=19,
    seat=20
)
ticket.clean()
# django.core.exceptions.ValidationError: {'row': ['row number must be in available range: (1, rows): (1, 18)']}

ticket = Ticket.objects.create(
    movie_session=movie_session,
    order=order,
    row=17,
    seat=26
)
ticket.clean()
# django.core.exceptions.ValidationError: {'seat': ['seat number must be in available range: (1, seats_in_row): (1, 24)']}
```
3. Custom model `User`, that model should inherit from `AbstractUser`. To replace
the default user model with custom, edit `settings.py`, add there 
`AUTH_USER_MODEL`.

In `services` you already have services you created earlier. Now
you have to create such services:
1. `user.py`, add such function:
   - `create_user`, takes `username`, `password`, optional parameters 
`email`, `first_name`, `last_name`. The method should save user properly (password 
should be encrypted), use method `.create_user()` for this purpose. Also, 
set fields if appropriate optional values are provided.
   - `get_user`, takes `user_id`, returns user with the given id.
   - `update_user`, takes `user_id`, optional parameters `password`, `email`, 
`first_name`, `last_name`. Update user with
provided id and set fields if appropriate values are provided. To save password
properly use the method `.set_password()`.
2. `movie_session.py`, add such function:
   - `get_tickets_of_taken_seats`, takes `movie_session_id` - the id of the
movie session, returns `QuerySet` of tickets of the provided session.
3. `order.py`, add such functions:
   - `create_order`, takes `tickets` - list of the tickets, where each ticket 
is a dict with keys: row, seat, movie_session, `username` - username of the
user, optional `date`. This method should create an order with the provided user,
if `date` is provided, set `created_at` to this date. Then creates 
tickets with that order and data provided in `tickets`.
   ```python
   tickets: [
       {
           "row": 6,
           "seat": 12,
           "movie_session": 1
       },
       {
           "row": 6,
           "seat": 13,
           "movie_session": 1
       }
   ]
   create_order(tickets=tickets, username="Username_1", date="2022-4-20 11:27")
   ```
   - `get_orders`, takes optional `username`, if `username` is provided, returns
all orders for the user with the provided username, else returns all orders.
