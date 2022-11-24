'''
Basic Usage
python3 db.py --create
python3 db.py --insert --location test --content donkey
python3 db.py --getLocations
python3 db.py --get --location test
'''
import sqlite3
import argparse
import os
from typing import Tuple

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def create_db(conn):
    createContentTable="""CREATE TABLE IF NOT EXISTS content (
            id integer PRIMARY KEY,
            location text NOT NULL,
            content blob);"""
    try:
        c = conn.cursor()
        c.execute(createContentTable)
    except Error as e:
        print(e)
def insert_content(conn, data:Tuple[str,str]):
    sql = ''' INSERT INTO content(location,content)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    return cur.lastrowid
def get_content(conn, data:Tuple[str]):
    sql = """SELECT content 
            FROM content 
            WHERE location = ? 
            """
    cur = conn.cursor()
    cur.execute(sql, data)
    row = cur.fetchone()
    return row[0]
def get_locations(conn):
    sql = """SELECT DISTINCT location 
             FROM content"""
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    return rows
if __name__ == "__main__":
    database = r"sqlite.db"
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--create','-c', help='Create Database', action='store_true')
    group.add_argument('--insert','-i', help='Insert Content', action='store_true')
    group.add_argument('--get','-g', help='Get Content', action='store_true')
    group.add_argument('--getLocations','-l', help='Get all Locations', action='store_true')

    parser.add_argument('--location','-L')
    parser.add_argument('--content','-C')
    args = parser.parse_args()
    conn = create_connection(database)

    if (args.create):
        print("[+] Creating Database")
        create_db(conn)
    elif (args.insert):
        if(args.location is None and args.content is None):
            parser.error("--insert requires --location, --content.")
        else:
            print("[+] Inserting Data")
            insert_content(conn, (args.location, args.content))
            conn.commit()
    elif (args.get):
        if(args.location is None):
            parser.error("--get requires --location, --content.")
        else:
            print("[+] Getting Content")
            print(get_content(conn, (args.location,)))
    if (args.getLocations):
        print("[+] Getting All Locations")
        print(get_locations(conn))