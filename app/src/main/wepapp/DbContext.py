import hashlib
import mysql.connector as mySqlDB
from pymongo import MongoClient
import random
import string


class MongoDBContext:
    def Connect():
        con = MongoClient("mongodb://localhost:27017")
        db = con["RedpinsBufferDB"]
        return db

    def SetCollectionsAndRoot():
        # Set root account
        db = MongoDBContext.Connect()

        # Create collections
        userDb = db["Users"]
        partneredPlacesDb = db["PartneredPlaces"]
        placesBonusCodesDb = db["PlacesBonusCodes"]
        placesBonusCodesDb.create_index("Timestamp", expireAfterSeconds=1800)
        machineLearningReportDb = db["MachineLearningReports"]
        
        try:
            passwordSalt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            passwordHash = hashlib.sha512(("P@ssw0rd" + passwordSalt).encode("utf-8")).hexdigest()

            userDb.insert_one({"_id": 0,
                                "Username": "Root", 
                                "Email": "redpinsbuffer@gmail.com", 
                                "Role": "Admin", 
                                "DateOfBirth": "2001-01-01", 
                                "Contact": "00000000", 
                                "Password": passwordHash,
                                "PasswordSalt": passwordSalt,
                                "Points": 9999999999,
                                "Tier": "Diamond"})
                                
            print("Root account has been created")
        except Exception:
            print("Root account in database")


MongoDBContext.SetCollectionsAndRoot()



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
                               "`Username` VARCHAR(50) NOT NULL Unique,"
                               "`Email` VARCHAR(100) NOT NULL Unique,"
                               "`Role` VARCHAR(20) NOT NULL DEFAULT \"User\","
                               "`DateOfBirth` DATE NOT NULL,"
                               "`Contact` VARCHAR(8) NOT NULL,"
                               "`Password` LONGTEXT NOT NULL,"
                               "`PwdSalt` VARCHAR(8) NOT NULL,"
                               "CHECK (`Role` in (\"User\", \"Admin\")),"
                               "UNIQUE (`Username`, `Email`),"
                               "PRIMARY KEY (`Id`));")
                # User preferences table
                cursor.execute("CREATE TABLE IF NOT EXISTS `Preferences` ("
                                "`RowId` INT NOT NULL AUTO_INCREMENT,"
                                "`UserId` INT NOT NULL,"
                                "`Preference` VARCHAR(50) NOT NULL,"
                                "`Category` VARCHAR(50) NOT NULL,"
                                "CHECK (`Category` in (\"Cuisine\", \"Activity\")),"
                                "PRIMARY KEY (`RowId`),"
                                "FOREIGN KEY (`UserId`) REFERENCES Users(`Id`));")
                # Shop points
                cursor.execute("CREATE TABLE IF NOT EXISTS `SignedPlaces` ("
                                "`Id` INT NOT NULL AUTO_INCREMENT,"
                                "`Address` VARCHAR(150) NOT NULL,"
                                "`UnitNo` VARCHAR(20) NOT NULL,"
                                "`ShopName` VARCHAR(100) NOT NULL,"
                                "`Organization` VARCHAR(100) NOT NULL,"
                                "`Points` INT NULL,"
                                "`Checkpoint` INT NULL,"
                                "`Discount` DECIMAL(4, 2) NULL,"
                                "PRIMARY KEY (`Id`));")
                # User points table
                cursor.execute("CREATE TABLE IF NOT EXISTS `UserPoints` ("
                                "`UserId` INT NOT NULL,"
                                "`Points` INT NULL,"
                                "`Tier` VARCHAR(10) NOT NULL DEFAULT \"Bronze\","
                                "CHECK (`Tier` in ('Bronze', 'Silver', 'Gold', 'Platinium', 'Diamond')),"
                                "PRIMARY KEY (`UserId`),"
                                "FOREIGN KEY (`UserId`) REFERENCES Users(`Id`));")
                # Itinerary table
                cursor.execute("CREATE TABLE IF NOT EXISTS `Itineraries` ("
                                "`UserId` INT NOT NULL,"
                                "`Date` DATE NULL,"
                                "`Address` VARCHAR(150) NOT NULL,"
                                "`Order` INT NOT NULL,"
                                "`Status` VARCHAR(15) NOT NULL,"
                                "CHECK (`Status` in ('Ongoing', 'Reached', 'Unreached')),"
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
                                "CHECK (`StoreMean` in ('Search', 'Visited', 'Planned')),"
                                "PRIMARY KEY (`RowId`),"
                                "FOREIGN KEY (`UserId`) REFERENCES Users(`Id`));")

                return db

    except Exception as e:
        msg = e

    @staticmethod
    def Close(self, con):
        con.Close()

    
    try:
        @staticmethod
        def SetRoot():
            try:
                db = mySqlDB.connect(
                    host="localhost",
                    user="root",
                    password="password",
                    database="redpinsdb"
                )

                passwordSalt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                passwordHash = hashlib.sha512(("P@ssw0rd" + passwordSalt).encode("utf-8")).hexdigest()

                cursor = db.cursor()
                cursor.execute('INSERT INTO `Users` VALUES(NULL, "Root", "redpinsbuffer@gmail.com", "Admin", "2001-01-01", "00000000", "{}", "{}");'
                                .format(passwordHash, passwordSalt))
                db.commit()
                cursor.close()
                print("Root account has been created")
            except mySqlDB.IntegrityError:
                print("Root account in database")
            except Exception as e:
                print(e)

    except Exception as e:
        msg = e


MySql.Connect()
MySql.SetRoot()
print(MySql.msg)
