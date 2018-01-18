import os
import json
import os.path
from helpers.Config import Config
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
import sched
import time
from gi.repository import GObject, Gtk, GdkPixbuf
from helpers.StationRequester import StationRequester
from helpers.StationThumbnailDownloader import StationThumbnailDownloader
from helpers.MusicPlayer import MusicPlayer


# This needs to go!
MENU_XML="""
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
      <attribute name="label" translatable="yes">Change label</attribute>
      <item>
        <attribute name="action">win.change_label</attribute>
        <attribute name="target">String 1</attribute>
        <attribute name="label" translatable="yes">String 1</attribute>
      </item>
      <item>
        <attribute name="action">win.change_label</attribute>
        <attribute name="target">String 2</attribute>
        <attribute name="label" translatable="yes">String 2</attribute>
      </item>
      <item>
        <attribute name="action">win.change_label</attribute>
        <attribute name="target">String 3</attribute>
        <attribute name="label" translatable="yes">String 3</attribute>
      </item>
    </section>
    <section>
      <item>
        <attribute name="action">win.maximize</attribute>
        <attribute name="label" translatable="yes">Maximize</attribute>
      </item>
    </section>
    <section>
      <item>
        <attribute name="action">app.about</attribute>
        <attribute name="label" translatable="yes">_About</attribute>
      </item>
      <item>
        <attribute name="action">app.quit</attribute>
        <attribute name="label" translatable="yes">_Quit</attribute>
        <attribute name="accel">&lt;Primary&gt;q</attribute>
    </item>
    </section>
  </menu>
</interface>
"""


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        self.Application = application

        # Read GUI from file and retrieve objects from Gtk.Builder
        try:
            builder = Gtk.Builder.new_from_file("../ui/test2.glade")
            #self.Application.set_app_menu(GtkBuilder.get_object("app-menu"))
            builder.connect_signals(self)
            self.musicPlayer = MusicPlayer(self)
        except GObject.GError:
            print("Error reading GUI file")
            raise

        #self.scheduler = sched.scheduler(time.time, time.sleep)

        # Fire up the main window
        self.MainWindow = builder.get_object("mainWindow")
        self.MainWindow.set_application(application)
        self.revealer = builder.get_object("stationDetailsRevealer")
        self.headerBar = builder.get_object("mainHeaderBar")
        self.headerBar.set_show_close_button(True)
        self.MainWindow.set_titlebar(self.headerBar)
        menubuilder = Gtk.Builder.new_from_string(MENU_XML, -1)
        self.Application.set_app_menu(menubuilder.get_object("app-menu"))

        self.lblNotificationMessage = builder.get_object("lblNotificationMessage")
        self.iconViewSpinner = builder.get_object("iconViewSpinner")
        self.notificationRevealer = builder.get_object("notificationRevealer")
        self.notificationBarFrame = builder.get_object("notificationBarFrame")

        self.newSearchStationsListStore = builder.get_object("newSearchStationsListStore")
        self.savedStationsListStore = builder.get_object("savedStationsListStore")
        self.activeStationPlayBarThumbnail = builder.get_object("activeStationPlayBarThumbnail")
        self.activeStationName = builder.get_object("activeStationPlayBarThumbnail")
        self.activeStationSong = builder.get_object("activeStationPlayBarThumbnail")
        self.lblDetailsStationName = builder.get_object("lblDetailsStationName")
        self.lblDetailsStationVotes = builder.get_object("lblDetailsStationVotes")
        self.lblDetailsStationLocation = builder.get_object("lblDetailsStationLocation")
        self.lblDetailsStationTags = builder.get_object("lblDetailsStationTags")
        self.lblDetailsStationCodec = builder.get_object("lblDetailsStationCodec")
        self.imgStationDetailsImage = builder.get_object("imgStationDetailsImage")
        self.lblSongName = builder.get_object("lblSongName")
        self.lblStationName = builder.get_object("lblStationName")
        self.volumeScaler = builder.get_object("volumeScaler")
        self.btnPlay = builder.get_object("btnPlay")
        self.playBtnImage = builder.get_object("playBtnImage")
        self.songNameLoadingSpinner = builder.get_object("songNameLoadingSpinner")
        self.imgSavedStationIcon = builder.get_object("imgSavedStationIcon")

        self.volumeScaler.set_value(50)
        self.volume_change(None, None, self.volumeScaler.get_value())


        self.newSearchIconView = builder.get_object("newSearchIconView")
        self.newSearchIconView.set_pixbuf_column(0)
        self.newSearchIconView.set_text_column(1)

        self.savedStationsIconView = builder.get_object("savedStationsIconView")
        self.savedStationsIconView.set_pixbuf_column(0)
        self.savedStationsIconView.set_text_column(1)

        self.activeStationPlayBarThumbnail.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/audio_wave.png', 64, 64))
        self.imgStationDetailsImage.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/audio_wave.png', 64, 64))

        self.MainWindow.show()

        self.test(None)

        #self.scheduler.run()


    def close(self, *args):
        self.MainWindow.destroy()

    def show_station_details(self, arg1):
        reveal = self.revealer.get_reveal_child()
        self.revealer.set_reveal_child(not reveal)

    def onStationSearch(self, widget):
        self.iconViewSpinner.start()
        StationRequester(self).request_by_name(widget.get_text())

        #self.showNotification("If we shouldn't eat at night, why is there a light in the fridge?")

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
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/audio_wave.png', width, height)
            except:
                self.showNotification("Error loading failsafe image!")

            try:
                self.newSearchStationsListStore.append([pixbuf, name, id, url, web, favicon, country, tags, votes, codec])
            except:
                print("den virkede ikke")

        print("der er " + str(len(self.newSearchStationsListStore)) + " stationer i liststore")
        for icon in self.newSearchStationsListStore:
            StationThumbnailDownloader(self, icon[2], True).go(icon[5])
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
            self.showNotification("Error loading real image!")


    def selectStation(self, liststore, index):
        pixbuf = None
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(Config().get_cache_folder(),  liststore[index][2]), 64, 64)
            self.imgStationDetailsImage.set_from_pixbuf(pixbuf)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/audio_wave.png', 64, 64)
            print("no image for station: " + liststore[index][2])

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

    #this needs to be rewritten
    #if a station in "saved" is unsaved and then saved, this looks for the station in the "all" liststore where it might not be
    def add_saved_station(self, widget):
        id = self.musicPlayer.get_playing_station_id()
        if Config().is_station_saved(id):
            Config().remove_station(id)
        else:
            for i in range(len(self.newSearchStationsListStore)):
                station = self.newSearchStationsListStore[i]
                if station[2] == str(id):
                    name = station[1]
                    sid = station[2]
                    web = station[4]
                    url = station[3]
                    country = station[6]
                    tags = station[7]
                    votes = station[8]
                    codec = station[9]
                    favicon = station[5]
                    Config().add_saved_station(sid, name, url, web, country, favicon, tags, votes, codec)
                    break


    def fill_detailswindow(self, station):
        #pixbuf, name, id, url, web, favicon, country, tags, votes, codec
        #self.imgStationDetailsImage.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(Config().get_cache_folder(),  station[2]), 64, 64))
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
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/audio_wave.png', width, height)
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



    #this should not be called test...
    def test(self, widget):
        self.savedStationsListStore.clear()
        content = Config().get_saved_stations()
        #js = content[0].decode("utf-8")
        #data = json.loads(js)
        for station in content:
            data = json.loads(str(station).replace("\'", "\""))
            id = data['id']
            name = data['name']
            url = data['url']
            favicon = data['favicon']
            web = data['homepage']
            country = data['country']
            tags = data['tags']
            votes = data['votes']
            codec = data['codec']
            width = 92  #should be set in settings
            height = 92 #should be set in settings

            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/audio_wave.png', width, height)
            except:
                self.showNotification("Error loading failsafe image!")

            try:
                self.savedStationsListStore.append([pixbuf, name, id, url, web, favicon, country, tags, votes, codec])
                print("added: " + name)
            except:
                print("den virkede ikke")

        print("der er " + str(len(self.savedStationsListStore)) + " stationer i liststore")
        for icon in self.savedStationsListStore:
            StationThumbnailDownloader(self, icon[2], False).go(icon[5])
            #self.changeThumbnail(id, False)
        self.iconViewSpinner.stop()


    def check_if_saved(self, widget):
        stationId = self.musicPlayer.get_playing_station_id()
        if Config().is_station_saved(stationId):
            self.imgSavedStationIcon.set_from_icon_name("gtk-apply", 1)
        else:
            self.imgSavedStationIcon.set_from_icon_name("list-add", 1)