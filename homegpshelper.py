from kivy.app import App
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog

class HomeGpsHelper():
    has_centered_map = False
    dialog = None

    global lattitude
    #coordoonées par défaut sur Rodez
    lattitude = 44.3603999922373

    global longitude
    longitude = 2.575843426265557

    def run(self):
        # Référence au blinker
        home_gps_blinker = App.get_running_app().root.ids.home_screen.ids.mapview.ids.blinker

        # on démarre l'animation du blinker
        home_gps_blinker.blink()

        # Permissions pour Android
        if platform == 'android':
            from android.permissions import Permission, request_permissions
            def callback(permission, results):
                if all([res for res in results]):
                    print("Got all permissions")
                    from plyer import gps
                    gps.configure(on_location=self.update_blinker_position, on_status=self.on_auth_status)
                    gps.start(minTime=1000, minDistance=1)

                else:
                    print("Did not get all permissions")

            request_permissions([Permission.ACCESS_COARSE_LOCATION,
                                 Permission.INTERNET,
                                 Permission.ACCESS_FINE_LOCATION], callback)

    #màj de la position du blinker en fonction de la position de l'utilsateur
    def update_blinker_position(self, *args, **kwargs):
        global lattitude
        lattitude = kwargs['lat']

        global longitude
        longitude = kwargs['lon']

        print("GPS POSITION", lattitude, longitude)
        # màj de la position du blinker
        home_gps_blinker = App.get_running_app().root.ids.home_screen.ids.mapview.ids.blinker
        home_gps_blinker.lat = lattitude
        home_gps_blinker.lon = longitude

        #affichage des coordonnées de l'utilisateur
        App.get_running_app().root.ids.home_screen.ids.position.title = str(lattitude) +" ; "+str(longitude)

    def on_auth_status(self, general_status, status_message):
        print("GPS :", general_status)
        if general_status == 'provider-enabled':
            App.get_running_app().root.ids.home_screen.ids.gpsStatus.icon = "map-marker-check"
            pass
        else:
            print("Open gps access popup")
            App.get_running_app().root.ids.home_screen.ids.gpsStatus.icon = "map-marker-off"

    def get_lat(self):
        return lattitude

    def get_long(self):
        return longitude
