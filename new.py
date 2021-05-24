from flask import Flask,render_template,request, url_for, redirect,flash
from werkzeug.utils import secure_filename

import gmaps
import pandas as pd
import matplotlib.pyplot as plt
import random 
#from shapely.geometry import Point,Polygon
import pickle
#import geopandas as gpd
import math
import random
import requests
import csv
import os
import os.path
from math import radians, cos, sin, asin, sqrt

from ipywidgets.embed import embed_minimal_html

from sklearn.cluster import KMeans


app = Flask(__name__)
app.config['DEBUG']= True

pd.options.mode.chained_assignment = None

apikey = "AIzaSyC4KrjejjTOAO_61zp7kSHfapldfDZq6go" #googlemaps key

clu_num=10

centroid_address=[] #storing centroid's address after calling api
#centroid_address=pickle.load(open('centroid_address.dat','rb'))

color_map2=[(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255),(128,0,128),(0,0,128),(0,128,128),(0,255,127),(218,112,214),(255,20,147),(245,222,179),(255,228,181)]





#df = pd.read_excel(os.path.join('.\dataset', "hospital.xlsx"),engine='openpyxl',index_col=False)
df=pd.read_csv(open(os.path.dirname(__file__) + '/dataset/hospital.csv'))

oxy_df=pd.read_csv(open(os.path.dirname(__file__) + '/dataset/latlongs_oxy.csv'))


#######################################################
#data cleaning and removig outliers
remove_index=[4500,4653,4654,1734,2285] #these are manually calculated outliers for rajasthan and karnataka
df = df.drop(remove_index, axis=0)

df_cleaned = df[df['LONGITUDE']> 60]
df_final =df_cleaned[df_cleaned['LONGITUDE']<98]


#######################################################
def getstate(state_name):
    
    global gdf_state
    gdf_state=df_final[df_final["State"]==state_name]

getstate("Karnataka")
#######################################################
def random_color():
    rgbl=[255,0,0]
    random.shuffle(rgbl)
    return tuple(rgbl)
#######################################################

def distance(lat1, lat2, lon1, lon2):
     

    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    r = 6371
      

    return(c * r)


Distance=[]
List1=[]

for i in range(len(gdf_state)):
    for j in range(len(oxy_df)):
        List1.append(distance(gdf_state.iloc[i,11],oxy_df.iloc[j,1],gdf_state.iloc[i,12],oxy_df.iloc[j,2]))
    Distance.append(List1)
    List1=[]
    
hosp_remlist=[]
for i in range(len(gdf_state)):
    hosp_remlist.append(min(Distance[i]))
  
hosp_to_be_rem=[]
c=0
for i in range(len(hosp_remlist)):
    if hosp_remlist[i] < 2:
        hosp_to_be_rem.append(i+1709)  

gdf_for_clustering = gdf_state.drop(hosp_to_be_rem, axis=0)

#######################################################
km = KMeans(n_clusters=clu_num, init="k-means++",n_init=10, max_iter=350,tol=1e-04, random_state=0)
y_km = km.fit(gdf_state[['LATITUDE','LONGITUDE']])

centroid_list=[]
for u in range(len(y_km.cluster_centers_)):
    centroid_list.append(tuple(y_km.cluster_centers_[u]))
#######################################################


#the list of centroids is appended in this list

gdf_state["Clusters"]= y_km.labels_    #new column is being created


#######################################################
cluster_colors=[] #colors of clusters are appended in this list and new column is created
#based on the clusters colors are being assigned
for k in range(len(gdf_state)):
    for m in range(clu_num):
        if gdf_state.iloc[k,13] ==m :
            cluster_colors.append(random_color())


gdf_state["cluster_colors"]=cluster_colors #new column is created with colors for easy accessbilty

#######################################################
#reverse geocoding 



Centroid_Longs=y_km.cluster_centers_[:,1] #splitting centroids coords into lats and longs
Centroid_Lats=y_km.cluster_centers_[:,0]



headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}

def decode(lati,longi):
  urli="https://maps.googleapis.com/maps/api/geocode/json?latlng="+str(lati)+","+str(longi)+"&key="+apikey
  response= requests.get(urli,headers=headers)
  return response.json()["results"][1]["formatted_address"]


 # Address list for Centroids

 #decode is not called as the addresses are dumped in pickle file
for k in range(clu_num):
  centroid_address.append(decode(Centroid_Lats[k],Centroid_Longs[k])) #function call for geocoding
  #centroid_address.append(random.randint(0,100),random.randint(0,100))
#######################################################

#pickle.dump(centroid_address,open("centroid_address.dat","wb"))
     


#######################################################



#gmaps part
gmaps.configure(api_key="AIzaSyC4KrjejjTOAO_61zp7kSHfapldfDZq6go")

figure_layout = {
    'width': '600px',
    'height': '600px',
}
figure_layout2 = {
    'width': '600px',
    'height': '600px',
}

cluster_df_list=[] #grouping the clusters so that they can be added to a layer
for m in range(clu_num):
  cluster_df_list.append(gdf_state[gdf_state['Clusters'] == m])


#######################################################
#Layer 1
#layers for map-hospital layer
layers_list=[]
for k in range(clu_num):
    rndmcol=random_color()
    layers_list.append(gmaps.symbol_layer(cluster_df_list[k].iloc[:,11:13],fill_color=color_map2[k],stroke_color=color_map2[k],scale=2))

#Layer 2
#Suggested Hospital Layer
Suggested_plants_layer=gmaps.marker_layer(centroid_list,info_box_content=centroid_address)  


#Layer 3
#Existing_plants_layer=gmaps.marker_layer(oxy_df[["Latitude","Longitude"]])  
Existing_plants_layer=gmaps.symbol_layer(oxy_df[["Latitude","Longitude"]],fill_color="rgb(0,0,0)",stroke_color="rgb(0,0,0)",scale=3,info_box_content=oxy_df["Address of Plants"])



#######################################################

#Adding Layers
@app.route("/map/<lats>/<longs>")
def Config_Map(lats,longs):
  Map_cent=(lats,longs)
  fig_final=gmaps.figure(center=Map_cent,layout=figure_layout,zoom_level=7)
  
  for r in range(clu_num):
    fig_final.add_layer(layers_list[r])
    
  fig_final.add_layer(Suggested_plants_layer)

  fig_final.add_layer(Existing_plants_layer)

  embed_minimal_html('templates/map.html', views=[fig_final])

  return render_template("map.html")
#######################################################

@app.route("/map_oxy/<lats>/<longs>")
def Config_Oxy_map(lats,longs):
  Map_cent2=(lats,longs)
  fig_final2=gmaps.figure(center=Map_cent2,layout=figure_layout2,zoom_level=7) 
  fig_final2.add_layer(Existing_plants_layer)

  embed_minimal_html('templates/map_oxy.html', views=[fig_final2])

  return render_template("map_oxy.html")

#######################################################



if __name__ == '__main__':
    app.debug = True
    app.run() 