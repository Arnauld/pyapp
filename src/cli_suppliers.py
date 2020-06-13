#!/usr/bin/env python3

from config import config
from db import DB
from db import load_commands
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
from time import sleep

import argparse

parser = argparse.ArgumentParser(description='Execute various command on the database')
parser.add_argument('--host', help="host section to use from 'database.ini'")
parser.add_argument('--db', help="db name to connect on")

# one of
parser.add_argument('--new_db', help="create database", action="store_true")
parser.add_argument('--generate', help="generate data", action="store_true")
#
parser.add_argument('--batch_delay', type=float, help="delay between batch in create in seconds")
parser.add_argument('--batch_sz', type=int, help="size of each batch")
parser.add_argument('--batch_nb', type=int, help="delay between batch in create in seconds")
args = parser.parse_args()
print(args)

# current date and time
now = datetime.now()
datetime_fmt = now.strftime("%Y%m%d_%H%M%S")

batch_delay_in_seconds = 1.0
if args.batch_delay:
    batch_delay_in_seconds = args.batch_delay
batch_sz = 10
if args.batch_sz:
    batch_sz = args.batch_sz
batch_nb = 10000
if args.batch_nb:
    batch_nb = args.batch_nb;

# read connection parameters
params = config(section=args.host)
db = DB(params)

def create_tables(db):
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE vendors (
            vendor_id SERIAL PRIMARY KEY,
            vendor_name VARCHAR(255) NOT NULL
        )
        """,
        """ CREATE TABLE parts (
                part_id SERIAL PRIMARY KEY,
                part_name VARCHAR(255) NOT NULL
                )
        """,
        """
        CREATE TABLE part_drawings (
                part_id INTEGER PRIMARY KEY,
                file_extension VARCHAR(5) NOT NULL,
                drawing_data BYTEA NOT NULL,
                FOREIGN KEY (part_id)
                REFERENCES parts (part_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE vendor_parts (
                vendor_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                PRIMARY KEY (vendor_id , part_id),
                FOREIGN KEY (vendor_id)
                    REFERENCES vendors (vendor_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (part_id)
                    REFERENCES parts (part_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
        )
        """)
    db.execute(commands)

def insert_vendor(cursor, vendor_name):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO vendors(vendor_name)
             VALUES(%s) RETURNING vendor_id;"""
    cursor.execute(sql, (vendor_name,))
    # get the generated id back
    vendor_id = cur.fetchone()[0]
    return vendor_id

def add_part(cursor, part_name, vendor_ids):
    # statement for inserting a new row into the parts table
    insert_part = "INSERT INTO parts(part_name) VALUES(%s) RETURNING part_id;"
    # statement for inserting a new row into the vendor_parts table
    assign_vendor = "INSERT INTO vendor_parts(vendor_id,part_id) VALUES(%s,%s)"

    # insert a new part
    cursor.execute(insert_part, (part_name,))
    # get the part id
    part_id = cursor.fetchone()[0]
    # assign parts provided by vendors
    for vendor_id in vendor_ids:
        cursor.execute(assign_vendor, (vendor_id, part_id))

if args.new_db:
    db.create_database(args.db)
    db.set_database(args.db)
    create_tables(db)

db.set_database(args.db)

def close(obj):
    try:
        if obj is not None:
            obj.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR!", error)

if args.generate:
    conn = None
    try:
        conn = db.connect()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        vendor_ids = []
        for i in range(0, batch_sz):
            vendor_ids.append(insert_vendor(cur, "vendor-{0}-{1}".format(datetime_fmt, i)))

        print("vendor ids: {0}".format(vendor_ids))

        error_nb = 0
        for i in range(0, batch_nb):
            print("Creating batch of 1+{0} elements {1}/{2} (delay {3}s, errors {4})".format(batch_sz, i, batch_nb, batch_delay_in_seconds, error_nb))
            try:
                if cur is None:
                    conn = db.connect()
                    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                    cur = conn.cursor()

                add_part(cur, "part-{0}-{1}".format(datetime_fmt, i), vendor_ids)
            except (Exception, psycopg2.DatabaseError, psycopg2.OperationalError) as error:
                print("ERROR!", error)
                error_nb = error_nb + 1
                close(cur)
                close(conn)
                cur = None


            sleep(batch_delay_in_seconds)

    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR!", error)
        raise error
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
