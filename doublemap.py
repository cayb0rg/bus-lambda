import requests

organization = "ucf"
URL = "http://" + organization + ".doublemap.com/map/v2/"

# Get all of the buses
def get_buses():
    response = requests.get(URL + "buses")
    return response.json()

# Get the route information for a route
def get_route(route_id):
    response = requests.get(URL + "routes?id=" + str(route_id))
    return response.json()

# Check if a route is active
def is_route_active(route_id):
    response = requests.get(URL + "routes?id=" + str(route_id))
    return response.json()['active']

# Get the etas for a stop
def get_etas(stop_id):
    response = requests.get(URL + "eta?stop=" + str(stop_id))
    etas = response.json()['etas'][str(stop_id)]['etas']
    return etas

# Get the minimum eta for a stop
def get_min_eta(stop_id):
    etas = get_etas(stop_id)
    min = 1000
    for eta in etas:
        if int(eta['avg']) < min:
            min = int(eta['avg'])
    return min

# Get the information for the last stop a bus was at
def get_last_stop_info(bus_id):
    response = requests.get(URL + "buses")
    buses = response.json()
    for bus in buses:
        if bus['id'] == bus_id:
            last_stop = bus['lastStop']
            bus_info = requests.get(URL + "stops?id=" + str(last_stop))
            bus_info = bus_info.json()
            return bus_info
    return None