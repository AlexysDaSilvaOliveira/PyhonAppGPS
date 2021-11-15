
from homegpshelper import HomeGpsHelper
from kivymd.uix.dialog import MDInputDialog
from kivy.uix.screenmanager import CardTransition
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.list import ThreeLineIconListItem
from kivymd.uix.list import TwoLineIconListItem
from kivymd.uix.list import IconLeftWidget
from time import strftime
from time import gmtime
import time
from marker import Marker
from kivy_garden.mapview import MapMarker
from routemapview import RouteMapView




class SearchPopupMenu(MDInputDialog):
    title = "Saisisez l'adresse de destination"
    text_button_ok = "Y-aller"

    #variables globales
    global latDes, lonDes, adresseComplete, codePostalOrigin, app_code
    latDes = 0
    lonDes = 0
    adresseComplete = ""
    app_code = "Y9SQb-wvJonInc2hvZ7_32hQqPpWlexBbOvwyyo5QX4"  # code api

    def __init__(self):
        super().__init__()
        self.size_hint = [.9, .25]
        self.events_callback = self.callback

########################################################################################################################
    #Déroulement des évenements
    #1- appel à l'api here pour obtenir les coordonnées de l'adresse voulue avec 'geocode_get_long_lat'
    #2-traitement de l'appel à l'api, si réussite appel, traitement données dans 'success_geocode'
    #3-vérification des codes postaux de la position actuelle et de la position demandée via success_verif_post_code
    #4-récupération de l'itinéraire dans 'define_route'
    #5-ouverture de la page présentant l'itinéraire


    def callback(self, *args):


        # méthode appellee lors du click sur le bouton 'Y-aller'
        adresse = self.text_field.text

        if(adresse == ""):
            Snackbar(text="Veuillez entrer une adresse", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
        else:
            adresse = adresse.replace(" ", "+")  # remplace les espaces par des '+'
            self.geocode_get_long_lat(adresse)

    #retourne la position demandée par l'utilisateur en geocode
    def geocode_get_long_lat(self, adresse):
        # on vérifie si la position actuelle est connue
        if App.get_running_app().root.ids.home_screen.ids.gpsStatus.icon == "map-marker-off":
            Snackbar(text="Impossible de récupérer votre position actuelle.", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
        else:

            url = "https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey=" + app_code + "&searchtext=" + adresse
            print("GEOCODE URL : ", url)
            UrlRequest(url, on_success=self.success_geocode, on_failure=self.failure_geocode, on_error=self.error_geocode)  # appel URL


    ####### Méthode pour la requete qui récupère les coordonnées de l'adresse souhaitée
    #lors du succès de geocodeGEtLongLat
    def success_geocode(self, urlrequest, result):
        print("GEOCODE SUCCES")

        # succes de l'appel URL
        #try:
        if len(result['Response']['View']) > 0:
            for i in range(0, len(result['Response']['View'][0]['Result'])):
                if result['Response']['View'][0]['Result'][0]['Location']['Address']['Country'] == "FRA":
                    global latDes
                    latDes = result['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Latitude']

                    global lonDes
                    lonDes = result['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Longitude']

                    global adresseComplete
                    adresseComplete = result['Response']['View'][0]['Result'][0]['Location']['Address']['Label']

                    global codePostalOrigin
                    codePostalOrigin = result['Response']['View'][0]['Result'][0]['Location']['Address']['PostalCode']

            if(latDes == 0 and lonDes == 0):
                Snackbar(text="Aucun résultat proche", snackbar_x="10dp", snackbar_y="10dp",
                         size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
            else:
                print("GOECODE RES :", adresseComplete, lonDes, latDes, codePostalOrigin)
                print("COORDONNEES ACTUELLES :", HomeGpsHelper.get_lat(self), HomeGpsHelper.get_long(self))

                #vérification des codes postaux

                urlCodePostaux = "https://revgeocode.search.hereapi.com/v1/revgeocode?apiKey="+app_code+"&at="\
                                +str(HomeGpsHelper.get_lat(self))\
                                +","\
                                +str(HomeGpsHelper.get_long(self))
                print("CODE POSTAUX URL : ",urlCodePostaux)

                UrlRequest(urlCodePostaux,
                           on_success=self.success_verif_post_code,
                           on_failure=self.failure_verif_post_code,
                           on_error=self.error_verif_post_code)




        else:
            Snackbar(text="Aucune adresse correspondante n'a été trouvée", snackbar_x="10dp", snackbar_y="10dp",
                    size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
        #except:
         #   Snackbar(text="Une erreur est survenue pendant la recherche", snackbar_x="10dp", snackbar_y="10dp",
          #        size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

    #lors de l'échec de geocodeGEtLongLat
    def failure_geocode(self, urlrequest, result):
        # echec de l'appel URL
        print("GEOCODE ECHEC")
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

    # si erreur lors de l'appel à geocodeGEtLongLat
    def error_geocode(self, urlrequest, result):
        # erreur de l'appel URL
        print("GEOCODE ERREUR")
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                 size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()


    ####### Méthodes pour la requete qui vérifie les codes postaux
    def success_verif_post_code(self, urlrequest, result):
        print("VERIF CODE POSTAUX SUCCES")
        codePostal = result["items"][0]["address"]["postalCode"]
        libAdressAct = result["items"][0]["address"]["label"]

        if codePostal == codePostalOrigin :
            # appel au WS pour calcul de l'itinéraire via méthode 'define_route'
            self.define_route(HomeGpsHelper.get_long(self), HomeGpsHelper.get_lat(self), lonDes, latDes,
                              adresseComplete, libAdressAct)
        else:
            Snackbar(text="L'adresse demandée n'est pas dans la même région", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()


    #echec de l'appel au WS pour l'itinéraire
    def failure_verif_post_code(self,urlrequest, result):
        # echec de l'appel URL
        print("VERIF CODE POSTAUX ECHEC")
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                 size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

    #erreur lors de l'appel au WS pour l'itinéraire
    def error_verif_post_code(self, urlrequest, result):
        # erreur de l'appel URL
        print("VERIF CODE POSTAUX ERREUR")
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                 size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()



    ####### Méthodes pour la requete qui récupère l'itinéraire

    # récupération de l'itinéraire
    def define_route(self, lonOrigin, latOrigin, lonDest, lattDest, adreseDest, libAdressAct):
            routeUrl = "https://routing.openstreetmap.de/routed-foot/route/v1/driving/" + str(lonOrigin) + "," + str(
                latOrigin) + ";" + str(lonDest) + "," + str(lattDest) + "?overview=false&geometries=polyline&steps=true"
            # routeUrl = "https://routing.openstreetmap.de/routed-foot/route/v1/driving/2.5621,44.3498;2.5764,44.36?overview=false&geometries=polyline&steps=true"; #TODO supprimer l'url de test
            print("DEFINE ROUTE URL : ", routeUrl)

            # mise a jour des infos sur la position actuelle et la destination
            App.get_running_app().root.ids.route_screen.ids.adresseAct.text = libAdressAct
            App.get_running_app().root.ids.route_screen.ids.adresseDest.text = adreseDest

            # Appel l'url du WS
            UrlRequest(routeUrl, on_success=self.success_route, on_failure=self.failure_route,
                       on_error=self.error_route)

    #succès de l'appel au WS pour l'itinéraire
    def success_route(self, urlrequest, result):
        print("ROUTE SUCCES")

        if result["code"] == "Ok": #si le WS a renvoyé un code "Ok" = un itinéraire est disponible

            # affichage de la distance et du temps
            distance = result["routes"][0]["distance"]
            temps = result["routes"][0]["duration"]

            #distance
            if distance >= 1000:
                distance = distance/1000
                App.get_running_app().root.ids.route_screen.ids.distTemps.secondary_text = str(distance)+" km"
            else:
                App.get_running_app().root.ids.route_screen.ids.distTemps.secondary_text = str(distance) + " m"

            #temps
            if temps >= 3600:
                print(strftime("%H h %M",time.gmtime(temps)))
                App.get_running_app().root.ids.route_screen.ids.distTemps.text = strftime("%H h %M",
                                                                                                    time.gmtime(temps))
            elif temps >= 60:
                App.get_running_app().root.ids.route_screen.ids.distTemps.text = strftime("%M min",
                                                                                                    time.gmtime(temps))
            else:
                App.get_running_app().root.ids.route_screen.ids.distTemps.text = str(temps) + "s"

            #affichage des étapes

            modifier = ""
            type = ""
            distanceEtape = ""  # la distance à parcourir avant la prochaine étape
            icon = ""
            name = ""

            etapeItineraire = App.get_running_app().root.ids.route_screen.ids.etapesItineraire #la grille qui contient toute les étapes
            for i in range(0, len(result["routes"][0]["legs"][0]["steps"])):

                if i == 0:
                    icon = IconLeftWidget(icon = "source-commit-start")
                elif i+1 == len(result["routes"][0]["legs"][0]["steps"]):
                    icon = IconLeftWidget(icon = "source-commit-end")
                else:
                    icon = IconLeftWidget(icon = "source-commit")


                #modifier = le type de diretion à prendre
                if "modifier" in result["routes"][0]["legs"][0]["steps"][i]["maneuver"]:
                    modifierMatch = result["routes"][0]["legs"][0]["steps"][i]["maneuver"]["modifier"]

                    if modifierMatch == "left":
                        modifier = " à gauche"

                    elif modifierMatch == "slight left":
                        modifier = " légèrement à gauche"

                    elif modifierMatch ==  "sharp left":
                        modifier = " complètement à gauche"

                    elif modifierMatch ==  "right":
                        modifier = " à droite"

                    elif modifierMatch ==  "sharp right":
                        modifier = " complètement à droite"

                    elif modifierMatch ==  "slight right":
                        modifier = " légèrement à doite"

                    elif modifierMatch ==  "straight":
                        modifier = " tout droit"

                    else:
                        #defaut
                        modifier = result["routes"][0]["legs"][0]["steps"][i]["maneuver"]["modifier"]
                else:
                    modifier = ""


                #type = le type d'action a effectuer
                modifierType = result["routes"][0]["legs"][0]["steps"][i]["maneuver"]["type"]

                if modifierType ==  "turn":
                    type = "Tourner"
                elif modifierType == "depart":
                    type = "Démarrez"
                elif modifierType == "arrive":
                    type = "Arrivez"
                elif modifierType == "new name":
                    type = "Continuez"
                elif modifierType == "merge":
                    type = "Continuez"
                elif modifierType == "on ramp":
                    type = "Entrez"
                elif modifierType == "off ramp":
                    type = "Sortez"
                elif modifierType == "fork":
                    type = "A l'intersection prenez"
                elif modifierType == "end of road":
                    type = "En fin de route, tournez"
                elif modifierType == "continue":
                    type = "Tournez"
                elif modifierType == "roundabout":
                    type = "Tournez"


                #distance
                distanceEtape = result["routes"][0]["legs"][0]["steps"][i]["distance"]
                if distanceEtape > 1000:
                    distanceEtape = distanceEtape / 1000
                    distanceEtape = str(distanceEtape)+" km"
                else:
                    distanceEtape = str(distanceEtape)+" m"

                #nom de la rue
                if result["routes"][0]["legs"][0]["steps"][i]["name"] == "":
                    name =""
                else:
                    name = "sur "+result["routes"][0]["legs"][0]["steps"][i]["name"]


                if type == "Démarrez":
                    #démarrage du parcours
                    if name == "":
                        #pas de nom de rue de départ
                        item = TwoLineIconListItem(text="Départ", secondary_text=distanceEtape)
                        item.add_widget(icon)
                        etapeItineraire.add_widget(item)
                    else:
                        #nom de rue de départ
                        item = ThreeLineIconListItem(text=type, secondary_text=name,tertiary_text=distanceEtape)
                        item.add_widget(icon)
                        etapeItineraire.add_widget(item)

                elif type == "Arrivez":
                    #fin du parcours
                    item = TwoLineIconListItem(text="Arrivée", secondary_text=distanceEtape)
                    item.add_widget(icon)
                    etapeItineraire.add_widget(item)
                else:
                    #etape du parcours
                    if(name != ""):
                        #un nom de rue est présent
                        item = ThreeLineIconListItem(text=type+modifier, secondary_text=name,tertiary_text=distanceEtape)
                        item.add_widget(icon)
                        etapeItineraire.add_widget(item)
                    else:
                        #pas de nom  de rue
                        item = TwoLineIconListItem(text=type +modifier, secondary_text=distanceEtape)
                        item.add_widget(icon)
                        etapeItineraire.add_widget(item)

                #ajout des marqueurs
                self.add_marker(result["routes"][0]["legs"][0]["steps"][i]["maneuver"]["location"][1],
                                result["routes"][0]["legs"][0]["steps"][i]["maneuver"]["location"][0],
                                i,
                                len(result["routes"][0]["legs"][0]["steps"]))

            # affichage de l'écran pour l'itinéraire
            self.change_screen("route_screen")


        else:
            Snackbar(text="Impossible de récupérer l'itinéraire", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

            App.get_running_app().root.ids.route_screen.ids.adresseAct.text = "Non connu"
            App.get_running_app().root.ids.route_screen.ids.adresseDest.text = "Non connu"

    #echec de l'appel au WS pour l'itinéraire
    def failure_route(self,urlrequest, result):
        # echec de l'appel URL
        print("ROUTE ECHEC")
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                 size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

    #erreur lors de l'appel au WS pour l'itinéraire
    def error_route(self, urlrequest, result):
        # erreur de l'appel URL
        print("ROUTE ERREUR")
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                 size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()



    # ajout des marqueurs à la carte
    def add_marker(self, lat, lon, i, lenresult):
        if i == 0:
            marker = MapMarker(lat=lat, lon=lon, source="icons/point2.png")
        elif i + 1 == lenresult:
            marker = MapMarker(lat=lat, lon=lon, source="icons/point3.png")
        else:
            marker = MapMarker(lat=lat, lon=lon, source="icons/point.png")
        App.get_running_app().root.ids.route_screen.ids.mapview.add_marker(marker)

    # pour changer d'écran lors de l'appui sur la flèche retour
    def change_screen(self, screen_name):
        screenManager = App.get_running_app().root.ids.screen_manager

        screenManager.transition = CardTransition(direction="left", mode="push")
        screenManager.current = screen_name