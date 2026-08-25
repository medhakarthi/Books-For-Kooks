#!/usr/bin/env python3
"""Import books_data.csv and Books_rating.csv into books.db.

Designed for a ~2.7 GB ratings CSV: streams rows, inserts in batches, and
does not load the whole file into memory.
"""

import argparse
import csv
import os
import sqlite3
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT, "books.db")
BOOKS_CSV = os.path.join(ROOT, "books_data.csv")
RATINGS_CSV = os.path.join(ROOT, "Books_rating.csv")

BATCH_SIZE = 10000
PROGRESS_EVERY = 100000
MAX_ERROR_PRINT = 20

BOOK_COLUMNS = [
    "Title",
    "description",
    "authors",
    "image",
    "previewLink",
    "publisher",
    "publishedDate",
    "infoLink",
    "categories",
    "ratingsCount",
]

RATING_COLUMNS = [
    "Id",
    "Title",
    "Price",
    "User_id",
    "profileName",
    "review/helpfulness",
    "review/score",
    "review/time",
    "review/summary",
    "review/text",
]

INSERT_BOOKS = (
    "INSERT INTO bookdetails ("
    "Title, description, authors, image, previewLink, publisher, "
    "publishedDate, infoLink, categories, ratingsCount"
    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)

INSERT_RATINGS = (
    'INSERT INTO bookratings ('
    'Id, Title, Price, User_id, profileName, '
    '"review/helpfulness", "review/score", "review/time", '
    '"review/summary", "review/text"'
    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_bookdetails_title_authors ON bookdetails(Title, authors)",
    "CREATE INDEX IF NOT EXISTS idx_bookratings_title ON bookratings(Title)",
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
    "CREATE INDEX IF NOT EXISTS idx_bookshelf_user_id ON bookshelf(user_id)",
]


def raise_csv_field_limit():
    max_int = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_int)
            return
        except OverflowError:
            max_int = int(max_int / 10)


class NulSafeReader:
    """Yield file lines with NUL bytes stripped so csv.reader does not crash."""

    def __init__(self, file_obj):
        self.file_obj = file_obj

    def __iter__(self):
        for line in self.file_obj:
            yield line.replace("\x00", "")


def table_count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def confirm_import(table, count, args):
    """Return True to import, False to skip. May clear the table first."""
    if count == 0:
        return True

    print(f"{table} already contains {count:,} rows.")
    print("Re-importing without clearing would duplicate data.")

    if args.skip_if_populated:
        print(f"Skipping {table} (--skip-if-populated).")
        return False

    if args.reimport:
        if not args.yes:
            answer = input(
                f"Delete all rows in {table} and reimport? [y/N] "
            ).strip().lower()
            if answer not in ("y", "yes"):
                print(f"Skipping {table}.")
                return False
        print(f"Clearing {table} ...")
        conn = args._conn
        conn.execute(f"DELETE FROM {table}")
        conn.commit()
        return True

    if args.yes:
        print(f"Skipping {table} (populated; pass --reimport to replace).")
        return False

    answer = input(
        f"{table} is populated. [s]kip, [r]eimport (wipe then import), [q]uit? "
    ).strip().lower()
    if answer in ("r", "reimport"):
        print(f"Clearing {table} ...")
        args._conn.execute(f"DELETE FROM {table}")
        args._conn.commit()
        return True
    if answer in ("q", "quit"):
        print("Aborted.")
        sys.exit(0)
    print(f"Skipping {table}.")
    return False


def import_table(conn, csv_path, table, columns, insert_sql, label):
    if not os.path.exists(csv_path):
        raise SystemExit(f"CSV not found: {csv_path}")

    print(f"Importing {os.path.basename(csv_path)} -> {table} ...")
    started = time.time()
    batch = []
    inserted = 0
    skipped = 0
    error_prints = 0

    def flush():
        nonlocal inserted
        if not batch:
            return
        conn.executemany(insert_sql, batch)
        conn.commit()
        inserted += len(batch)
        batch.clear()

    with open(csv_path, "r", encoding="utf-8", errors="replace", newline="") as raw:
        reader = csv.reader(NulSafeReader(raw))
        try:
            headers = next(reader)
        except StopIteration:
            print(f"CSV is empty: {csv_path}")
            return 0, 0

        header_index = {name: i for i, name in enumerate(headers)}
        missing = [col for col in columns if col not in header_index]
        if missing:
            raise SystemExit(
                f"{os.path.basename(csv_path)} is missing expected columns: {missing}"
            )

        extra = [h for h in headers if h not in columns]
        if extra:
            print(f"  Note: ignoring extra CSV columns: {extra}")

        line_no = 1
        while True:
            line_no += 1
            try:
                row = next(reader)
            except StopIteration:
                break
            except csv.Error as exc:
                skipped += 1
                if error_prints < MAX_ERROR_PRINT:
                    print(f"  Skipping row {line_no}: {exc}")
                    error_prints += 1
                continue

            if not row or all(not (cell or "").strip() for cell in row):
                continue

            try:
                values = []
                for col in columns:
                    idx = header_index[col]
                    values.append(row[idx] if idx < len(row) else "")
                batch.append(tuple(values))
            except Exception as exc:
                skipped += 1
                if error_prints < MAX_ERROR_PRINT:
                    print(f"  Skipping row {line_no}: {exc}")
                    error_prints += 1
                continue

            if len(batch) >= BATCH_SIZE:
                flush()
                if inserted % PROGRESS_EVERY < BATCH_SIZE:
                    elapsed = time.time() - started
                    print(f"Imported {inserted:,} {label}... ({elapsed:.1f}s)")

        flush()

    elapsed = time.time() - started
    print(
        f"Finished {table}: {inserted:,} rows inserted, "
        f"{skipped:,} skipped ({elapsed:.1f}s)"
    )
    return inserted, skipped


def configure_bulk_pragmas(conn):
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = OFF")
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA cache_size = -131072")  # 128 MiB
    conn.execute("PRAGMA foreign_keys = OFF")


def restore_pragmas(conn):
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA foreign_keys = ON")


def create_indexes(conn):
    print("Creating indexes ...")
    started = time.time()
    for sql in INDEXES:
        conn.execute(sql)
    conn.commit()
    print(f"Indexes ready ({time.time() - started:.1f}s)")
    print("Running ANALYZE ...")
    conn.execute("ANALYZE")
    conn.commit()
    print("ANALYZE complete.")


def print_summary(conn):
    print()
    print("Database summary:")
    for table in ("bookdetails", "bookratings", "users", "bookshelf"):
        print(f"  {table}: {table_count(conn, table):,} rows")


def main():
    # So progress lines show up immediately when stdout is not a TTY.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="Import CSV book and ratings data into books.db."
    )
    parser.add_argument(
        "--skip-if-populated",
        action="store_true",
        help="Skip a table if it already has rows.",
    )
    parser.add_argument(
        "--reimport",
        action="store_true",
        help="Wipe destination tables and reimport (asks unless --yes).",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Do not prompt. Combined with --reimport, wipes without asking.",
    )
    parser.add_argument(
        "--indexes-only",
        action="store_true",
        help="Only create indexes and run ANALYZE; do not import.",
    )
    args = parser.parse_args()

    if not os.path.exists(DB_PATH):
        raise SystemExit(
            f"{DB_PATH} not found. Run first:\n  python3 create_database.py"
        )

    raise_csv_field_limit()

    conn = sqlite3.connect(DB_PATH)
    args._conn = conn
    try:
        configure_bulk_pragmas(conn)

        if not args.indexes_only:
            book_count = table_count(conn, "bookdetails")
            if confirm_import("bookdetails", book_count, args):
                import_table(
                    conn,
                    BOOKS_CSV,
                    "bookdetails",
                    BOOK_COLUMNS,
                    INSERT_BOOKS,
                    "books",
                )

            rating_count = table_count(conn, "bookratings")
            if confirm_import("bookratings", rating_count, args):
                print(
                    "Importing ratings (this file is ~2.7 GB and may take "
                    "several minutes to tens of minutes) ..."
                )
                import_table(
                    conn,
                    RATINGS_CSV,
                    "bookratings",
                    RATING_COLUMNS,
                    INSERT_RATINGS,
                    "ratings",
                )

        create_indexes(conn)
        restore_pragmas(conn)
        print_summary(conn)
    finally:
        conn.close()

    print("Done.")


if __name__ == "__main__":
    main()
