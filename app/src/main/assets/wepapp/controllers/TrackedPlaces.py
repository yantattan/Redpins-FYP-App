import csv, pandas
from datetime import datetime
from DbContext import MySql
from DbContext import MongoDBContext
from bson.objectid import ObjectId

from Model import TrackedPlace


class TrackedPlacesCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["TrackedInfo"]
    
    def SetInfo(self, trackedPlace):
        '''cursor = self.__connection.cursor()
        # Check if today with the store mean has already been registered
        cursor.execute('SELECT LastRegistered FROM TrackedPlaces '
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
                        return {"success": False}
            

        self.__connection.commit()
        cursor.close()

        return {"success": True}'''

        # Check if today with the store mean has already been registered
        trackedInfo = self.__connection.find_one({"UserId": trackedPlace.getUserId(), 
                                                    "Address": trackedPlace.getAddress()})
        currentTime = datetime.now()
        timestamps = []

        if trackedInfo is not None:
            try:
                timestamps = trackedInfo["Actions"][trackedPlace.getAction()]["Timestamps"]
                lastRegisteredDate = timestamps[-1]

                if lastRegisteredDate.strftime("%Y-%m-%d") != currentTime.strftime("%Y-%m-%d"):
                    timestamps.append(currentTime)
                    trackedInfo["Actions"][trackedPlace.getAction()]["Frequency"] += 1
                
                    try:  
                        self.__connection.update_one({"UserId": trackedPlace.getUserId(), 
                                                        "Address": trackedPlace.getAddress()},
                                                        {"$set": {"Actions": trackedInfo}
                                                    }) 
                        print("I reached here")
                    except Exception as e:
                        print(e)
                        try:
                            self.__connection.insert_one({"UserId": trackedPlace.getUserId(), "Address": trackedPlace.getAddress(), 
                                                "Actions": {
                                                    trackedPlace.getAction() : {"Frequency": 1, "Timestamps": [currentTime]}
                                                }
                                            })
                        except Exception as e:
                            print(e)
                            return {"success": False, "error": "An error occurred"}
                else:
                    return {"success": False, "error": "User already arrived"}

            except KeyError or IndexError as e:
                print(e)
                trackedInfo["Actions"][trackedPlace.getAction()] = {"Frequency": 1, "Timestamps": [currentTime]}
                try:
                    self.__connection.update_one({"UserId": trackedPlace.getUserId(), "Address": trackedPlace.getAddress()}, 
                                                    {"$set": {"Actions": trackedInfo["Actions"]}
                                                }) 
                except Exception as e:
                    print(e)
                    return {"success": False, "error": "An error occurred"}                    
        else:
            self.__connection.insert_one({"UserId": trackedPlace.getUserId(), "Address": trackedPlace.getAddress(), 
                                            "Actions": {
                                                trackedPlace.getAction() : {"Frequency": 1, "Timestamps": [currentTime]}
                                            }
                                        }) 

        return {"success": True}

    def GetTopAccessedInfo(self, userId):
        # Return top 5 most frequently accessed places
        allActions = ["Searched", "Planned", "Visited"]
        resultsDict = {}
        try:
            for act in allActions:
                results = self.__connection.aggregate([
                    {"$match": {"UserId": userId}},
                    {"$sort": {f"Actions.{act}": -1}},
                    {"$limit": 5}
                ])

                resultsList = []
                for row in results:
                    action = row["Actions"][act]
                    trackedPlace = TrackedPlace(row["UserId"], row["Address"], row["PlaceName"], act)
                    trackedPlace.setFrequency(action["Frequency"])
                    trackedPlace.setTimestamps(action["Timestamps"])
                    resultsList.append(trackedPlace)

                resultsDict[act] = resultsList

            return resultsDict

        except Exception as e:
            print(e)
            return 

    def GetDetailedTopAccessedInfo(self, userId, action):
        try:
            results = self.__connection.aggregate([
                    {"$match": {"UserId": userId}},
                    {"$sort": {f"Actions.{action}": -1}},
                    {"$limit": 5}
            ])

            return results
        except Exception as e:
            print(e)
            return 

    '''def GetRecentlyAccessedInfo(self, userId):
        try:
            results = self.__connection.aggregate([{
                "$addFields": {
                    "$recentDate": { "$let": { "vars": {
                        "last": {
                            "$arrayElemAt": ["Timestamps", -1]
                        }
                    }}}
                }
            }, 
            {"$sort": {"recentDate": 1}},
            {"$project": {"recentDate": 0}},
            {"$limit": 5}])

            resultsList = []

            for row in results:
                actionsList = []
                for action in row["Actions"]:
                    trackedPlace = TrackedPlace(row["UserId"], row["Address"], row["PlaceName"], action["Action"])
                    trackedPlace.setFrequency(action["Frequency"])
                    trackedPlace.setTimestamps(action["Timestamps"])
                    actionsList.append(trackedPlace)

                resultsList.append({"PlaceName": row["PlaceName"], "Address": row["Address"], "Actions": actionsList})

            return resultsList

        except Exception as e:
            print(e)
            return '''

    # Data export csv functions
    def ExportYourTrackedInfoCSV(self):
        # path = "csv/dbcsv/your-tracked-info.csv"
        # csvFile = open(path, "w", newline="")
        # csvWriter = csv.writer(csvFile)
        # # Header
        # csvWriter.writerow(["UserId", "Address", "Action", "Frequency"])
        path = "csv/dbcsv/future-tracked-info-preferences.csv"
        allInfo = self.__connection.find()
        csvReader = pandas.read_csv("csv/webcsv/restaurants_info.csv", encoding = "ISO-8859-1")
        csvWriter = csv.writer(open(path, "w", newline=""))
        # Header
        csvWriter.writerow(["UserId", "Category", "Action", "Timestamp", "Preference"])

        for row in allInfo:
            prefs = csvReader.loc[csvReader["Address"] == row["Address"].replace(", ", "|")]["Cuisines"].values[0].split("|")
            for pref in prefs:
                for action in row["Actions"]:
                    for t in row["Actions"][action]["Timestamps"]:
                        csvWriter.writerow([row["UserId"], "Eateries", action, t, pref])
        
        return path