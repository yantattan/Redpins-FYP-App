import mysql.connector as mySqlDB


class MySql:
    msg = ""

    try:
        @staticmethod
        def Connect():
            db = mySqlDB.connect(
                host="localhost",
                user="root",
                password="password",
                database="redpinsdb"
            )

            cursor = db.cursor()
            cursor.execute("CREATE SCHEMA IF NOT EXISTS redpinsdb")

            if db.is_connected():
                msg = "DB Connected"
                cursor.execute("CREATE TABLE IF NOT EXISTS `Users` ("
                               "`Id` INT NOT NULL AUTO_INCREMENT, "
                               "`Username` VARCHAR(50) NOT NULL,"
                               "`Contact` VARCHAR(8) NOT NULL,"
                               "`Password` LONGTEXT NOT NULL,"
                               "`PwdSalt` VARCHAR(8) NOT NULL,"
                               "PRIMARY KEY (`Id`));")
                return db

    except Exception as e:
        msg = e

    @staticmethod
    def Close(self, con):
        con.Close()


MySql.Connect()
print(MySql.msg)
