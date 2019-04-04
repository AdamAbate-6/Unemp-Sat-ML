import pyexcel as pe
import numpy as np
records = pe.get_records(file_name = "C:/Users/abate/OneDrive - William & Mary/Economics_Honors/Data/MSA_Unemp.xlsx")

quart_data = [["Year", "Quarter", "MSA", "Unemployment Rate"]]

#print(records)
quart_rates = []
for record in records:
    quart_rates.append(float(record["Unemployment Rate"]))

    if (int(record["Month"]) % 3 == 0):

        year = int(record["Year"])

        #Get quarter number
        quart = 0
        if (int(record["Month"]) == 3):
            quart = 1
        elif (int(record["Month"]) == 6):
            quart = 2
        elif (int(record["Month"]) == 9):
            quart = 3
        elif (int(record["Month"]) == 12):
            quart = 4

        msa = record["Area"]

        #Get quarterly average
        avg = np.average(quart_rates)

        quart_data.append([year, quart, msa, avg])

        quart_rates = []

quart_sheet = pe.Sheet(quart_data)

quart_sheet.save_as("quart_data.xlsx")
