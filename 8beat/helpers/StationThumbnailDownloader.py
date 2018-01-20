import os
import os.path
from gi.repository import Gio, GLib
from helpers.Config import Config

class StationThumbnailDownloader:

    def __init__(self, view, stationId, newSearch):
        self.cancellable = Gio.Cancellable()
        self.stationId = stationId
        self.view = view
        self.newSearch = newSearch

    def on_ready_callback(self, source_object, result, user_data):
        try:
            success, content, etag = source_object.load_contents_finish(result)
            outputfile = open(os.path.join(Config().get_cache_folder(), self.stationId), "wb")
            outputfile.write(content)
            self.view.changeThumbnail(self.stationId, self.newSearch)
        except GLib.GError as e:
            pass
            #print("Error: " + self.stationId + " " + e.message)
        #else:
            #content_text = content[:100].decode("utf-8")
            #self.append_text("Got content: " + content_text + "...")
        finally:
            self.cancellable.reset()

    def go(self, url):
        file_ = Gio.File.new_for_uri(url)
        file_.load_contents_async(self.cancellable, self.on_ready_callback, Config().get_cache_folder())
