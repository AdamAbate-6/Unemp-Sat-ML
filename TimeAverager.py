from PIL import Image
import numpy as np
import os

class TimeAverager:

    def __init__(self, direc, timePeriod):
        self.direc = direc
        self.timePeriod = timePeriod    #Number of months over which to average
    
    def average(self):
        #The month marking the end of the period of interest
        endOfPeriod = self.timePeriod
        periodNum = 1
        numPicsInPeriod = 0
        prevYear = 999999
        for root, dirs, files in os.walk(self.direc):
            pixelTotalArr = []
            #Make file names consist of numeric dates, and sort them in ascending order.
            dateFiles = sorted([int(f[15:23]) for f in files if f.endswith(".jpg")])
            #Loop through files in specified directory
            for i in range(len(dateFiles)):

                #i=0 corresponds to earliest date
                dateFileName = str(dateFiles[i])
                #print(dateFileName)
                #Find actual fileName that corresponds to this date
                fileName = ''
                for i in range(len(files)):
                    if (dateFileName == files[i][15:23] and files[i].endswith(".jpg")):
                        fileName = files[i]
                #print(fileName)
                
                #Ensure that we are averaging JPGs
                if (fileName.endswith(".jpg")):

                    #Make sure that image is in direc and not in a subdirectory
                    #because the subdirectory could well be periodAvgs
                    if (fileName not in os.listdir(self.direc)):
                        print(fileName + " not in " + self.direc)
                        continue

                    #The 19th and 20th (base 0) fileName characters indicate the month
                    month = int(fileName[19] + fileName[20])
                    year = int(fileName[15] + fileName[16] + fileName[17] + fileName[18])
                    
                    #Increase picture count for this period
                    if (month <= endOfPeriod and year <= prevYear):
                        numPicsInPeriod += 1

                    #If this photo is past current period of interest
                    elif (month > endOfPeriod or year > prevYear):
                        #Only output an average image if we have passed the previous period and the previous period had some images in it.
                        if (numPicsInPeriod > 0):
                            print("Period " + str(periodNum) +" has " + str(numPicsInPeriod) + " picture(s)")
                            #Average current pixelTotalArr
                            for i in range(len(pixelTotalArr)):
                                for j in range(len(pixelTotalArr[i])):
                                    #Assume grayscale -- only two dimensions
                                    pixelTotalArr[i][j] = pixelTotalArr[i][j]/float(numPicsInPeriod)
                            #And export averaged array to a JPG
                            a = np.asarray(pixelTotalArr)
                            avgIm = Image.fromarray(a)
                            if (avgIm.mode != 'RGB'):
                                avgIm = avgIm.convert('RGB')
                            #Weird filename indexing keeps location and date-retrieved info, but gets rid of date-taken info because this is an average
                            avgName = fileName[0:15] + fileName[24:len(fileName)-4] + "_PER" + str(periodNum) + "_" + str(year) + "_AVG.jpg"
                            if ("periodAvgs" not in os.listdir(self.direc)):
                                os.mkdir(self.direc + "/periodAvgs/")
                            avgIm.save(self.direc + "/periodAvgs/" + avgName)
                            print("Average image " + avgName + " successfully produced for period " + str(periodNum))

                        #set new end of period of interest
                        endOfPeriod += self.timePeriod
                        periodNum += 1
                        #Adjust endOfPeriod and periodNum to reflect date of new picture
                        #E.g. if there were pictures in quarter 1, but none in 2, and some in 3, make endOfPeriod 9 and periodNum 3.
                        while (month > endOfPeriod):
                            print("No pictures in", str(periodNum))
                            endOfPeriod += self.timePeriod
                            periodNum += 1
                        numPicsInPeriod = 1
                        pixelTotalArr = []
                        
                        #And if this new end is outside of the year...
                        if (endOfPeriod > 12):
                            #Reset it to start a new year
                            endOfPeriod = self.timePeriod
                            periodNum = 1

                    print(fileName)
                    im = Image.open(self.direc + "/" + fileName).convert("L")
                    width, height = im.size

                    #Initialize pixelTotalArr if not already done for this period
                    if(len(pixelTotalArr) == 0):
                        #COULD BE REVERSING WIDTH AND HEIGHT IN ARRAY
                        for i in range(0, height):
                            pixelTotalArr.append([])
                            for j in range(0, width):
                                #SIMPLIFYING BY ENFORCING GRAYSCALE
                                #pixelTotalArr[i].append([])
                                #for k in range(0, k_len):
                                #    pixelTotalArr[i][j].append(0)
                                pixelTotalArr[i].append(0)

                    #Update current period's pixelTotalArr with this jpg's values
                    for i in range(0, height):
                        for j in range(0, width):
                            #Assume grayscale -- only two dimensions
                            pixelTotalArr[i][j] += im.getpixel((j,i))
                    
                    prevYear = year