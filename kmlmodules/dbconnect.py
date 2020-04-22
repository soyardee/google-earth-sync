import sqlite3
import os
from datetime import datetime


# controller class for the database (I/O interface)
class DBConnect:
    def __init__(self, dbfile, dbpath="history"):
        os.makedirs(dbpath, exist_ok=True)
        self.dbpath = os.path.join(dbpath, dbfile)
        self.conn = sqlite3.connect(self.dbpath)
        self.createTables()
        self.conn.close()

    # create tables if none exist
    def createTables(self):
        c = self.conn.cursor()
        create_names = "CREATE TABLE IF NOT EXISTS names  (" \
                       "user_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                       "user_name varchar(30)); "
        create_files = "CREATE TABLE IF NOT EXISTS files  (" \
                       "files_id INTEGER PRIMARY KEY AUTOINCREMENT," \
                       "templatefilename TEXT, " \
                       "appendfilename TEXT, " \
                       "outfilename TEXT);"
        create_merges = "CREATE TABLE IF NOT EXISTS merges (" \
                        "merge_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                        "user_id INTEGER NOT NULL, " \
                        "files_id INTEGER NOT NULL, " \
                        "time_stamp TIMESTAMP, " \
                        "conflicts INTEGER, " \
                        "FOREIGN KEY(user_id) REFERENCES names(user_id)" \
                        "FOREIGN KEY(files_id) REFERENCES files(files_id)); "

        # this order is important
        c.execute(create_names)
        c.execute(create_files)
        c.execute(create_merges)
        c.close()

    # inserts a new user into the user table, if they don't already exist.
    def insert_name(self, name):
        c = self.conn.cursor()
        sql = "INSERT INTO names (user_name) " \
              "SELECT (?) WHERE NOT EXISTS (SELECT 1 FROM names WHERE user_name=(?));"
        c.execute(sql, (name, name))
        self.conn.commit()
        self.conn.cursor().close()

    # gets the primary key of the user. Could be refactored into better sql, but this functions as expected.
    def get_user_id(self, name):
        c = self.conn.cursor()
        sql = "SELECT user_id FROM names WHERE user_name=?;"
        c.execute(sql, (name,))
        row = c.fetchone()
        self.conn.cursor().close()
        if row is None:
            return None
        else:
            return row[0]

    # helper method to populate the files table
    def insert_files(self, infile1, infile2, outfile):
        c = self.conn.cursor()
        sql = "INSERT INTO files (templatefilename, appendfilename, outfilename) VALUES (?, ?, ?);"
        c.execute(sql, (infile1, infile2, outfile))
        self.conn.commit()
        c.execute("SELECT last_insert_rowid();")
        file_id_out = c.fetchone()
        c.close()
        return file_id_out[0]

    # the main database insertion method
    def insert_history(self, user_name, conflicts, file1name, file2name, outfilename):
        self.conn = sqlite3.connect(self.dbpath)
        c = self.conn.cursor()
        sql = "INSERT INTO merges (user_id, files_id, time_stamp, conflicts) VALUES (?, ?, ?, ?);"
        self.insert_name(user_name)
        user_id = self.get_user_id(user_name)
        file_id = self.insert_files(file1name, file2name, outfilename)
        now = datetime.now()
        c.execute(sql, (user_id, file_id, now, conflicts))
        self.conn.commit()
        c.close()
        self.conn.close()

    # returns a list of tuples with all attributes required (non-configurable at the moment).
    def get_history_rows(self):
        self.conn = sqlite3.connect(self.dbpath)
        c = self.conn.cursor()
        sql = "SELECT " \
              "merges.time_stamp, " \
              "names.user_name, " \
              "merges.conflicts, " \
              "files.templatefilename, " \
              "files.appendfilename " \
              "FROM merges " \
              "INNER JOIN names ON merges.user_id = names.user_id " \
              "INNER JOIN files ON merges.files_id = files.files_id " \
              "ORDER BY time_stamp DESC;"

        c.execute(sql)
        rows = c.fetchall()
        self.conn.close()
        return rows
