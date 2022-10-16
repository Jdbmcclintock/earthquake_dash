import pandas as pd
import requests
from datetime import datetime, timedelta
from obspy.clients.fdsn import Client
client = Client("GEONET")
nrt_client = Client("http://service-nrt.geonet.org.nz")
 
def get_last_month():
    thirty_days = datetime.now() - timedelta(days=30)
    thirty_days_str = thirty_days.strftime("%Y-%m-%dT%H:%M:%S")
    return thirty_days_str
 
 
def last_months_json(thirty_days_str):
    json = requests.get("http://wfs.geonet.org.nz/geonet/ows?service=WFS&version=1.0.0&request=GetFeature&type"
                 "Name=geonet:quake_search_v1&outputFormat=json&cql_filter=origintime>=" + thirty_days_str).json()
    return json
 
def extract_json(json):
    lon, lat, mag, quakeid, origtime, depth = [[] for i in range(6)]
 
    for i in json['features']:
        lon.append(i['geometry']['coordinates'][0])
        lat.append(i['geometry']['coordinates'][1])
        mag.append(i['properties']['magnitude'])
        quakeid.append(i['properties']['publicid'])
        origtime.append(i['properties']['origintime'])
        depth.append(i['properties']['depth'])
 
    df = pd.DataFrame({"quakeid": quakeid, "longitude": lon, "latitude": lat, "magnitude": mag, "origintime": origtime, "depth":depth})
 
    df["energy"] = [10 ** (1.44 * i + 5.24) for i in mag]
    df["TNT"] = df["energy"] / (4.184 * 10 ** 9)
 
    return df
 
def convert_tnt(total_tnt):
 
    if total_tnt < 1000:
        unit = " tons of TNT equivalent"
        converted = total_tnt
    elif total_tnt >= 1000 and total_tnt < 1000000:
        unit = " kilotons of TNT equivalent"
        converted = round(total_tnt / 1000)
    elif total_tnt >= 1000000:
        unit = " megatons of TNT equivalent"
        converted = round(total_tnt / 1000000, 1)
    return converted, unit
 
def get_obspy_text(quakeid_latest):
    try:
        get_obsp_loc = client.get_events(eventid=quakeid_latest)
    except:
        get_obsp_loc = nrt_client.get_events(eventid=quakeid_latest)
    location = get_obsp_loc[0].event_descriptions[0].text
    try:
        magnitude = "M " + str(round(get_obsp_loc[0].preferred_magnitude().mag, 1))
    except:
        magnitude = "M " + str(round(requests.get("https://api.geonet.org.nz/quake/"
                                                  + quakeid_latest).json()['features'][0]['properties']['magnitude']
        , 1))
    return location, magnitude
 
