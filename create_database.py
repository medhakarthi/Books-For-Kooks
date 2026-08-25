#!/usr/bin/env python3
"""Create books.db with the schema expected by app.py.

Does not insert users, reviews, or bookshelf rows.
Does not import CSV data — run import_data.py for that.
"""

import argparse
import os
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "books.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookdetails (
    Title TEXT,
    description TEXT,
    authors TEXT,
    image TEXT,
    previewLink TEXT,
    publisher TEXT,
    publishedDate TEXT,
    infoLink TEXT,
    categories TEXT,
    ratingsCount TEXT
);

CREATE TABLE IF NOT EXISTS bookratings (
    Id TEXT,
    Title TEXT,
    Price TEXT,
    User_id TEXT,
    profileName TEXT,
    "review/helpfulness" TEXT,
    "review/score" TEXT,
    "review/time" TEXT,
    "review/summary" TEXT,
    "review/text" TEXT
);

CREATE TABLE IF NOT EXISTS bookshelf (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT,
    author TEXT,
    status TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""


def main():
    parser = argparse.ArgumentParser(description="Create books.db schema.")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Continue without prompting if books.db already exists.",
    )
    args = parser.parse_args()

    if os.path.exists(DB_PATH):
        print(f"WARNING: {DB_PATH} already exists.")
        print("This script will NOT delete it.")
        print("It only runs CREATE TABLE IF NOT EXISTS (existing data is kept).")
        if not args.yes:
            answer = input("Continue? [y/N] ").strip().lower()
            if answer not in ("y", "yes"):
                print("Aborted.")
                sys.exit(0)
    else:
        print(f"Creating {DB_PATH} ...")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()

    print("Created tables (if they did not already exist):")
    print("  users")
    print("  bookdetails")
    print("  bookshelf")
    print("  bookratings")
    print("users and bookshelf start empty. Import book data with: python3 import_data.py")


if __name__ == "__main__":
    main()
