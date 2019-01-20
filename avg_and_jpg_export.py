from qgis.core import *
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
import os, sys
from osgeo import gdal
from PIL import Image
import numpy as np
import tarfile
#import Image, ImageDraw
gdal.UseExceptions()

class tifPreProcessor:

    def __init__(self, direc):
        # supply path to qgis install location
        QgsApplication.setPrefixPath("privatemodules/qgis", True)

        # create a reference to the QgsApplication, setting the
        # second argument to False disables the GUI
        self.qgs = QgsApplication([], False)

        # load providers
        self.qgs.initQgis()

        self.rootDir = direc

    def calculateAvgAndOutput(self, rlayers, entries, outputDir):	
        rlayer = rlayers[len(rlayers)-1]
        if (len(entries) == 7):
            calc = QgsRasterCalculator( '( lyr@1 + lyr@2 + lyr@3 + lyr@4 + lyr@5 + lyr@6 + lyr@7 ) / 7', outputDir, 'GTiff', rlayer.extent(), rlayer.width(), rlayer.height(), entries )
            print(calc.processCalculation())

        elif (len(entries) == 6):
            calc = QgsRasterCalculator( '(lyr@1 + lyr@2 + lyr@3 + lyr@4 + lyr@5 + lyr@6) / 6', outputDir, 'GTiff', rlayer.extent(), rlayer.width(), rlayer.height(), entries )
            print(calc.processCalculation())
        
        elif (len(entries) == 5):
            calc = QgsRasterCalculator( '(lyr@1 + lyr@2 + lyr@3 + lyr@4 + lyr@5) / 5', outputDir, 'GTiff', rlayer.extent(), rlayer.width(), rlayer.height(), entries )
            print(calc.processCalculation())

        elif (len(entries) == 4):
            calc = QgsRasterCalculator( '(lyr@1 + lyr@2 + lyr@3 + lyr@4) / 4', outputDir, 'GTiff', rlayer.extent(), rlayer.width(), rlayer.height(), entries )
            print(calc.processCalculation())

        elif (len(entries) == 3):
            calc = QgsRasterCalculator( '(lyr@1 + lyr@2 + lyr@3) / 3', outputDir, 'GTiff', rlayer.extent(), rlayer.width(), rlayer.height(), entries )
            print(calc.processCalculation())

        elif (len(entries) == 2):
            calc = QgsRasterCalculator( '(lyr@1 + lyr@2) / 2', outputDir, 'GTiff', rlayer.extent(), rlayer.width(), rlayer.height(), entries )
            print(calc.processCalculation())
        
        elif (len(entries) == 1):
            calc = QgsRasterCalculator( '(lyr@1)', outputDir, 'GTiff', rlayers[0].extent(), rlayers[0].width(), rlayers[0].height(), entries )
            print(calc.processCalculation())

        self.exportToJPG(outputDir)

    def obtainOutDir(self, dir):
        #Variables needed for finding directories -- MOVE THESE
        output_path = self.rootDir + "/" + dir + "_SRB_AVG.tif"
        return output_path
    
    def exportToJPG(self, outputDir):
        options_list = [
            '-ot Byte',
            '-of JPEG',
            '-b 1',
            '-scale'
        ]
        options_string = " ".join(options_list)

        #Give file the same name (outputDir), but make it a jpg (jpgDir)
        baseDir = outputDir[:-3]
        jpgSuf = "jpg"
        jpgDir = baseDir + jpgSuf

        gdal.Translate(jpgDir,
                       outputDir,
                       options=options_string)

    def executeCalculations(self):
        for root, dirs, files in os.walk(self.rootDir):
            for dir in dirs:
                newDir = self.rootDir + '/' + dir
                print("------------------------------")
                print("SCANNING DIRECTORY: " + newDir)
                #Variables needed for raster calculation
                rasIndex=1
                ras=[]
                entries=[]
                rlayers = []
                for subRoot, subDirs, subFiles in os.walk(newDir):
                    #print("Subfiles of directory: " + str(subFiles))
                    for fileName in subFiles:
                        if (fileName.endswith(".tif") and fileName[len(fileName)-5] != "A" and fileName[len(fileName)-7] != "B"):
                            print("Evaluating SRB TIF file of band " + fileName[len(fileName)-5] + ": " + fileName)

                            #Figure out properties of file
                            tifFile = newDir + '/' + fileName# + ".tif"
                            bandNumber = fileName[len(fileName)-5]
                    
                            #Create a raster layer
                            rlayer = QgsRasterLayer(tifFile, "Band" + bandNumber)
                            if not rlayer.isValid():
                                print("Layer failed to load!")
                            rlayers.append(rlayer)

                            #Create a raster calculator entry
                            ref = 'lyr@' + str(rasIndex)
                            ras = QgsRasterCalculatorEntry()
                            ras.ref = ref
                            ras.raster = rlayer
                            ras.bandNumber = 1
                            entries.append(ras)
                            rasIndex += 1	

                if (len(rlayers) > 0 and len(entries) > 0):
                    #Obtain desired output path
                    outDir = self.obtainOutDir(dir)

                    #Calculate average for this directory	
                    self.calculateAvgAndOutput(rlayers, entries, outDir)

class jpgTimeAverager:

    def __init__(self, direc, timePeriod):
        self.direc = direc
        self.timePeriod = timePeriod    #Number of months over which to average
    
    def average(self):
        #The month marking the end of the period of interest
        endOfPeriod = self.timePeriod
        periodNum = 1
        numPicsInPeriod = 0
        for root, dirs, files in os.walk(self.direc):
            pixelTotalArr = []
            #Loop through files in specified directory
            for fileName in files:
                #Ensure that we are averaging JPGs
                if (fileName.endswith(".jpg")):
                    #The 19th and 20th (base 0) fileName characters indicate the month
                    month = int(fileName[19] + fileName[20])
                    year = int(fileName[15] + fileName[16] + fileName[17] + fileName[18])
                    
                    if (month <= endOfPeriod):
                        numPicsInPeriod += 1
                    #If the month is past the period of interest...
                    elif (month > endOfPeriod):
                        #Only output an average image if we have passed the previous period and the previous period had some images in it.
                        if (numPicsInPeriod > 0):
                            print("Period",str(periodNum),"has",str(numPicsInPeriod),"pictures")
                            #Average current pixelTotalArr
                            for i in range(len(pixelTotalArr)):
                                for j in range(len(pixelTotalArr[i])):
                                    #SIMPLIFYING BY ENFORCING GRAYSCALE
                                    #for k in range(len(pixelTotalArr[i][j])):
                                    #    pixelTotalArr[i][j][k] = pixelTotalArr[i][j][k]/float(numPicsInPeriod)
                                    pixelTotalArr[i][j] = pixelTotalArr[i][j]/float(numPicsInPeriod)
                            #And export averaged array to a JPG
                            a = np.asarray(pixelTotalArr)
                            avgIm = Image.fromarray(a)
                            if (avgIm.mode != 'RGB'):
                                avgIm = avgIm.convert('RGB')
                            #Weird filename indexing keeps location and date-retrieved info, but gets rid of date-taken info because this is an average
                            avgName = fileName[0:15] + fileName[24:len(fileName)-4] + "_PER" + str(periodNum) + "_" + str(year) + "_AVG.jpg"
                            avgIm.save(self.direc + "/periodAvgs/" + avgName)
                            print("Average image", avgName, "successfully produced for period", periodNum)

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

                    #If image has many layers, its getpixel() will return a tuple
                    #Accounting for this is necessary in pixelTotalArr initialization
                    #pixIsTup = False
                    #if (type(im.getpixel((0,0))) == int):
                    #    k_len = 1
                    #else:
                    #    pixIsTup = True
                    #    k_len = len(im.getpixel((0,0)))
                    
                    if(len(pixelTotalArr) == 0):
                        #Initialize pixelTotalArr
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
                            #SIMPLIFYING BY ENFORCING GRAYSCALE
                            #for k in range(0, k_len):
                                #if (pixIsTup):
                                #    pixelTotalArr[i][j][k] += im.getpixel((i,j))[k]
                                #else:
                                #    pixelTotalArr[i][j][k] += im.getpixel((i,j))
                            pixelTotalArr[i][j] += im.getpixel((j,i))

class Unzipper:

    def __init__(self, direc):
        self.direc = direc
    
    def unzipFiles(self):
        for root, dirs, files in os.walk(self.direc):
            #Loop through files in specified directory
            for fileName in files:
                #Ensure that we are only unzipping tars
                if (fileName.endswith(".tar")):
                    print("Unzipping " + fileName)
                    try:
                        tarObj = tarfile.open(self.direc + "/" + fileName)
                        #Extract the contents of the tar into a directory of the same name
                        tarObj.extractall(self.direc + "/" + fileName[0:len(fileName)-4])
                        os.remove(self.direc + "/" + fileName)
                    #If tar file doesn't have contents, we don't need it anyway
                    except tarfile.ReadError:
                        os.remove(self.direc + "/" + fileName)

if __name__ == '__main__':
    direc = "scr10/Baltimore-Columbia-Towson, MD MSA/Bulk Order 976698/U.S. Landsat 4-8 ARD"
    unzipper = Unzipper(direc)
    unzipper.unzipFiles()
    print("Unzipping finished")
    
    #processor = tifPreProcessor(direc)
    #processor.executeCalculations()
    #processor.qgs.exitQgis()

    #Average quarterly (3 months)
    #avgr = jpgTimeAverager(direc, 3)
    #avgr.average()
