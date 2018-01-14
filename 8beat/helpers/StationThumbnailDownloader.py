from gi.repository import Gio, GLib

class StationThumbnailDownloader:

    def __init__(self, view, stationId):
        self.cancellable = Gio.Cancellable()
        self.stationId = stationId
        self.view = view

    def on_ready_callback(self, source_object, result, user_data):
        try:
            success, content, etag = source_object.load_contents_finish(result)
            outputfile = open("cache/"+self.stationId, "wb")
            outputfile.write(content)
            self.view.changeThumbnail(self.stationId)
        except GLib.GError as e:
            print("Error: " + self.stationId + " " + e.message)
        #else:
            #content_text = content[:100].decode("utf-8")
            #self.append_text("Got content: " + content_text + "...")
        finally:
            self.cancellable.reset()

    def go(self, url):
        file_ = Gio.File.new_for_uri(url)
        file_.load_contents_async(self.cancellable, self.on_ready_callback, "../cache/")
