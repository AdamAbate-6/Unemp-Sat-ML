import tarfile
import os

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