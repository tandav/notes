# import requests
# import random
# from http import HTTPStatus
# from faker import Faker
# fake = Faker()
#
#
# API_URL = 'http://localhost:5003'
#
#
# def create_user(username: str, password: str) -> None:
#     r = requests.post(f'{API_URL}/users', json={
#         "username": username,
#         "password": password,
#     })
#     assert r.ok
#
#
# def create_users(n: int = 10) -> list[str]:
#     usernames = []
#     for _ in range(n):
#         username = fake.user_name()
#         password = fake.password(length=32, special_chars=False)
#         create_user(username, password)
#         usernames.append(username)
#     return usernames
#
#
# def create_notes(username: str, n: int = 100) -> None:
#     for _ in range(n):
#         r = requests.post(f'{API_URL}/users/{username}/notes/', json={
#             "title": fake.text(max_nb_chars=30),
#             "text": fake.text(max_nb_chars=200),
#             "is_bookmark": False,
#         })
#         assert r.ok
#
#
# def test_valid_bookmarks():
#     r = requests.post(f'{API_URL}/users/test_user/notes/', json={
#         "title": "test_title",
#         "text": 'http://example.com',
#         "is_bookmark": True,
#     })
#     assert r.ok
#
#     r = requests.post(f'{API_URL}/users/test_user/notes/', json={
#         "text": 'http://example.com',
#         "is_bookmark": True,
#     })
#     assert r.ok
#
#
# def test_invalid_bookmarls():
#     r = requests.post(f'{API_URL}/users/test_user/notes/', json={
#         "is_bookmark": True,
#     })
#     assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
#
#     r = requests.post(f'{API_URL}/users/test_user/notes/', json={
#         "text": 'broken-link',
#         "is_bookmark": True,
#     })
#     assert r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
#
#
# if __name__ == '__main__':
#     usernames = create_users()
#     create_user('test_user', 'test_password')
#
#     for username in usernames:
#         create_notes(username, n = random.randint(0, 20))
#
#     test_valid_bookmarks()
#     test_invalid_bookmarls()


from notes import models
from notes import database


def main():


if __name__ == '__main__':
    main()
