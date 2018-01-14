
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

        self.scheduler = sched.scheduler(time.time, time.sleep)

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

        self.volumeScaler.set_value(50)
        self.volume_change(None, None, self.volumeScaler.get_value())


        self.newSearchIconView = builder.get_object("newSearchIconView")
        self.newSearchIconView.set_pixbuf_column(0)
        self.newSearchIconView.set_text_column(1)

        self.MainWindow.show()

        self.scheduler.run()

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
            StationThumbnailDownloader(self, icon[2]).go(icon[5])
        self.iconViewSpinner.stop()

    def changeThumbnail(self, stationId):
        print("changing for: " + stationId)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("cache/"+stationId, 92, 92)
            for station in self.newSearchStationsListStore:
                if station[2] == stationId:
                    station[0] = pixbuf

        except:
            self.showNotification("Error loading real image!")

    def selectStation(self, widget, index):
        pixbuf = None
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("cache/" + self.newSearchStationsListStore[index][2], 64, 64)
        except:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('../ui/audio_wave.png', 64, 64)
            print("no image for station: " + self.newSearchStationsListStore[index][2])

        self.activeStationPlayBarThumbnail.set_from_pixbuf(pixbuf)
        self.fill_detailswindow(self.newSearchStationsListStore[index])
        self.musicPlayer.play(self.newSearchStationsListStore[index][3], self.newSearchStationsListStore[index][2])
        self.set_current_station_name(self.newSearchStationsListStore[index][1]);

    def set_current_station_name(self, name):
        self.lblStationName.set_label(name)

    def set_current_station_song(self, songName):
        self.lblStationSong.set_label(songName)

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
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("cache/" + stationId, width, height)
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
