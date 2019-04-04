import os, sys
import Unzipper as u
import BandAvgExporter as bae
import TimeAveragerNew as ta
import Cleaner as cl

import getopt
import sys

if __name__ == '__main__':
    #sys.settrace

    #Get user input
    #MSAName = "New York-Newark-Jersey City, NY-NJ-PA MSA"
    #MSAName = "Baltimore-Columbia-Towson, MD MSA"
    # For now, average on a quarterly basis
    period = 3
    #bulkOrderNum = "977289"
    #bulkOrderNum = "976698"

    options, remainder = getopt.getopt(sys.argv[1:], 'm:b:', ['MSA=', 'BulkOrder='])

    for opt, arg in options:
        if opt in ('-m', '--MSA'):
            MSAName = arg
        elif opt in ('-b', '--BulkOrder'):
            bulkOrderNum = arg


    #Specific to W&M HPC
    rootDir = "/sciclone/scr10/acabate"

    #Specific to USGS BDA download package structure
    picsDir = rootDir + "/" + MSAName + "/Bulk Order " + bulkOrderNum + "/U.S. Landsat 4-8 ARD"

    # ---BEGIN PREPROCESSING---

    # Unzip tars holding GeoTIFFs
    print("Unzipping files")
    #unzipper = u.Unzipper(picsDir)
    #unzipper.unzipFiles()
    print("Unzipping finished")
    print("------------------")
    
    #Average GeoTIFF bands and export to JPG
    print("Averaging spectral bands and exporting to JPG")
    #processor = bae.BandAvgExporter(picsDir)
    #processor.executeCalculations()
    #processor.qgs.exitQgis()
    print("Spectral average and export finished")
    print("------------------")

    #Average JPGs over multiple designated time period
    print("Averaging images over designated time period")
    avgr = ta.TimeAverager(picsDir, period)
    avgr.average()
    print("Period averaging finished")
    print("------------------")

    #Match JPGs with unemployment values
    print("Matching images with unemployment values")
    import PicAndUnempMatcher as pum
    unempData = rootDir + "/quart_data.xlsx"
    #Match quarterly
    matcher = pum.PicAndUnempMatcher(rootDir, picsDir, unempData, MSAName, period)
    matcher.match()
    print("Image/unemployment matching finished")
    print("------------------")

    #Delete everything but final directory
    print("Deleting all MSA imagery except final directory")
    #cleaner = cl.Cleaner(picsDir)
    #cleaner.clean()
    print("Extraneous data deleted")
    print("------------------")
