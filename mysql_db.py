import sys
import os
import mysql
import mysql.connector 

INSERT_DIC = {
    "insertUsers"    : "INSERT INTO users(userId,cmkId)                          VALUES(%s,%s)",
    "insertOngUp"    : "INSERT INTO ongoingUploads(fileId, uploaderId, nonce)    VALUES(%s,%s,%s)",
    "insertCompUp"   : "INSERT INTO completedUploads(fileId, uploaderId, filepath, nro, abort) VALUES(%s,%s,%s,%s,%s)",
    "insertOngDown"  : "INSERT INTO ongoingDownloads(downloadId, downloaderId, fileId, nonce) VALUES(%s,%s,%s,%s)",
    "insertCompDown" : "INSERT INTO completedDownloads(downloadId, downloaderId, fileId, nrr) VALUES(%s,%s,%s,%s)"
}

class MySQL_DB(object):

    def __init__(self):
        self.conn = mysql.connector.connect(host="my_db_host", port="3306",
        database="my_db_name_to_connect", user="admin", password="admin1111")
        self.cur = self.conn.cursor()

    def __create_tables__(self):
        tables = (
            """
            CREATE TABLE users (
                userId INTEGER PRIMARY KEY,
                cmkId VARCHAR(255) NOT NULL
            )
            """,
            """ 
            CREATE TABLE ongoingUploads (
                fileId INTEGER PRIMARY KEY,
                uploaderId INTEGER NOT NULL,
                nonce VARCHAR(255) NOT NULL,
                    FOREIGN KEY(uploaderId)
                        REFERENCES users(userId)
            )
            """,
            """ 
            CREATE TABLE completedUploads (
                fileId INTEGER PRIMARY KEY,
                uploaderId INTEGER NOT NULL,
                filepath VARCHAR(255) NOT NULL,
                nro VARCHAR(255) NOT NULL,
                abort INTEGER NOT NULL,
                    FOREIGN KEY(uploaderId)
                        REFERENCES users(userId)
                        ON UPDATE CASCADE ON DELETE CASCADE
            )
            """,
            """ 
            CREATE TABLE ongoingDownloads (
                downloadId   VARCHAR(255) PRIMARY KEY,
                downloaderId INTEGER NOT NULL,
                fileId       INTEGER NOT NULL,
                nonce        VARCHAR(255) NOT NULL,
                    FOREIGN KEY(downloaderId)
                        REFERENCES users(userId)
            )
            """,
            """ 
            CREATE TABLE completedDownloads (
                downloadId   VARCHAR(255) PRIMARY KEY,
                downloaderId INTEGER NOT NULL,
                fileId       INTEGER NOT NULL,
                nrr          VARCHAR(255) NOT NULL,
                    FOREIGN KEY(downloaderId)
                        REFERENCES users(userId)
                        ON UPDATE CASCADE ON DELETE CASCADE,
                    FOREIGN KEY(fileId)
                        REFERENCES completedUploads(fileId)
                        ON UPDATE CASCADE ON DELETE CASCADE
            )
            """)
        for table in tables:
            self.cur.execute(table)

        # commit the changes
        self.conn.commit()

    def __reset__(self):
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        self.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s", ("mysqldata",))
        rows = self.cur.fetchall()
        for row in rows:
            print("drop table " + row[0].decode())
            self.cur.execute("DROP TABLE " + row[0].decode() + " cascade")   
        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        self.conn.commit()

    def insert_into(self, query, params):
        try:
            response = self.cur.execute(INSERT_DIC[query], params)
            self.conn.commit()
            return response
        except mysql.connector.Error as error:
            print(error)
            return -1

    def get_record(self, attribute, sum = -1):
        """
            Returns all records that matches the given attribute.
            If sum = -1 return all records. Change value to the sum of record you want to be returned
        """
        try:
            self.cur.execute("SELECT users.cmkid FROM users WHERE userid = %s",[attribute])
            record = self.cur.fetchall() 
            if sum == -1:
                return record
            else:
                if (len(record) <= sum):
                    return record
                else:
                    return record[:sum]
        except mysql.connector.Error as error:
            print(error)
            return -1
        return None

    def get_attribute(self, userId):
        """
            Returns a specific value from a record.
        """
        try:
            self.cur.execute("SELECT users.cmkid FROM users WHERE userid = %s",[userId])
            record = self.cur.fetchall() 
            if (len(record) == 1):
                return record[0][0] # record = [('Nro',)]
            return None
        except mysql.connector.Error as error:
            print(error)
            return -1
        return None

    def record_exists(self,attribute):
        """
            Returns true if there is a record with the specified attribute otherwise returns false
        """
        try:
            self.cur.execute("SELECT * FROM ongoingUploads WHERE fileid = %s",[attribute])
            if (self.cur.fetchall()):
                return True
            else:
                return False
        except mysql.connector.Error as error:
            print(error)
            return -1

    def delete_record(self,attribute):
        """
        Deletes a record from table with specified attribute
        """
        try:
            self.cur.execute("DELETE FROM ongoingUploads WHERE fileid = %s",(attribute,))
            self.conn.commit()
            return 0
        except mysql.connector.Error as error:
            print(error)
            return -1

if __name__ == "__main__":
    db = MySQL_DB()

    if (len(sys.argv) > 1):
        if (sys.argv[1] == "restart"):
            db.__reset__()
            db.__create_tables__()
            print("Tables recreated")
            exit()
        elif (sys.argv[1] == "reset"):
            db.__reset__()
            print("Tables deleted")
            exit()
        elif (sys.argv[1] == "init"):
            db.__create_tables__()
            print("Tables created")
            exit()
        elif (sys.argv[1] == "insert"):
            for x in range(10,20):
                db.insert_into("insertUsers",(x,"4161616161",)) #uploader
                db.insert_into("insertUsers",(x+10,"4161611551",)) #downloaders
                db.insert_into("insertOngUp",(x+30,x,"nonceAAAD"))
                db.insert_into("insertOngDown",(str(x)+"_"+str(x+30),x,x+30,"noncebbb"))
            print("Insertion completed")
            exit()
        elif (sys.argv[1] == "exists"):
            print(db.record_exists(41))
            exit()
        elif (sys.argv[1] == "get"):
            print(db.get_record(10))
            exit()
        elif (sys.argv[1] == "del"):
            print(db.delete_record(10))
            exit()
