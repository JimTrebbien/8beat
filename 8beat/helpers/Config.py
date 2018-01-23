from tinydb import TinyDB, Query
import os
import os.path


class Config:

    def __init__(self):
        self.homeFolder = os.path.expanduser('~')
        self.settingsFolder = os.path.join(self.homeFolder, ".8beat-radio/")
        if not os.path.isdir(self.settingsFolder):
            self.first_run()
        else:
            self.configDatabase = TinyDB(os.path.join(self.settingsFolder, 'config.json'))
            self.stationsDatabase = TinyDB(os.path.join(self.settingsFolder, 'stations.json'))

    def startup(self):
        pass

    def create_config(self):
        os.mknod(os.path.join(self.settingsFolder, "config.json"))
        self.configDatabase = TinyDB(os.path.join(self.settingsFolder, 'config.json'))

        self.configDatabase.insert({'name': 'cache_thumbmails',
                              'value': True})

        self.configDatabase.insert({'name': 'default_volume',
                              'value': 50})

    def create_staionsdb(self):
        os.mknod(os.path.join(self.settingsFolder, "stations.json"))
        self.stationsDatabase = TinyDB(os.path.join(self.settingsFolder, 'stations.json'))

    def first_run(self):
        os.mkdir(self.settingsFolder)    #making the settingsfolder
        os.mkdir(os.path.join(self.settingsFolder, "cache"))    #making the folder for the cached thumbnails
        self.create_config()
        self.create_staionsdb()
        #self.test()

    def get_cache_folder(self):
        return os.path.join(self.settingsFolder, "cache")

    def add_saved_station(self, sid, name, url, web, country, favicon,  tags, votes, codec ):

        ft = Query()
        if not self.stationsDatabase.contains(ft.id == sid):
            self.stationsDatabase.insert({'id': sid,
                                            'name': name,
                                            'url': url,
                                            'homepage': web,
                                            'country': country,
                                            'favicon': favicon,
                                            'tags': tags,
                                            'votes': votes,
                                            'codec': codec})

    def get_saved_stations(self):
        return self.stationsDatabase.all()

    def is_station_saved(self, stationId):
        ft = Query()
        return self.stationsDatabase.contains(ft.id == stationId)

    def remove_station(self, stationId):
        ft = Query()
        return self.stationsDatabase.remove(ft.id == stationId)
