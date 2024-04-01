import requests

organization = "ucf"
URL = "http://" + organization + ".doublemap.com/map/v2/"

def get_buses():
    response = requests.get(URL + "buses")
    return response.json()

def is_route_active(route_id):
    response = requests.get(URL + "routes?id=" + str(route_id))
    return response.json()['active']

def get_route(route_id):
    response = requests.get(URL + "routes?id=" + str(route_id))
    return response.json()

def get_etas(stop_id):
    response = requests.get(URL + "eta?stop=" + str(stop_id))
    etas = response.json()['etas'][str(stop_id)]['etas']
    return etas

def get_min_eta(stop_id):
    etas = get_etas(stop_id)
    min = 1000
    for eta in etas:
        if int(eta['avg']) < min:
            min = int(eta['avg'])
    return min

def get_last_stop(bus_id):
    response = requests.get(URL + "buses")
    buses = response.json()
    for bus in buses:
        if bus['id'] == bus_id:
            return bus['lastStop']
    return None