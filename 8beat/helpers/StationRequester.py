import urllib.request
import json
import urllib.parse
from gi.repository import Gio, GLib


class StationRequester:

    def __init__(self, view):
        self.view = view
        self.cancellable = Gio.Cancellable()

    def on_ready_callback(self, source_object, result, user_data):
        try:
            success, content, etag = source_object.load_contents_finish(result)
            js = content.decode("utf-8")
            data = json.loads(js)
            self.view.fill_search_results(data)
        except GLib.GError as e:
            print("Error: " + e.message)
        finally:
            self.cancellable.reset()

    def request_by_name(self, name):
        url = "http://www.radio-browser.info/webservice/json/stations/search?name={}".format(
            urllib.parse.quote_plus(name))
        file_ = Gio.File.new_for_uri(url)
        file_.load_contents_async(self.cancellable, self.on_ready_callback, None)
