from DbContext import MongoDBContext
from Model import Itinerary
from bson.objectid import ObjectId


class ItinerariesCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["Itineraries"]

    def SetItinerary(self, itinerary: Itinerary):
        if itinerary.getId() is None:
            try:
                self.__connection.insert_one({"Name": itinerary.getName(), "PlannerId": itinerary.getPlannerId(), "UserId": itinerary.getUserId(), "Date": itinerary.getDate(), "StartTime": itinerary.getStartTime(), 
                                            "EndTime": itinerary.getEndTime(), "Type": itinerary.getType(), "TransportMode": itinerary.getTransportMode(), 
                                            "TimeAllowance": itinerary.getTimeAllowance(), "TimeLeft": itinerary.getTimeLeft(), "HasEnd": itinerary.getEnd(), 
                                            "Places": itinerary.getPlaces(), "Description": itinerary.getDescription(), "Confirmed": itinerary.getConfirmed(), "Status": itinerary.getStatus()})

                return {"success": True}
            except Exception as e:
                print(e)
                return {"success": False, "error": e}
        else:
            try:
                self.__connection.update_one({"_id": ObjectId(itinerary.getId())}, {"$set": {"Name": itinerary.getName(), "PlannerId": itinerary.getPlannerId(), "UserId":itinerary.getUserId(), "Date": itinerary.getDate(), "StartTime": itinerary.getStartTime(), 
                                            "EndTime": itinerary.getEndTime(), "Type": itinerary.getType(), "TransportMode": itinerary.getTransportMode(), 
                                            "TimeAllowance": itinerary.getTimeAllowance(), "TimeLeft": itinerary.getTimeLeft(), "HasEnd": itinerary.getEnd(), 
                                            "Places": itinerary.getPlaces(), "Description": itinerary.getDescription(), "Confirmed": itinerary.getConfirmed(), "Status": itinerary.getStatus()}})

                return {"success": True}
            except Exception as e:
                print(e)
                return {"success": False, "error": e}

    def GetItineraryById(self, id):
        try:
            itinerary = self.__connection.find_one({"_id": ObjectId(id)})
            if itinerary is not None:
                return Itinerary(itinerary["_id"], itinerary["UserId"], itinerary["Name"], itinerary["Date"], itinerary["StartTime"], itinerary["EndTime"], itinerary["Type"], 
                                itinerary["TransportMode"], itinerary["TimeAllowance"], itinerary["TimeLeft"], itinerary["Confirmed"], itinerary["Status"], itinerary["Places"], itinerary["Description"], itinerary["PlannerId"], itinerary["HasEnd"])
        except Exception as e:
            print(e)

    def GetOngoingItinerary(self, userId):
        try:
            itinerary = self.__connection.find_one({"UserId": userId, "Status": "Ongoing"})
            if itinerary is not None:
                return Itinerary(itinerary["_id"], itinerary["UserId"], itinerary["Name"], itinerary["Date"], itinerary["StartTime"], itinerary["EndTime"], itinerary["Type"], 
                                itinerary["TransportMode"], itinerary["TimeAllowance"], itinerary["TimeLeft"], itinerary["Confirmed"], itinerary["Status"], itinerary["Places"], itinerary["Description"], itinerary["PlannerId"], itinerary["HasEnd"])
        except Exception as e:
            print(e)

    def GetUnconfimredItinerary(self, userId, tripType):
        try:
            if tripType == "Explorer":
                itinerary = self.__connection.find_one({"UserId": userId, "Type": tripType, "Confirmed": False})
                if itinerary is not None:
                    return Itinerary(itinerary["_id"], itinerary["UserId"], itinerary["Name"], itinerary["Date"], itinerary["StartTime"], itinerary["EndTime"], itinerary["Type"], 
                                    itinerary["TransportMode"], itinerary["TimeAllowance"], itinerary["TimeLeft"], itinerary["Confirmed"], itinerary["Status"], itinerary["Places"], itinerary["Description"], itinerary["PlannerId"], itinerary["HasEnd"])
            else:
                itinerary = list(self.__connection.find({"UserId": userId, "Type": tripType, "Confirmed": False}))
                if len(itinerary) > 0:
                    return list(map(lambda x: Itinerary(x["_id"], x["UserId"], x["Name"], x["Date"], x["StartTime"], x["EndTime"], x["Type"], 
                                    x["TransportMode"], x["TimeAllowance"], x["TimeLeft"], x["Confirmed"], x["Status"], x["Places"], x["Description"], x["PlannerId"], x["HasEnd"]), itinerary))
            
        except Exception as e:
            print(e)

    def GetReviewingItinerary(self, userId, tripType):
        try:
            if tripType == "Explorer":
                itinerary = self.__connection.find_one({"UserId": userId, "Type":  tripType, "Confirmed": True, "Status": "Planning"})
                if itinerary is not None:
                    return Itinerary(itinerary["_id"], itinerary["UserId"], itinerary["Name"], itinerary["Date"], itinerary["StartTime"], itinerary["EndTime"], itinerary["Type"], 
                                    itinerary["TransportMode"], itinerary["TimeAllowance"], itinerary["TimeLeft"], itinerary["Confirmed"], itinerary["Status"], itinerary["Places"], itinerary["Description"], itinerary["PlannerId"], itinerary["HasEnd"])
            else:
                itinerary = list(self.__connection.find({"UserId": userId, "Type":  tripType, "Confirmed": True, "Status": "Planning"}))
                if len(itinerary) > 0:
                    return list(map(lambda x: Itinerary(x["_id"], x["UserId"], x["Name"], x["Date"], x["StartTime"], x["EndTime"], x["Type"], 
                                    x["TransportMode"], x["TimeAllowance"], x["TimeLeft"], x["Confirmed"], x["Status"], x["Places"], x["Description"], x["PlannerId"], x["HasEnd"]), itinerary))

        except Exception as e:
            print(e)  

    def GetPlannerItineraries(self, plannerId):
        try:
            itineraries = self.__connection.find({"PlannerId": plannerId})
            if len(list(itineraries)) > 0:
                return list(map(lambda x: Itinerary(x["_id"], x["UserId"], x["Name"], x["Date"], x["StartTime"], x["EndTime"], x["Type"], x["TransportMode"], x["TimeAllowance"], x["TimeLeft"], x["Confirmed"], x["Status"], x["Places"], x["Description"],x["PlannerId"], x["HasEnd"]), itineraries)) 
        except Exception as e:
            print(e)

    def GetAllPlannerItineraries(self, userId):
        try:
            itineraries = self.__connection.find({"UserId": userId, "Type": "Planner"})
            if len(list(itineraries)) > 0:
                return list(map(lambda x: Itinerary(x["_id"], x["UserId"], x["Name"], x["Date"], x["StartTime"], x["EndTime"], x["Type"], x["TransportMode"], x["TimeAllowance"], x["TimeLeft"], x["Confirmed"], x["Status"], x["Places"], x["Description"],  x["PlannerId"], x["HasEnd"]), itineraries)) 
        except Exception as e:
            print(e)

    def ClearPlanner(self, plannerId):
        try:
            self.__connection.delete_many({"PlannerId": plannerId})

            return {"success": True}
        except Exception as e:
            print(e)
            return {"success": False, "error": e}
