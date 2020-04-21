import sqlite3
import os

# controller class for the database (I/O interface)
class DBConnect:
    def __init__(self, dbpath="history", dbfile="data.db"):
        os.makedirs(dbpath, exist_ok=True)
        self.dbpath = os.path.join(dbpath, dbfile)
        self.conn = sqlite3.connect(self.dbpath)

    # create tables if none exist
    def createTables(self):
        c = self.conn.cursor()
        create_names = "CREATE TABLE IF NOT EXISTS names  (" \
            "user_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
            "user_name varchar(30)); "
        create_merges = "CREATE TABLE IF NOT EXISTS merges (" \
            "merge_id int(16) PRIMARY KEY NOT NULL, " \
            "user_id int(3) NOT NULL, " \
            "time_stamp DATE, " \
            "FOREIGN KEY(user_id) REFERENCES names(user_id)); "
        create_files = "CREATE TABLE IF NOT EXISTS files  (" \
            "merge_id int(16) NOT NULL," \
            "templatefilename TEXT, " \
            "appendfilename TEXT, " \
            "outfilename TEXT, " \
            "FOREIGN KEY(merge_id) REFERENCES merges(merge_id));"

        c.execute(create_names)
        c.execute(create_merges)
        c.execute(create_files)

    # insert a dictionary into the table
    """
    format: {
                user_name: string
                timestamp: Date()
                file1: string
                file2: string
                outfile: string
                conflicts: int
            }
    """

    def insert_name(self, name):
        c = self.conn.cursor()
        sql = "INSERT INTO names (user_name) " \
              "SELECT (?) WHERE NOT EXISTS (SELECT 1 FROM names WHERE user_name=(?));"
        c.execute(sql, (name, name))
        self.conn.commit()

