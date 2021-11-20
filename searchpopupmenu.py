import urllib

from homegpshelper import HomeGpsHelper
from kivymd.uix.dialog import MDInputDialog
from kivy.uix.screenmanager import CardTransition
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.list import ThreeLineAvatarIconListItem
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.list import IconLeftWidget
from time import strftime
import time
from kivy_garden.mapview import MapMarker

import geopy
from geopy import Nominatim






class SearchPopupMenu(MDInputDialog):
    title = "Saisisez l'adresse de destination"
    text_button_ok = "Y-aller"


    #adresse origine
    global codePostalOrigin

    #adresse de destination
    global latDes, lonDes, adresseCompleteDes, codePostalDes
    adresseCompleteDes = []

    #api nominatim
    global headerURL

    headerURL = {
        'User-Agent': 'PythonApp'
    }


    global app_code
    app_code = "Y9SQb-wvJonInc2hvZ7_32hQqPpWlexBbOvwyyo5QX4"  # code api


    def __init__(self):
        super().__init__()
        self.size_hint = [.9, .25]
        self.events_callback = self.callback

########################################################################################################################
    #Déroulement des évenements
    #1-
    #2-
    #3-
    #4-
    #5-


    def callback(self, *args):

        # méthode appellee lors du click sur le bouton 'Y-aller'
        adresse = self.text_field.text

        if(adresse == ""):
            Snackbar(text="Veuillez entrer une adresse", snackbar_x="10dp", snackbar_y="10dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
        else:
            #si le gps est activé
            if App.get_running_app().root.ids.home_screen.ids.gpsStatus.icon == "map-marker-off":
                Snackbar(text="Impossible de récupérer votre position actuelle.", snackbar_x="10dp", snackbar_y="10dp",
                         size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
            else:
                adresse = adresse.replace(" ", "+")  # remplace les espaces par des '+'
                adresse = urllib.parse.quote(adresse, safe="")
                self.call_geocode(adresse)


    ####### Méthode pour la requete qui récupère les coordonnées de l'adresse souhaitée
    #lors du succès de callback
    def call_geocode(self,adresse):
        urlGeocode = "https://nominatim.openstreetmap.org/search?q="+adresse+"&format=json&addressdetails=1"
        print(urlGeocode)
        UrlRequest(urlGeocode,
                   on_success=self.success_geocode,
                   on_failure=self.failure_geocode,
                   on_error=self.error_geocode,
                   req_headers=headerURL)

    def success_geocode(self, urlrequest, result):
        print("GEOCODE SUCCES ",urlrequest)

        # succes de l'appel URL
        try:
            if len(result) > 0:

                global latDes
                latDes = result[0]['lat']

                global lonDes
                lonDes = result[0]['lon']

                global adresseCompleteDes
                adresseCompleteDes = []
                if "house_number" in result[0]["address"]:
                    if "road" in result[0]["address"]:
                        adresseCompleteDes.append(
                            result[0]["address"]['house_number'] + " " + result[0]["address"]['road'])
                    else:
                        adresseCompleteDes.append("")
                else:
                    if "road" in result[0]["address"]:
                        adresseCompleteDes.append(result[0]["address"]['road'])
                    else:
                        adresseCompleteDes.append("")


                if "postcode" in result[0]["address"]:
                    if "town" in result[0]["address"]:
                        adresseCompleteDes.append(
                            result[0]["address"]['postcode'] + " " + result[0]["address"]['town'])
                    else:
                        adresseCompleteDes.append(result[0]["address"]['postcode'])
                else:
                    if "road" in result[0]["address"]:
                        adresseCompleteDes.append(result[0]["address"]['road'])
                    else:
                        adresseCompleteDes.append("")


                global codePostalDes
                codePostalDes = result[0]['address']['postcode']

                print("GOECODE RES :", adresseCompleteDes, lonDes, latDes, codePostalDes)
                print("COORDONNEES ACTUELLES :", HomeGpsHelper.get_lat(self), HomeGpsHelper.get_long(self))

                #vérification des codes postaux
                urlCodePostaux = "https://nominatim.openstreetmap.org/reverse?format=json&"\
                                 "lat="+str(HomeGpsHelper.get_lat(self))+\
                                 "&lon="+str(HomeGpsHelper.get_long(self))+\
                                 "&addressdetails=1"
                print("CODE POSTAUX URL : ", urlCodePostaux)

                UrlRequest(urlCodePostaux,
                           on_success=self.success_verif_post_code,
                           on_failure=self.failure_verif_post_code,
                           on_error=self.error_verif_post_code,
                           req_headers=headerURL)

            else:
                Snackbar(text="Aucune adresse correspondante n'a été trouvée", snackbar_x="10dp", snackbar_y="10dp",
                        size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
        except:
            Snackbar(text="Une erreur est survenue pendant la recherche", snackbar_x="10dp", snackbar_y="10dp",
            size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

    #lors de l'échec de geocodeGEtLongLat
    def failure_geocode(self, urlrequest, result):
        # echec de l'appel URL
        print("GEOCODE ECHEC",urlrequest)
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

    # si erreur lors de l'appel à geocodeGEtLongLat
    def error_geocode(self, urlrequest, result):
        # erreur de l'appel URL
        print("GEOCODE ERREUR",urlrequest)
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                 size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()


    ####### Méthodes pour la requete qui vérifie les codes postaux
    def success_verif_post_code(self, urlrequest, result):
        print("VERIF CODE POSTAUX SUCCES",urlrequest)
        codePostal = result["address"]["postcode"]

        libAdressAct = []
        libAdressAct.append(result["address"]['house_number'] + " " + result["address"]['road'])
        libAdressAct.append(result["address"]['postcode'] + " " + result["address"]['town'])

        if codePostal == codePostalDes :
            # appel au WS pour calcul de l'itinéraire via méthode 'define_route'
            self.define_route(HomeGpsHelper.get_long(self), HomeGpsHelper.get_lat(self), lonDes, latDes,
                              adresseCompleteDes, libAdressAct)
        else:
            Snackbar(text="L'adresse demandée n'est pas dans la même région", snackbar_x="20dp", snackbar_y="20dp",
                     size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()


    #echec de l'appel au WS pour l'itinéraire
    def failure_verif_post_code(self,urlrequest, result):
        # echec de l'appel URL
        print("VERIF CODE POSTAUX ECHEC",urlrequest)
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                 size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

    #erreur lors de l'appel au WS pour l'itinéraire
    def error_verif_post_code(self, urlrequest, result):
        # erreur de l'appel URL
        print("VERIF CODE POSTAUX ERREUR",urlrequest)
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
            App.get_running_app().root.ids.route_screen.ids.adresseAct.text = libAdressAct[0]
            App.get_running_app().root.ids.route_screen.ids.adresseAct.secondary_text = libAdressAct[1]
            App.get_running_app().root.ids.route_screen.ids.adresseDest.text = adreseDest[0]
            App.get_running_app().root.ids.route_screen.ids.adresseDest.secondary_text = adreseDest[1]

            # Appel l'url du WS
            UrlRequest(routeUrl, on_success=self.success_route, on_failure=self.failure_route,
                       on_error=self.error_route)

    #succès de l'appel au WS pour l'itinéraire
    def success_route(self, urlrequest, result):
        print("ROUTE SUCCES",urlrequest)

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
            icon2 = ""
            name = ""

            etapeItineraire = App.get_running_app().root.ids.route_screen.ids.etapesItineraire #la grille qui contient toute les étapes
            for i in range(0, len(result["routes"][0]["legs"][0]["steps"])):



                #modifier = le type de diretion à prendre
                if "modifier" in result["routes"][0]["legs"][0]["steps"][i]["maneuver"]:
                    modifierMatch = result["routes"][0]["legs"][0]["steps"][i]["maneuver"]["modifier"]

                    if modifierMatch == "left":
                        modifier = " à gauche"
                        icon = IconLeftWidget(icon="icons/left.png")

                    elif modifierMatch == "slight left":
                        modifier = " légèrement à gauche"
                        icon = IconLeftWidget(icon="icons/slight_left.png")

                    elif modifierMatch ==  "sharp left":
                        modifier = " complètement à gauche"
                        icon = IconLeftWidget(icon="icons/left.png")

                    elif modifierMatch ==  "right":
                        modifier = " à droite"
                        icon = IconLeftWidget(icon="icons/right.png")

                    elif modifierMatch ==  "sharp right":
                        modifier = " complètement à droite"
                        icon = IconLeftWidget(icon="icons/right.png")

                    elif modifierMatch ==  "slight right":
                        modifier = " légèrement à doite"
                        icon = IconLeftWidget(icon="icons/slight_right.png")

                    elif modifierMatch ==  "straight":
                        modifier = " tout droit"
                        icon = IconLeftWidget(icon="icons/straight.png")

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


                #icons
                if i == 0:
                    icon = IconLeftWidget(icon = "icons/depart.png")

                elif i+1 == len(result["routes"][0]["legs"][0]["steps"]):
                    icon = IconLeftWidget(icon = "icons/finish.png")
                else:
                    icon = icon

                # ajout des étapes
                if type == "Démarrez":
                    #démarrage du parcours
                    if name == "":
                        #pas de nom de rue de départ
                        item = TwoLineAvatarIconListItem(text="Départ", secondary_text=distanceEtape)
                        item.add_widget(icon)
                        etapeItineraire.add_widget(item)
                    else:
                        #nom de rue de départ
                        item = ThreeLineAvatarIconListItem(text=type, secondary_text=name,tertiary_text=distanceEtape)
                        item.add_widget(icon)
                        etapeItineraire.add_widget(item)

                elif type == "Arrivez":
                    #fin du parcours
                    item = TwoLineAvatarIconListItem(text="Arrivée", secondary_text=distanceEtape)
                    item.add_widget(icon)
                    etapeItineraire.add_widget(item)
                else:
                    #etape du parcours
                    if(name != ""):
                        #un nom de rue est présent
                        item = ThreeLineAvatarIconListItem(text=type+modifier, secondary_text=name,tertiary_text=distanceEtape)
                        item.add_widget(icon)
                        etapeItineraire.add_widget(item)
                    else:
                        #pas de nom  de rue
                        item = TwoLineAvatarIconListItem(text=type +modifier, secondary_text=distanceEtape)
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
        print("ROUTE ECHEC",urlrequest)
        print(result)

        Snackbar(text="Une erreur est survenue.", snackbar_x="10dp", snackbar_y="10dp",
                 size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()

    #erreur lors de l'appel au WS pour l'itinéraire
    def error_route(self, urlrequest, result):
        # erreur de l'appel URL
        print("ROUTE ERREUR",urlrequest)
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