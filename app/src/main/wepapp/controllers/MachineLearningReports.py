from sys import excepthook
from DbContext import MongoDBContext
from Model import MachineLearningReport


class MachineLearningReportCon:
    __connection = None

    def __init__(self):
        self.__connection = MongoDBContext.Connect()["MachineLearningReports"]

    def SetData(self, machineLearningReport):
        modelField = self.__connection.find_one({"Model": machineLearningReport.getModelName()})
        if modelField is not None:
            modelField["Data"][machineLearningReport.getAttribute()] = machineLearningReport.getData()
            try:
                self.__connection.update_one({"Model": machineLearningReport.getModelName()}, 
                                                {"$set": {"Model": modelField["Model"], "Data": modelField["Data"]}})
            except Exception as e:
                print("An error occurred updating new info to machine learning report")

        else:
            resultData = {"Model": machineLearningReport.getModelName(),
                            "Data": {
                                machineLearningReport.getAttribute(): machineLearningReport.getData()
                            }}
            try:
                self.__connection.insert_one(resultData)
            except Exception:
                print("An error occurred registering new model to machine learning report")

    def GetData(self, model):
        try:
            return self.__connection.find_one({"Model": model})
        except Exception as e:
            print(e)
