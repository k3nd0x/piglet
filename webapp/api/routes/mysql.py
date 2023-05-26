from fastapi import HTTPException
import mysql.connector
import os

class sql:
    def __init__(self):
        try:
            if not os.environ.get("MYSQL_HOST"):
                host = "database"
            else:
                host = os.environ.get("MYSQL_HOST")
            if not os.environ.get("MYSQL_USER"):
                user = "piglet"
            else:
                user = os.environ.get("MYSQL_USER")

            if not os.environ.get("MYSQL_DATABASE"):
                database = "piglet"
            else:
                database = os.environ.get("MYSQL_DATABASE")

            self.db = mysql.connector.connect(
                host=host,
                user=user,
                password=os.environ.get("MYSQL_PASSWORD"),
                database=database
            )
        except:
            raise HTTPException(status_code=503, detail="Service Unavailable")

    def get(self, query):
        self.cursor = self.db.cursor(dictionary=True)
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        self.cursor.close()

        return data

    def delete(self, query):
        self.cursor = self.db.cursor(dictionary=True)
        try:
            self.cursor.execute(query)
            self.db.commit()
            self.cursor.close()
            data = "Entity deleted"
        except:
            data = { "Query":"Failed"}

        return data

    def post(self, query,close=True):
        self.cursor = self.db.cursor(dictionary=True)
        try:
            self.cursor.execute(query)
            self.db.commit()
            rows = self.cursor.rowcount
            if close:
                self.cursor.close()
        except mysql.connector.errors.IntegrityError:
            return "duplicated"

        if rows > 0:
            return True
        else:
            return False

    def fetchall(self):
        data = self.cursor.fetchall()
        self.cursor.close()
        return data

    def fetchone(self,query):
        self.cursor = self.db.cursor()
        self.cursor.execute(query)
        data = self.cursor.fetchone()
        self.cursor.close()
        return data

    def lastrowid(self):
        data = self.cursor.lastrowid
        self.cursor.close()
        return data

    def close(self):
        self.db.commit()
        self.db.close()
