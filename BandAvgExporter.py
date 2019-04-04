from qgis.core import *
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from osgeo import gdal
import os
gdal.UseExceptions()

class BandAvgExporter:

    def __init__(self, direc):
        # supply path to qgis install location
        #QgsApplication.setPrefixPath("privatemodules/qgis", True)
        QgsApplication.setPrefixPath("/sciclone/home20/acabate/.conda/envs/qgis/share/qgis/python/qgis", True)

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
                                continue
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