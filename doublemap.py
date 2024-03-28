import requests

organization = "ucf"
URL = "http://" + organization + ".doublemap.com/map/v2/"

def get_buses():
    response = requests.get(URL + "buses")
    return response.json()

def is_route_active(route_id):
    response = requests.get(URL + "routes?id=" + str(route_id))
    return response.json()['active']

def get_etas(stop_id):
    response = requests.get(URL + "eta?stop=" + str(stop_id))
    etas = response.json()['etas'][str(stop_id)]['etas']
    # min = 1000
    # for eta in etas:
    #     if eta['route'] == int(route_id) and int(eta['avg']) < min:
    #         min = eta.get("avg")
    return etas