from kivymd.app import MDApp
from kivy.app import App
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from searchpopupmenu import SearchPopupMenu
from homegpshelper import HomeGpsHelper
from kivy.lang import Builder
from homemapview import HomeMapView
from routemapview import RouteMapView
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivy.factory import Factory
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp
from kivy_garden.mapview import MapMarker
from marker import Marker
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()



from kivy.core.window import Window
#Window.size = (375, 750)

class HomeScreen(Screen):
    pass

class RouteScreen(Screen):
    pass

class MainApp(MDApp):

    #Menu pour rechercher
    search_menu = None

    def on_start(self):
        # https://kivymd.readthedocs.io/en/latest/themes/theming/
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Light"

        self.search_menu = SearchPopupMenu() #intialisation menu
        HomeGpsHelper().run() #initialisation GPS

    def open_bottom_sheet(self):
        self.custom = MDCustomBottomSheet(screen=Factory.CustomBottomSheet())
        self.custom.open()

    def close_bottom_sheet(self):
        self.custom.dismiss()

    #recherche d'adresse via la barre de recherche
    def search_adresse(self, adresse):
        if adresse == "":
            Snackbar(text="Le champ ne peut être vide", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
        else:
            adresse = adresse.replace(" ", "+")  # remplace les espaces par des '+'
            search_menu = SearchPopupMenu()
            SearchPopupMenu.call_geocode(search_menu, adresse)
            self.delete_search()

    #supprime le contenu de la barre de recherche
    def delete_search(self):
        App.get_running_app().root.ids.home_screen.ids.search_field.text=""
        App.get_running_app().root.ids.home_screen.ids.delete_search.icon=""

    #affiche le bouton de suppresion du contenu de la barre de recherche quand du texte est inscrit
    def print_delete_button(self):
        if App.get_running_app().root.ids.home_screen.ids.delete_search.icon == "":
            App.get_running_app().root.ids.home_screen.ids.delete_search.icon = "close-circle-outline"

    #pour changer d'écran
    def change_screen(self, screen_name):
        screenManager = self.root.ids.screen_manager
        screenManager.transition = CardTransition(direction="left", mode="push")
        screenManager.current = screen_name

        if(screen_name == "home_screen"):
            #Remise a 0 des champs
            App.get_running_app().root.ids.route_screen.ids.etapesItineraire.clear_widgets()
            App.get_running_app().root.ids.route_screen.ids.distTemps.secondary_text = ""
            App.get_running_app().root.ids.route_screen.ids.distTemps.text = ""
            App.get_running_app().root.ids.route_screen.ids.adresseAct.text = ""
            App.get_running_app().root.ids.route_screen.ids.adresseDest.text = ""

            #Supression des marqueurs
            for x in App.get_running_app().root.ids.route_screen.ids.mapview.walk():
                if x.__class__ == MapMarker:
                    App.get_running_app().root.ids.route_screen.ids.mapview.remove_marker(x)
                else:
                    continue

    #centrage de la carte sur la position actuelle de l'utilisateur
    def center_map(self):
        map2 = App.get_running_app().root.ids.home_screen.ids.mapview
        map2.center_on(HomeGpsHelper.get_lat(self), HomeGpsHelper.get_long(self))

    def check_gps_status(self):
        if App.get_running_app().root.ids.home_screen.ids.gpsStatus.icon == "map-marker-off":
            Snackbar(text="GPS désactivé", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
        else:
            Snackbar(text="GPS activé", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()



MainApp().run()

