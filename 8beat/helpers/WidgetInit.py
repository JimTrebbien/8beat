class WidgetInit:

    def init(self, builder, window):

        window.revealer = builder.get_object("stationDetailsRevealer")
        window.headerBar = builder.get_object("mainHeaderBar")
        window.headerBar.set_show_close_button(True)
        window.MainWindow.set_titlebar(window.headerBar)
        # menubuilder = Gtk.Builder.new_from_string(MENU_XML, -1)
        # window.Application.set_app_menu(menubuilder.get_object("app-menu"))

        window.lblNotificationMessage = builder.get_object("lblNotificationMessage")
        window.iconViewSpinner = builder.get_object("iconViewSpinner")
        window.notificationRevealer = builder.get_object("notificationRevealer")
        window.notificationBarFrame = builder.get_object("notificationBarFrame")

        window.newSearchStationsListStore = builder.get_object("newSearchStationsListStore")
        window.savedStationsListStore = builder.get_object("savedStationsListStore")
        window.activeStationPlayBarThumbnail = builder.get_object("activeStationPlayBarThumbnail")
        window.activeStationName = builder.get_object("activeStationPlayBarThumbnail")
        window.activeStationSong = builder.get_object("activeStationPlayBarThumbnail")
        window.lblDetailsStationName = builder.get_object("lblDetailsStationName")
        window.lblDetailsStationVotes = builder.get_object("lblDetailsStationVotes")
        window.lblDetailsStationLocation = builder.get_object("lblDetailsStationLocation")
        window.lblDetailsStationTags = builder.get_object("lblDetailsStationTags")
        window.lblDetailsStationCodec = builder.get_object("lblDetailsStationCodec")
        window.imgStationDetailsImage = builder.get_object("imgStationDetailsImage")
        window.lblSongName = builder.get_object("lblSongName")
        window.lblStationName = builder.get_object("lblStationName")
        window.volumeScaler = builder.get_object("volumeScaler")
        window.btnPlay = builder.get_object("btnPlay")
        window.playBtnImage = builder.get_object("playBtnImage")
        window.songNameLoadingSpinner = builder.get_object("songNameLoadingSpinner")
        window.imgSavedStationIcon = builder.get_object("imgSavedStationIcon")
        window.viewStack = builder.get_object("viewStack")
        window.stackFirstPage = builder.get_object("stackFirstPage")

        window.volumeScaler.set_value(50)
        window.volume_change(None, None, window.volumeScaler.get_value())

        window.newSearchIconView = builder.get_object("newSearchIconView")
        window.newSearchIconView.set_pixbuf_column(0)
        window.newSearchIconView.set_text_column(1)

        window.savedStationsIconView = builder.get_object("savedStationsIconView")
        window.savedStationsIconView.set_pixbuf_column(0)
        window.savedStationsIconView.set_text_column(1)


