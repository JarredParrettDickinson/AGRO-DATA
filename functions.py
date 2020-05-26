
import pandas as pd
import numpy as np
import urllib
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
import geojson
from geojson import Feature, Point, FeatureCollection, Polygon

def make_bins_for_cat(df):
    merged = df.copy()
    #per request work - make bins and add to sheet
    merged['val_bins'] = (pd.cut(x=merged['VALUE'], bins=16))
    merged['val_bins']=merged['val_bins'].astype(str)
    return merged

#per request work - for bin - df - make geoJson objects
#find subset
#make feature collection
#for each row, make featrue and add to feature collection
#https://pypi.org/project/geojson/#feature
def make_geo_json(df):
    feature_array = []
    for _, row in df.iterrows():
        poly = row["geometry"]
        tuple_list = poly_to_tuple_list(poly)
        tuple_list_Arr = []
        tuple_list_Arr.append(tuple_list)
        poly = Polygon(coordinates=tuple_list_Arr)
        dict_ft = make_properties_dict(row)
        feature = Feature(geometry=poly, properties=dict_ft)
        feature_array.append(feature)
    feature_collection = geojson.FeatureCollection(features=feature_array) 
    return feature_collection

def poly_to_tuple_list(poly):
  poly = str(poly)
  poly = poly[10:-2]
  if "ON" in poly:
      #print(poly)
      poly = poly.replace("(","")
      poly = poly.replace(")","")
      poly = poly.replace("ON ","")
      #print(poly)
  poly_arr = poly.split(", ")
  tuple_list = []
  for pair in poly_arr:
      pair = pair.replace(")","")
      pair = pair.replace("(","")
      pair_arr = pair.split(' ', 2)
      #try:
      cords = (np.ndarray.item(np.array(float(pair_arr[0]))),np.ndarray.item(np.array((float(pair_arr[1])))))
      #except:
      #cords = []
      #print(poly_arr)
      #print("not made")
      tuple_list.append(cords)
  return tuple_list

def make_properties_dict(row):
    dict = { "id": row["id"], "name": row["name"], "Unnamed: 0": row["Unnamed: 0"], "SOURCE_DESC": row["SOURCE_DESC"], "SECTOR_DESC": row["SECTOR_DESC"], "GROUP_DESC": row["GROUP_DESC"], "COMMODITY_DESC": row["COMMODITY_DESC"], "VALUE":row["VALUE"], "COUNTY_FIP": row["COUNTY_FIP"], "val_bins": row["val_bins"]}
    return dict

def get_center_lat_long(STATE_ALPHA):
    df = pd.read_csv("./data/State_Lat_Long_Center.csv")
    df_state = df.loc[(df["STATE"] == str(STATE_ALPHA))]
    lat = df_state['LAT'].iloc[0]
    lon = df_state['LONG'].iloc[0]
    return lat, lon

def get_sub_df(df, unit, cat, year, state):
    df_cur = df.loc[(df["SHORT_DESC"] == str(cat))]
    
    if state != "United States" and state != None:
        df_cur = df_cur.loc[(df_cur["STATE_ALPHA"] == str(state))]

        
    if str(year) != "NOT SPECIFIED" and year != None:
        df_cur = df_cur.loc[(df_cur["YEAR"] == int(year))]


    if unit != "NOT SPECIFIED" and unit != None:
        df_cur = df_cur.loc[(df_cur["DOMAINCAT_DESC"] == str(unit))]

    return df_cur

def add_state_county_string(df):
    new_col = []
    for ind in df.index:
        county = (df["COUNTY_NAME"][ind])
        state = (df["STATE_ALPHA"][ind])
        col_val = str(county)+","+str(state)
        new_col.append(str(col_val))
    df["STATE_COUNTY"]=new_col
    return df