import ast
import os
import json
import os.path
from helpers.Config import Config
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
import time
from gi.repository import GObject, Gtk, GdkPixbuf
from helpers.StationRequester import StationRequester
from helpers.StationThumbnailDownloader import StationThumbnailDownloader
from helpers.MusicPlayer import MusicPlayer
from helpers.WidgetInit import WidgetInit


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        self.Application = application

        try:
            builder = Gtk.Builder.new_from_file("../ui/test2.glade")
            #self.Application.set_app_menu(GtkBuilder.get_object("app-menu"))
            builder.connect_signals(self)
            self.musicPlayer = MusicPlayer(self)
        except GObject.GError:
            print("Error reading GUI file")
            raise

        # Fire up the main window
        self.MainWindow = builder.get_object("mainWindow")
        self.MainWindow.set_application(application)
        self.Application.set_title = "8 Beat Radio"

        WidgetInit().init(builder, self)

        self.activeStationPlayBarThumbnail.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/icon_512_2.png', 64, 64))
        self.imgStationDetailsImage.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/icon_512_2.png', 128, 128))

        self.MainWindow.show()
        self.volume_change(None, None, 33)
        self.volumeScaler.set_fill_level(33)
        self.fill_saved_station_list(None)
        StationRequester(self).request_recently_clicked(20)

    def close(self, *args):
        self.MainWindow.destroy()

    def show_station_details(self, arg1):
        reveal = self.revealer.get_reveal_child()
        self.revealer.set_reveal_child(not reveal)

    def onStationSearch(self, widget):
        self.iconViewSpinner.start()
        StationRequester(self).request_by_name(widget.get_text(), 100)
        self.viewStack.set_visible_child(self.stackFirstPage)

    def hideNotificationBar(self, widget):
        self.notificationRevealer.set_reveal_child(False)

    def showNotification(self, message):
        self.lblNotificationMessage.set_label(message + " " + str(time.time()))
        self.notificationRevealer.set_reveal_child(True)

    def fill_search_results(self, data):
        self.newSearchStationsListStore.clear()

        for station in data:
            name = station['name']
            url = station['url']
            favicon = station['favicon']
            id = station['id']
            web = station['homepage']
            country = station['country']
            tags = station['tags']
            votes = station['votes']
            codec = station['codec']
            width = 92  #should be set in settings
            height = 92 #should be set in settings
            if ".pls" not in url and station['lastcheckok'] != "0":  #exclude .pls and broken stations
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(Config().get_cache_folder(), id),
                                                                    width, height)
                except:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/icon_512_2.png', width, height)
                    StationThumbnailDownloader(self, id, True).go(favicon)
                try:
                    self.newSearchStationsListStore.append([pixbuf, name, id, url, web, favicon, country, tags, votes, codec])
                except:
                    print("den virkede ikke")
        self.iconViewSpinner.stop()

    def changeThumbnail(self, stationId, newSearch):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(Config().get_cache_folder(), stationId), 92, 92)

            if newSearch:
                listStore = self.newSearchStationsListStore
            else:
                listStore = self.savedStationsListStore

            for station in listStore:
                if station[2] == stationId:
                    station[0] = pixbuf
        except:
            pass
            #self.showNotification("Error loading real image!")

    def selectStation(self, liststore, index):
        pixbuf = None
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(Config().get_cache_folder(),  liststore[index][2]), 64, 64)
            self.imgStationDetailsImage.set_from_pixbuf(pixbuf)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/icon_512_2.png', 64, 64)

        self.activeStationPlayBarThumbnail.set_from_pixbuf(pixbuf)
        self.lblSongName.set_label("")
        self.songNameLoadingSpinner.start()

        self.fill_detailswindow(liststore[index])
        self.musicPlayer.play(liststore[index][3], liststore[index][2])
        self.set_current_station_name(liststore[index][1])
        self.check_if_saved(None)

    def set_current_station_name(self, name):
        self.lblStationName.set_label(name)

    def set_current_station_song(self, songName, longName):
        self.songNameLoadingSpinner.stop()
        self.lblSongName.set_label(songName)
        self.lblSongName.set_tooltip_text(longName)

    def save_new_station(self, data):
        if len(data) > 0:
            station = data[0]
            name = station['name']
            url = station['url']
            favicon = station['favicon']
            sid = station['id']
            web = station['homepage']
            country = station['country']
            tags = station['tags']
            votes = station['votes']
            codec = station['codec']
            Config().add_saved_station(sid, name, url, web, country, favicon, tags, votes, codec)
            self.check_if_saved(None)
            self.fill_saved_station_list(None)


    def add_saved_station(self, widget):
        id = self.musicPlayer.get_playing_station_id()
        if id != 0:
            if Config().is_station_saved(id):
                Config().remove_station(id)
            else:
                StationRequester(self).request_by_id(id)


    def fill_detailswindow(self, station):
        #pixbuf, name, id, url, web, favicon, country, tags, votes, codec
        self.lblDetailsStationName.set_label(station[1])
        self.lblDetailsStationTags.set_label(station[7].replace(",", ", "))
        self.imgStationDetailsImage.set_from_pixbuf(self.get_local_thumbnail(station[2], 128, 128))
        self.lblDetailsStationVotes.set_label(station[8])
        self.lblDetailsStationCodec.set_label(station[9])
        self.lblDetailsStationLocation.set_label(station[6])

    def get_local_thumbnail(self, stationId, width, height):
        pixbuf = None
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(Config().get_cache_folder(),  stationId), width, height)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/icon_512_2.png', width, height)
        return pixbuf

    def volume_change(self, arg1, arg2, arg3):

        newVol = arg3/100
        if newVol > 1:
            newVol = 1
        if newVol < 0:
            newVol = 0
        self.musicPlayer.set_volume(newVol)

    def press_play_btn(self, widget):
        self.musicPlayer.pause()

    def set_play_btn_image(self, img):
        self.playBtnImage.set_from_icon_name(img, 1)

    def fill_saved_station_list(self, widget):
        #self.newSearchStationsListStore.clear()
        self.savedStationsListStore.clear()
        content = Config().get_saved_stations()

        for station in content:
            data = json.loads(str(station).replace("\'", "\"").replace("\\", "\\\\"))

            try:
                self.savedStationsListStore.append([self.get_thumbnail(data['id']),
                                                    data['name'].replace('\\xa0', ' '),
                                                    data['id'],
                                                    data['url'],
                                                    data['homepage'],
                                                    data['favicon'],
                                                    data['country'],
                                                    data['tags'],
                                                    data['votes'],
                                                    data['codec']])
            except:
                print("could not add station " + data['id'])

        for icon in self.savedStationsListStore:
            StationThumbnailDownloader(self, icon[2], False).go(icon[5])
        self.iconViewSpinner.stop()

    def check_if_saved(self, widget):
        stationId = self.musicPlayer.get_playing_station_id()
        if Config().is_station_saved(stationId):
            self.imgSavedStationIcon.set_from_icon_name("gtk-apply", 1)
        else:
            self.imgSavedStationIcon.set_from_icon_name("list-add", 1)

    def get_thumbnail(self, sid):

        width = 92  #should be set in settings
        height = 92 #should be set in settings

        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(Config().get_cache_folder(), sid),
                                                                width, height)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/icon_512_2.png', width, height)

        return pixbuf
