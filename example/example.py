import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import aiosql


class User(NamedTuple):
    userid: int
    username: str
    firstname: str
    lastname: str


class UserBlog(NamedTuple):
    blogid: int
    author: str
    title: str
    published: datetime

    def __post_init__(self):
        self.published = datetime.strptime(self.publised, "%Y-%m-%d %H:%M")


dir_path = Path(__file__).parent
sql_path = dir_path / "sql"
db_path = dir_path / "exampleblog.db"
queries = aiosql.from_path(
    dir_path / "sql", "sqlite3", record_classes={"User": User, "UserBlog": UserBlog}
)


users = [("bobsmith", "Bob", "Smith"), ("johndoe", "John", "Doe"), ("janedoe", "Jane", "Doe")]
blogs = [
    (
        1,
        "What I did Today",
        """\
I mowed the lawn, washed some clothes, and ate a burger.

Until next time,
Bob""",
        "2017-07-28",
    ),
    (
        3,
        "Testing",
        """\
Is this thing on?
""",
        "2018-01-01",
    ),
    (
        1,
        "How to make a pie.",
        """\
1. Make crust
2. Fill
3. Bake
4. Eat
""",
        "2018-11-23",
    ),
]


def createdb():
    conn = sqlite3.connect(dir_path / "exampleblog.db")
    print("Inserting users and blogs data.")
    with conn:
        queries.create_schema(conn)
        queries.users.insert_many(conn, users)
        queries.blogs.insert_many(conn, blogs)
    print("Done!")
    conn.close()


def deletedb():
    print(f"deleting the {db_path} file")
    if db_path.exists():
        db_path.unlink()


def get_users():
    conn = sqlite3.connect(dir_path / "exampleblog.db")
    for user in queries.users.get_all(conn):
        print(user)


def get_user_blogs(username):
    conn = sqlite3.connect(dir_path / "exampleblog.db")
    user_blogs = queries.blogs.get_user_blogs(conn, username=username)
    for user_blog in user_blogs:
        print("------")
        print(f'"{user_blog.title}"')
        print(f"by {user_blog.author} at {user_blog.published}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    createdb_parser = subparsers.add_parser("createdb")
    createdb_parser.set_defaults(cmd=createdb)

    deletedb_parser = subparsers.add_parser("deletedb")
    deletedb_parser.set_defaults(cmd=deletedb)

    get_users_parser = subparsers.add_parser("get-users")
    get_users_parser.set_defaults(cmd=get_users)

    get_user_blogs_parser = subparsers.add_parser("get-user-blogs")
    get_user_blogs_parser.add_argument("username")
    get_user_blogs_parser.set_defaults(cmd=get_user_blogs)

    args = parser.parse_args()
    cmd_kwargs = {k: v for k, v in vars(args).items() if k != "cmd"}
    args.cmd(**cmd_kwargs)
