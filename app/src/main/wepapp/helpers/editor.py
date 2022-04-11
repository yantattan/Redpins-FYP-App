import csv, json

import requests

path = "csv/webcsv/restaurants_info.csv"
csvReader = csv.reader(open(path), delimiter = ',')

csvFile = open("csv/webcsv/restaurants_info2.csv", "w", newline="")
csvWriter = csv.writer(csvFile)
# Header
i = True
count = 1
for row in csvReader:
    if i:
        csvWriter.writerow(row + ["Latlng"])
        i = False
    else:
        print(count)
        
        postalCode = row[2][-16:-10]
        print(postalCode)
        print()
        link = "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y".format(postalCode)
        apiResult = requests.get(link).json()
        csvWriter.writerow(row + [apiResult["results"][0]["LATITUDE"] + "|" +apiResult["results"][0]["LONGITUDE"]])
        count += 1
