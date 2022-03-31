from datetime import datetime
from DbContext import MySql
from DbContext import MongoDBContext


class TrackedPlacesCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["TrackedInformation"]
    
    def SetInfo(self, trackedPlace):
        # cursor = self.__connection.cursor()
        # # Check if today with the store mean has already been registered
        # cursor.execute('SELECT LastRegistered FROM TrackedPlaces '
        #                 'WHERE UserId = "{}" AND StoreMean = "{}";'
        #                 .format(trackedPlace.getUserId(), trackedPlace.getStoreMean() ))
        # currentTime = datetime.now()
        # lastRegisteredDate = cursor.fetchone()[0]

        # # If the user last updated date is not same as today then register to db
        # if lastRegisteredDate:
        #     if lastRegisteredDate.strftime("%Y-%m-%d") != currentTime.strftime("%Y-%m-%d"):
        #         try:
        #             cursor.execute('UPDATE TrackedPlaces SET'
        #                             'Frequency = Frequency + 1, LastRegistered = "{}" '
        #                             'WHERE UserId = {} AND StoreMean = "{}";'
        #                             .format(currentTime, trackedPlace.getUserId()))     
        #         except Exception as e:
        #             print(e)
        #             try:
        #                 cursor.execute('INSERT INTO TrackedPlaces VALUES(NULL, "{}", "{}", "{}", "{}", "{}");'
        #                                 .format(trackedPlace.getUserId(), trackedPlace.getAddress(), trackedPlace.getStoreMean(), 
        #                                 trackedPlace.getFrequency(), currentTime))
        #             except Exception as e:
        #                 print(e)
        #                 return {"success": False}
            

        # self.__connection.commit()
        # cursor.close()

        # return {"success": True}

        # Check if today with the store mean has already been registered
        trackedInfo = self.__connection.find_one({"_id": trackedPlace.getUserId(), "Action": trackedPlace.getStoreMean(), 
                                                    "Address": trackedPlace.getAddress()})
        currentTime = datetime.now()
        timestamps = []

        if trackedInfo is not None:
            try:
                timestamps = trackedInfo["timestamps"]
                lastRegisteredDate = timestamps[-1]

                if lastRegisteredDate.strftime("%Y-%m-%d") != currentTime.strftime("%Y-%m-%d"):
                    timestamps.append(currentTime)
                
                    try:  
                        self.__connection.update_one({"_id": trackedPlace.getUserId(), "action": trackedPlace.action()},
                                                        {"$set": {"timestamps": timestamps},
                                                        "$inc": {"frequency": 1}
                                                    }) 
                    except Exception as e:
                        print(e)
                        return {"success": False, "error": "An error occurred"}
                else:
                    return {"success": False, "error": "User already arrived"}

            except KeyError and IndexError:
                print("Timestamps and track record registered")
                self.__connection.insert_one({"Address": trackedPlace.getAddress(), "Action": trackedPlace.getStoreMean(), 
                                                "Frequency": 1, "Timestamps": [currentTime]}) 
        else:
            self.__connection.insert_one({"Address": trackedPlace.getAddress(), "Action": trackedPlace.getStoreMean(), 
                                                "Frequency": 1, "Timestamps": [currentTime]}) 
                

        return {"success": True}
