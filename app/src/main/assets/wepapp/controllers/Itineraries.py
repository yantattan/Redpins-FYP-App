from DbContext import MongoDBContext
from Model import Itinerary
from bson.objectid import ObjectId


class ItinerariesCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["Itineraries"]

    def SetItinerary(self, itinerary: Itinerary):
        recordExists = self.__connection.find_one({"_id": ObjectId(itinerary.getId())})
        try:
            if recordExists is None:
                self.__connection.insert_one({"Name": itinerary.getName(), "Date": itinerary.getDate(), "Type": itinerary.getType(),
                                            "TransportMode": itinerary.getTransportMode(), "TimeAllowance": itinerary.getTimeAllowance(),
                                            "TimeLeft": itinerary.getTimeLeft(), "Places": itinerary.getPlaces()})

                return {"success": True}
            else:
                self.__connection.update_one({"_id": ObjectId(itinerary.getId())}, {"$set": {"Name": itinerary.getName(), "Date": itinerary.getDate(), "Type": itinerary.getType(),
                                            "TransportMode": itinerary.getTransportMode(), "TimeAllowance": itinerary.getTimeAllowance(),
                                            "TimeLeft": itinerary.getTimeLeft(), "Places": itinerary.getPlaces()}})

                return {"success": True}
        except Exception as e:
            print(e)
            return {"success": False, "error": e}
