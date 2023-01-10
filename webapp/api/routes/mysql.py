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

    def fetchone(self):
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



#def session():
#    try:
#        mydb = mysql.connector.connect(
#            host="db",
#            user="piglet",
#            password="FLASK_budget2PW!",
#            database="piglet"
#        )
#    except:
#        return False, "MYSQL not available"
#
#    return mydb
#
#def get(query):
#    mydb = session()
#    cursor = mydb.cursor(dictionary=True)
#    cursor.execute(query)
#
#    row = cursor.fetchall()
#
#    cursor.close()
#    mydb.close()
#
#    return row
#
#def post(query,mode=""):
#    mydb = session()
#    if mode == "":
#        try:
#            cursor = mydb.cursor(dictionary=True)
#            cursor.execute(query)
#
#            mydb.commit()
#            response = True
#            cursor.close()
#            mydb.close()
#        except: 
#            response = False
#
#        return response
#
#    elif mode == "register":
#        try:
#            cursor = mydb.cursor(dictionary=True)
#            cursor.execute(query)
#            mydb.commit()
#            
#            rows = cursor.rowcount
#
#            cursor.close()
#        except mysql.connector.errors.IntegrityError as IntegrityError:
#            return "duplicated"
#        except mysql.connector.Error as error:
#            return { "Connection to mysql": "Failed" }
#        mydb.close()
#
#        if rows > 0:
#            return "added"
#        else:
#            return "failed"
#    elif mode == "budget_id":
#        try:
#            cursor = mydb.cursor(dictionary=True)
#            cursor.execute(query)
#            mydb.commit()
#            
#            rows = cursor.rowcount
#            budget_id = cursor.lastrowid
#
#            cursor.close()
#        except mysql.connector.errors.IntegrityError as IntegrityError:
#            return "duplicated"
#        except mysql.connector.Error as error:
#            return { "Connection to mysql": "Failed" }
#        mydb.close()
#
#
#        if rows > 0:
#            return str(budget_id)
#        else:
#            return "500"
#
#def delete(query):
#    mydb = session()
#    try:
#        cursor = mydb.cursor()
#        cursor.execute(query)
#        mydb.commit()
#
#        row = "Entity deleted"
#
#    except:
#        row = { "Query":"Failed"}
#
#    return row
