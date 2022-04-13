import csv, json

import requests

path = "csv/webcsv/restaurants_info.csv"
csvReader = csv.reader(open(path), delimiter = ',')

csvFile = open("csv/webcsv/restaurants_info.csv", "w", newline="")
csvWriter = csv.writer(csvFile)
# Header
i = True
count = 1
for row in csvReader:
    if i:
        csvWriter.writerow(row + ["Latlng"])
        i = False
    else:
        newChar = row[0]
        for char in row[0]:
            if char.isdigit():
                newChar = newChar[1:]
            elif char == ".":
                newChar = newChar[2:]
                break
            else:
                break
        row[0] = newChar
        
        postalCode = row[2][-16:-10]
        link = "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y".format(postalCode)
        apiResult = requests.get(link).json()
        csvWriter.writerow(row + [apiResult["results"][0]["LATITUDE"] + "|" +apiResult["results"][0]["LONGITUDE"]])
        count += 1
