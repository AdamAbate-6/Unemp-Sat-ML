import shutil

class Cleaner:

    def __init__(self, picsDir):
        self.picsDir = picsDir

    def clean(self):
        shutil.rmtree(self.picsDir, ignore_errors=True)