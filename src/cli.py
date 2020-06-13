#!/usr/bin/env python3

from config import config
from db import DB
from db import load_commands
import argparse

parser = argparse.ArgumentParser(description='Execute various command on the database')
parser.add_argument('--host', help="host section to use from 'database.ini'")
# one of
parser.add_argument('--db', help='db name to connect on')
parser.add_argument('--script', help='script file to execute')
parser.add_argument('--mode', help='select script file to execute')
parser.add_argument('--new_db', help="create a new database")
args = parser.parse_args()
print(args)

def execute():
    # read connection parameters
    params = config(section=args.host)
    db = DB(params)

    # connect to the PostgreSQL server
    if args.new_db:
        db.create_database(args.new_db)
    else:
        db.set_database(args.db)
        commands = load_commands(args.script)
        if args.mode == "select":
            rets = db.select(commands)
            print(rets)
        else:
            rets = db.execute(commands)
            print(rets)

if __name__ == '__main__':
    execute()
