from datetime import datetime
from DbContext import MySql


class TrackedPlacesCon:
    __connection = None

    def __init__(self):
        self.__connection = MySql.Connect()
    
    def SetInfo(self, trackedPlace):
        cursor = self.__connection.cursor()
        # Check if today with the store mean has already been registered
        cursor.execute('SELECT LastRegistered FROM TrackedPlaces'
                        'WHERE UserId = "{}" AND StoreMean = "{}";'
                        .format(trackedPlace.getUserId(), trackedPlace.getStoreMean() ))
        currentTime = datetime.now()
        lastRegisteredDate = cursor.fetchone()[0]

        # If the user last updated date is not same as today then register to db
        if lastRegisteredDate:
            if lastRegisteredDate.strftime("%Y-%m-%d") != currentTime.strftime("%Y-%m-%d"):
                try:
                    cursor.execute('UPDATE TrackedPlaces SET'
                                    'Frequency = Frequency + 1, LastRegistered = "{}" '
                                    'WHERE UserId = {} AND StoreMean = "{}";'
                                    .format(currentTime, trackedPlace.getUserId()))     
                except Exception as e:
                    print(e)
                    try:
                        cursor.execute('INSERT INTO TrackedPlaces VALUES(NULL, "{}", "{}", "{}", "{}", "{}");'
                                        .format(trackedPlace.getUserId(), trackedPlace.getAddress(), trackedPlace.getStoreMean(), 
                                        trackedPlace.getFrequency(), currentTime))
                    except Exception as e:
                        print(e)
                        return {"success": False, "error": e}
            

        self.__connection.commit()
        cursor.close()

        return {"success": True}
