from kivy.app import App
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog

class HomeGpsHelper():
    has_centered_map = False
    dialog = None

    global lattitude
    lattitude = 44.3603999922373

    global longitude
    longitude = 2.575843426265557

    def run(self):
        # Get a reference to GpsBlinker, then call blink()
        home_gps_blinker = App.get_running_app().root.ids.home_screen.ids.mapview.ids.blinker

        # Start blinking the GpsBlinker
        home_gps_blinker.blink()

        # Request permissions on Android
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

    def update_blinker_position(self, *args, **kwargs):
        global lattitude
        lattitude = kwargs['lat']

        global longitude
        longitude = kwargs['lon']

        print("GPS POSITION", lattitude, longitude)
        # Update GpsBlinker position
        home_gps_blinker = App.get_running_app().root.ids.home_screen.ids.mapview.ids.blinker
        home_gps_blinker.lat = lattitude
        home_gps_blinker.lon = longitude

        App.get_running_app().root.ids.home_screen.ids.position.title = str(lattitude) +" ; "+str(longitude)

    def on_auth_status(self, general_status, status_message):
        print("GPS :", general_status)
        if general_status == 'provider-enabled':
            App.get_running_app().root.ids.home_screen.ids.gpsStatus.icon = "map-marker-check"
            pass
        else:
            print("Open gps access popup")
            App.get_running_app().root.ids.home_screen.ids.gpsStatus.icon = "map-marker-off"
            try:
                self.run_dialog()
            except:
                print("error")
                pass

    def run_dialog(self, *args):
        self.dialog = MDDialog(title="GPS", text="Le GPS n'est pas activé",
                               size_hint=(0.5, 0.5))
        self.dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        self.dialog.open()
        self.dialog = None

    def get_lat(self):
        return lattitude

    def get_long(self):
        return longitude
