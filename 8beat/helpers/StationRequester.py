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

    def request_by_name(self, name, limit):
        url = "http://www.radio-browser.info/webservice/json/stations/search?name={}".format(
            urllib.parse.quote_plus(name)+"&limit="+str(limit))

        file_ = Gio.File.new_for_uri(url)
        file_.load_contents_async(self.cancellable, self.on_ready_callback, None)


    def on_request_by_id_callback(self, source_object, result, user_data):
        try:
            success, content, etag = source_object.load_contents_finish(result)
            js = content.decode("utf-8")
            data = json.loads(js)
            self.view.save_new_station(data)
        except GLib.GError as e:
            print("Error: " + e.message)
        finally:
            self.cancellable.reset()


    def request_by_id(self, stationId):
        url = "http://www.radio-browser.info/webservice/json/stations/byid/"+stationId
        file_ = Gio.File.new_for_uri(url)
        file_.load_contents_async(self.cancellable, self.on_request_by_id_callback, None)


    def request_by_votes(self, limit):
        url = "http://www.radio-browser.info/webservice/json/stations/topvote/"+str(limit)
        file_ = Gio.File.new_for_uri(url)
        file_.load_contents_async(self.cancellable, self.on_ready_callback, None)

    def request_by_clicks(self, limit):
        url = "http://www.radio-browser.info/webservice/json/stations/topclick/"+str(limit)
        file_ = Gio.File.new_for_uri(url)
        file_.load_contents_async(self.cancellable, self.on_ready_callback, None)

    def request_recently_clicked(self, limit):
        url = "http://www.radio-browser.info/webservice/json/stations/lastclick/"+str(limit)
        file_ = Gio.File.new_for_uri(url)
        file_.load_contents_async(self.cancellable, self.on_ready_callback, None)
