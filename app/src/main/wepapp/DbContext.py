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
                               "`Age` INT NOT NULL,"
                               "`Contact` VARCHAR(8) NOT NULL,"
                               "`Password` LONGTEXT NOT NULL,"
                               "`PwdSalt` VARCHAR(8) NOT NULL,"
                               "PRIMARY KEY (`Id`));")
                # User preferences table
                cursor.execute("CREATE TABLE IF NOT EXISTS `Preferences` ("
                                "`RowId` INT NOT NULL AUTO_INCREMENT,"
                                "`UserId` INT NOT NULL,"
                                "`Preference` VARCHAR(50) NOT NULL,"
                                "`Category` VARCHAR(50) NOT NULL,"
                                "PRIMARY KEY (`RowId`),"
                                "FOREIGN KEY (`UserId`) REFERENCES Users(`Id`));")
                # Shop points
                cursor.execute("CREATE TABLE IF NOT EXISTS `ShopPoints` ("
                                "`Address` VARCHAR(150) NOT NULL,"
                                "`UnitNo` VARCHAR(20) NOT NULL,"
                                "`ShopName` VARCHAR(100) NOT NULL,"
                                "`Points` INT NULL,"
                                "PRIMARY KEY (`Address`, `UnitNo`));")
                # User points table
                cursor.execute("CREATE TABLE IF NOT EXISTS `UserPoints` ("
                                "`UserId` INT NOT NULL,"
                                "`Points` INT NULL,"
                                "`Tier` VARCHAR(10) NOT NULL DEFAULT \"Bronze\","
                                "PRIMARY KEY (`UserId`),"
                                "FOREIGN KEY (`UserId`) REFERENCES Users(`Id`));")
                # Itinerary table
                cursor.execute("CREATE TABLE IF NOT EXISTS `Itineraries` ("
                                "`UserId` INT NOT NULL,"
                                "`Date` DATE NULL,"
                                "`Address` VARCHAR(150) NOT NULL,"
                                "`Order` INT NOT NULL,"
                                "`Status` VARCHAR(15) NOT NULL,"
                                "PRIMARY KEY(`UserId`),"
                                "FOREIGN KEY (`UserId`) REFERENCES Users(`Id`));")
                # Tracked places table
                cursor.execute("CREATE TABLE IF NOT EXISTS `TrackedPlaces` ("
                                "`RowId` INT NOT NULL AUTO_INCREMENT,"
                                "`UserId` INT NOT NULL,"
                                "`Address` VARCHAR(150) NOT NULL,"
                                "`StoreMean` VARCHAR(20) NOT NULL,"
                                "`Frequency` INT NOT NULL,"
                                "`LastRegistered` DATE NULL,"
                                "PRIMARY KEY (`RowId`),"
                                "FOREIGN KEY (`UserId`) REFERENCES Users(`Id`));")
                return db

    except Exception as e:
        msg = e

    @staticmethod
    def Close(self, con):
        con.Close()


MySql.Connect()
print(MySql.msg)
