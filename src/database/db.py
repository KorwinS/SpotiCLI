import sqlite3
from next_track import next_track


class Database:
    def __init__(self, name=None):
        self.conn = None
        self.cursor = None

        if name:
            self.open(name)

    def open(self, name):
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()

        except sqlite3.Error as e:
            print("Error connecting to database!")

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get(self, table, columns, limit=None):
        query = "SELECT {0} from {1};".format(columns, table)
        self.cursor.execute(query)

        # fetch data
        rows = self.cursor.fetchall()

        return rows[len(rows) - limit if limit else 0 :]

    def execute(self, sql, params=None or ()):
        return self.cursor.execute(sql, params)

    def write(self, table, data):
        return self.cursor.execute(f"INSERT INTO {table} VALUES(?, ?, ?)", data)

    def getLast(self, table, columns):
        return self.get(table, columns, limit=1)[0]

    @staticmethod
    def toCSV(data, fname="output.csv"):
        with open(fname, "a") as file:
            file.write(",".join([str(j) for i in data for j in i]))


# table = "spotify"

# with Database("my_db.db") as db:
# data = next_track.CLISpotify().status()
# db.write(table=table, data=data)
# # db.execute(f"INSERT INTO {table} VALUES(?, ?, ?)", data)

# q = db.get(table="spotify", columns="track,artist")
# for i in q:
#     print(i[0], i[1])
