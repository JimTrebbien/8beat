import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


class MusicPlayer:

    def __init__(self, view):
        self.view = view
        Gst.init(None)
        self.player = Gst.ElementFactory.make("playbin", "player")
        self.player.connect("audio-tags-changed", self.on_tags_changed)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message::application", self.on_application_message)
        bus.connect("message::state-changed", self.on_state_changed)
        self.playingStationId = 0

    def on_state_changed(self, bus, msg):
        old, new, pending = msg.parse_state_changed()
        print("1: " + str(old))
        print("2: " + str(new))
        print("3: " + str(pending))
        if new == Gst.State.PLAYING:
            self.view.set_play_btn_image("media-playback-pause")
        elif new == Gst.State.PAUSED:
            self.view.set_play_btn_image("media-playback-start")


    def on_tags_changed(self, playbin, stream):
        self.player.post_message(
            Gst.Message.new_application(
                self.player,
                Gst.Structure.new_empty("tags-changed")))

    def on_application_message(self, bus, msg):
        if msg.get_structure().get_name() == "tags-changed":
            self.analyze_streams()



    def analyze_streams(self):
        nr_audio = self.player.get_property("n-audio")
        for i in range(nr_audio):
            tags = None
            # retrieve the stream's audio tags
            tags = self.player.emit("get-audio-tags", i)
            if tags:
                title = tags.get_string(Gst.TAG_TITLE)[1]
                stationLongName = tags.get_string(Gst.TAG_ORGANIZATION)[1]
                if title:
                    # station = (station[:42] + '..') if len(station) > 42 else station


                    # self.mainWin.lblStationName.set_label(station)
                    # self.mainWin.lblStationName.set_markup("<a href=\"http://www.gtk.org\" " "title=\"Our website\">"+station+"</a>")
                    self.view.lblSongName.set_tooltip_text(title)
                    shortTitle = (title[:32] + '..') if len(title) > 32 else title
                    self.view.lblSongName.set_label(shortTitle)

    def play(self, uri, stationId):
        self.player.set_state(Gst.State.NULL)
        self.player.set_property("uri", uri)
        self.player.set_state(Gst.State.PLAYING)
        self.playingStationId = stationId

    def stop(self):
        pass

    def set_volume(self, volume):
        self.player.set_property("volume", volume)

    def play_pressed(self, uri):
        (ret, state, pending) = self.player.get_state(1)
        if state == Gst.State.PLAYING:
            self.player.set_state(Gst.State.PAUSED)
        else:
            self.play(uri)

    def is_playing(self):
        (ret, state, pending) = self.player.get_state(1)
        if state == Gst.State.PLAYING:
            return True
        else:
            return False

    def is_paused(self):
        (ret, state, pending) = self.player.get_state(1)
        if state == Gst.State.PAUSED:
            return True
        else:
            return False

    def get_playing_station_id(self):
        return self.playingStationId

    def pause(self):
        (ret, state, pending) = self.player.get_state(1)
        if state == Gst.State.PLAYING:
            self.player.set_state(Gst.State.PAUSED)
        elif state == Gst.State.PAUSED:
            self.player.set_state(Gst.State.PLAYING)
