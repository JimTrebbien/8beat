#!/usr/bin/python3
# coding=utf8
import gi
from helpers.Config import Config
from views.MainWindow import MainWindow
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GObject, Gio, Gdk, Gtk, GLib



class EightBeat(Gtk.Application):
    # Main initialization routine
    def __init__(self, application_id, flags):
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        Config().startup()
        self.connect("activate", self.new_window)



    def new_window(self, *args):
        MainWindow(self)


# Starter
def main():
    # Initialize GTK Application
    Application = EightBeat("com.motorlicker.eightbeat", Gio.ApplicationFlags.FLAGS_NONE)

    # Start GUI
    Application.run()

if __name__ == "__main__": main()