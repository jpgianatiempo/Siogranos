import geopandas as gpd
from shapely.geometry import Polygon
import shapely
import pandas as pd
import os
import json
import numpy as np

if os.path.isfile("./Data/Output/MapFlowData.csv"):
    data = pd.read_csv("./Data/Output/MapFlowData.csv",sep=',',encoding='utf-8',index_col=0)
    print("dale, que va")
else:
    print("Fijate si esta actualizado el git")

#cambiar Cutlivo soja, trigo (replace, inplace=true)
data["Cultivo"].replace("Soja total", "Soja",inplace=True)
data["Cultivo"].replace("Trigo total", "Trigo",inplace=True)
#agrupar por años
data2 = data.groupby(["Provincia","Cultivo","LugarEntrega",'Ano','ProvCentroidLat','ProvCentroidLon','ZonaCentroidLat','ZonaCentroidLon']).agg({'CantTns':'sum'}).reset_index()

#genero Values con ciertas columnas
Values = data2[['Cultivo',"Ano",'Provincia',"LugarEntrega","CantTns"]]
#Renombro columnas
Values.rename(columns={'Ano':'Año',
                       "Provincia":"Origen",
                       "LugarEntrega":"Destino",
                       "CantTns": "Cantidad Transportada (MTn)"}, 
                 inplace=True)

Values["Cantidad Transportada (MTn)"] = Values["Cantidad Transportada (MTn)"]/1000000
Values['Año'] = Values['Año'].astype('int')

Values.to_csv('./Data/Output/Values.csv', encoding='utf-8')

 
#Location
#pensaba hacer dos group by segun uno provinica
LocationA = data2.groupby(["Provincia"]).agg({'ProvCentroidLat':'mean', 'ProvCentroidLon':'mean'}).reset_index()
LocationA.rename(columns={'Provincia':'Location Name',
                       "ProvCentroidLat":"Longitude",
                       "ProvCentroidLon":"Latitude"}, 
                 inplace=True)
LocationA = pd.DataFrame(LocationA)
LocationB = data2.groupby(["LugarEntrega"]).agg({'ZonaCentroidLat':'mean', 'ZonaCentroidLon':'mean'}).reset_index()
LocationB.rename(columns={'LugarEntrega':'Location Name',
                       "ZonaCentroidLat":"Longitude",
                       "ZonaCentroidLon":"Latitude"}, 
                 inplace=True)
LocationB = pd.DataFrame(LocationB)
#agrupo los dos
Location = pd.concat([LocationA,LocationB])
Location["Location Code"] = Location["Location Name"]
del LocationA, LocationB

Location.to_csv('./Data/Output/Locations.csv', encoding='utf-8')



######################################
######## ARMAR DATOS PARA SANKEY #####
######################################
data3 = data.groupby(["Provincia","Cultivo","EsFinal","LugarEntrega"]).agg({'CantTns':'sum'}).reset_index()

#Loop generador de Cultivo/EsFinal
for l in data3.Cultivo.unique():
    for i in data3.EsFinal.unique():
        globals()[l+str(i)] = data3.loc[(data3.Cultivo == l) & (data3.EsFinal == i)]
        #agrego columnas
        if i:
            globals()[l+str(i)]["Step From"] = 0
            globals()[l+str(i)]["Step To"] = 2
        else:
            globals()[l+str(i)]["Step From"] = 0
            globals()[l+str(i)]["Step To"] = 1

#TOMO LOS FALSE Y CAMBIO LOS NOMBRES DE LAS COLUMNAS
SojaInt = SojaFalse.copy()
SojaInt["Provincia"] = SojaInt["LugarEntrega"]
SojaInt["Step From"] = 1
SojaInt["Step To"] = 2

#agrupo los dos
Soja = pd.concat([SojaFalse,SojaTrue,SojaInt])
Maiz = pd.concat([MaizFalse,MaizTrue])
Trigo = pd.concat([TrigoFalse,TrigoTrue])

#del TrigoFalse,TrigoTrue,SojaFalse,SojaTrue,MaizFalse,MaizTrue

#No me gustó
Soja.to_csv('./Data/Output/SojaMSS.csv', encoding='utf-8')

#####################################
####### MULTI STEP SANKEY 2.0 #######
#####################################

#SANKEY NORMAL FROM VALUES
Values["Step From"] = 0
Values["Step To"] = 1
data4 = Values.groupby(["Cultivo","Destino"]).agg({'Cantidad Transportada (MTn)':'sum'}).reset_index()

#ordenar las columns
data4["Step From"] = 1
data4["Step To"] = 2

#destino a origen, cultivo a destino, año 2020
data4["Origen"] = data4["Destino"]
data4["Destino"] = data4["Cultivo"]
data4["Año"] = 2020
#concat
MSSankey = pd.concat([Values,data4])

MSSankey.to_csv('./Data/Output/MSSankey.csv', encoding='utf-8')


