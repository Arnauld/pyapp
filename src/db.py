import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def load_commands(filename):
    with open(filename, 'r') as content_file:
        content = content_file.read()
        return [x for x in content.split(";") if x.strip()]

class DB:
    def __init__(self, conf):
        self.conf = conf

    def connect(self):
        return psycopg2.connect(**self.conf)

    def create_database(self, db_name):
        conn = None
        try:
            conn = self.connect()
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        except (Exception, psycopg2.DatabaseError) as error:
            print("ERROR!")
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def set_database(self, db_name):
        self.conf['dbname'] = db_name

    def execute(self, commands):
        conn = None
        try:
            conn = self.connect()
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            rets = []
            for command in commands:
                rets.append(cur.execute(command))
            cur.close()
            return rets
        except (Exception, psycopg2.DatabaseError) as error:
            print("ERROR!")
            print(error)
            raise error
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

    def select(self, sql):
        conn = None
        try:
            conn = self.connect()
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(command)
            rets = cur.fetchall()
            cur.close()
            return rets
        except (Exception, psycopg2.DatabaseError) as error:
            print("ERROR!")
            print(error)
            raise error
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')
