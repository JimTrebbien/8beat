from tinydb import TinyDB, Query
import os
import os.path

class Config():

    def __init__(self):
        self.homeFolder = os.path.expanduser('~')
        self.settingsFolder = os.path.join(self.homeFolder, ".8beat-radio/")

    def startup(self):

        if not os.path.isdir(self.settingsFolder):
            self.first_run()
        else:
            self.database = TinyDB(os.path.join(self.settingsFolder, 'config.json'))

    def create_config(self):
        os.mknod(os.path.join(self.settingsFolder, "config.json"))
        self.database = TinyDB(os.path.join(self.settingsFolder, 'config.json'))
        self.database.insert({'cache_thumbmails': 'True',
                              'default_volume': 50})

    def first_run(self):
        print("first run")
        os.mkdir(self.settingsFolder)    #making the settingsfolder
        os.mkdir(os.path.join(self.settingsFolder, "cache"))    #making the folder for the cached thumbnails
        self.create_config()

    def get_cache_folder(self):
        return os.path.join(self.settingsFolder, "cache")


