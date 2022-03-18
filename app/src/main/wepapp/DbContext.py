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

                # User table
                cursor.execute("CREATE TABLE IF NOT EXISTS `Users` ("
                               "`Id` INT NOT NULL AUTO_INCREMENT, "
                               "`Username` VARCHAR(50) NOT NULL,"
                               "`Email` VARCHAR(100) NOT NULL,"
                               "`Contact` VARCHAR(8) NOT NULL,"
                               "`Password` LONGTEXT NOT NULL,"
                               "`PwdSalt` VARCHAR(8) NOT NULL,"
                               "PRIMARY KEY (`Id`));")
                # Tracked Places table
                cursor.execute("CREATE TABLE IF NOT EXISTS `TrackedPlaces` ("
                                "`RowId` INT NOT NULL AUTO_INCREMENT,"
                                "`UserId` INT NOT NULL,"
                                "`Address` VARCHAR(150) NOT NULL,"
                                "`StoreMean` VARCHAR(20) NOT NULL,"
                                "`Frequency` INT NOT NULL,"
                                "`LastRegistered` DATE NULL,"
                                "PRIMARY KEY (`RowId`),"
                                "FOREIGN KEY (`UserId`) REFERENCES Users(`Id`)"
                                ");")
                return db

    except Exception as e:
        msg = e

    @staticmethod
    def Close(self, con):
        con.Close()


MySql.Connect()
print(MySql.msg)
