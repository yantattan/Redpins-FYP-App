from bs4 import BeautifulSoup
import csv, json

import requests

# Add more restaurants from different locations (RUN ONCE)
# Add in more info and clean data
# print("Start")
# hi = requests.get('https://www.tripadvisor.in/Hotels-g187147-Paris_Ile_de_France-Hotels.html')
# print(hi.status_code)
# print(hi)
# sectorsLeft = {}
# csvReaderRaw = csv.reader(open("csv/webcsv/restaurants_info_raw.csv"), delimiter = ',')
csvReader = csv.reader(open("csv/webcsv/restaurants_info_raw.csv"), delimiter = ',')

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
        # print(row[1])
        # html = requests.get(row[1], timeout=5)
        # print("req done")
        # soup = BeautifulSoup(html, 'lxml')
        # mapViewA = soup.findAll('a', class_="fhGHT", href=True)
        # for a in mapViewA:
        #     if a["href"] == "#MAPVIEW":
        #         address = a.text
        #         print(address)

        # Name
        # newChar = row[0]
        # for char in row[0]:
        #     if char.isdigit():
        #         newChar = newChar[1:]
        #     elif char == ".":
        #         newChar = newChar[2:]
        #         break
        #     else:
        #         break
        # row[0] = newChar

        if row[5][-9:].lower() == "singapore":
            row[5] = row[5][:-10]
        postalCode = row[5][-6:]
        json.loads(row[7])
        print(f"Row {count}")
        link = "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y".format(postalCode)
        apiResult = requests.get(link).json()
        print(postalCode)
        csvWriter.writerow(row + [apiResult["results"][0]["LATITUDE"] + "," +apiResult["results"][0]["LONGITUDE"]])
        count += 1
