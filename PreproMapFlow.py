#%%
import geopandas as gpd
from shapely.geometry import Polygon
import shapely
import pandas as pd
import os
import json
import numpy as np

if os.path.isfile("./Data/Output/data.csv"):
    data = pd.read_csv("./Data/Output/data.csv",sep=',',encoding='utf-8',index_col=0)
    data['Mes'] = data['Mes'].astype('category')
    data['Ano'] = data['Ano'].astype('category')
    print("Puede continuar con EDA.py")
else:
    print("Correr prepro.py para obtener los datos preprocesados")

##########################
## CENTROIDE PROVINCIAS ##
##########################
#Poligonos
#cargo el shape de provincia
lga_df = gpd.read_file("./Data/Shapes/provincia.shp")
#calculo el centroide
lga_df["centroid"] = lga_df["geometry"].centroid


#Genero campo Año con los ultimos números de la campaña
lga_df['centroid'] = lga_df['centroid'].astype('str')
nuevo = lga_df['centroid'].str.strip('()')                               \
                   .str.strip("POINT")                                   \
                   .str.strip("(")                                   \
                   .str.split(' ', expand=True)


lga_df["ProvCentroidLat"]= nuevo[1].str.strip("(")
lga_df["ProvCentroidLon"]= nuevo[2]
del nuevo
#cambio el nombre de la columna geometry
lga_df.rename(columns={'geometry':'ProvGeometry',
                       "nam": "Provincia"}, 
                 inplace=True)

#Cambiar los nombres de provincia a data
Modificar = {"BUENOS AIRES":"Buenos Aires",
             "CATAMARCA":"Catamarca",
             "CHACO":"Chaco",
             "CHUBUT":"Chubut",
             "CIUDAD AUTONOMA DE BUENOS AIRES":"Ciudad Autónoma de Buenos Aires",
             "CORDOBA":"Córdoba",
             "CORRIENTES":"Corrientes",
             "ENTRE RIOS":"Entre Ríos",
             "FORMOSA":"Formosa",
             "JUJUY":"Jujuy",
             "LA PAMPA":"La Pampa",
             "LA RIOJA":"La Rioja",
             "MENDOZA":"Mendoza",
             "MISIONES":"Misiones",
             "NEUQUEN":"Neuquén",
             "RIO NEGRO":"Río Negro",
             "SALTA":"Salta",
             "SAN JUAN":"San Juan",
             "SAN LUIS":"San Luis",
             "SANTA CRUZ":"Santa Cruz",
             "SANTA FE":"Santa Fe",
             "SANTIAGO DEL ESTERO":"Santiago del Estero",
             "TIERRA DEL FUEGO":"Tierra del Fuego, Antártida e Islas del Atlántico Sur",
             "TUCUMAN":"Tucumán"}
data["Provincia"] = data['Provincia'].map(Modificar).fillna(data['Provincia'])
#remuevo las columnas que no me sirven
lga_df = lga_df[['Provincia','ProvGeometry',"ProvCentroidLat","ProvCentroidLon"]]
#join en (Provincia) y pasar ProvGeometry, ProvCentroidLat, ProvCentroidLon
data = pd.merge(data, lga_df,how='left', on=['Provincia'])



###########################
#### ZONAS DE DESTINO #####
###########################
#Cargo shape de zona de destino
zonas = gpd.read_file("./Data/Shapes/ZonasSiogranos.shp",encoding='utf-8')
#Modifico datos
#En data Zona 26 a Resto del País
data["LugarEntrega"].replace("Zona 26", "Resto del País",inplace=True)
#En zonas:
Modificar = {"Zona 19":"B.Blanca",
             "Zona 21":"Bs As",
             "Zona 22":"Cordoba",
             "Zona 20":"Quequen",
             "Zona 23":"Rosario N",
             "Zona 24":"Rosario S"}
zonas["nam"] = zonas['nam'].map(Modificar).fillna(zonas['nam'])
#cambio el nombre de la columna geometry
zonas.rename(columns={'geometry':'ZonaGeometry',
                       "nam": "LugarEntrega"}, 
                 inplace=True)

#calculo centroides
zonas = gpd.GeoDataFrame(zonas, geometry='ZonaGeometry')
zonas["centroid"] = zonas["ZonaGeometry"].centroid

#separo lat y lon de los centroides
zonas['centroid'] = zonas['centroid'].astype('str')
nuevo = zonas['centroid'].str.strip('()')                               \
                   .str.strip("POINT")                                   \
                   .str.strip("(")                                   \
                   .str.split(' ', expand=True)

#los agrego como columnas
zonas["ZonaCentroidLat"]= nuevo[1].str.strip("(")
zonas["ZonaCentroidLon"]= nuevo[2]
del nuevo

#elimino columnas extra
zonas = zonas[['LugarEntrega','ZonaGeometry',"ZonaCentroidLat","ZonaCentroidLon"]]
#Leftjoin con data en LugarEntrega pasar ProvGeometry, ProvCentroidLat, ProvCentroidLon
data = pd.merge(data, zonas,how='left', on=['LugarEntrega'])

#Elimino columnas no utilizadas
data = data[['Provincia',
 'Cultivo',
 'LugarEntrega',
 'Mes',
 'Ano',
 'CantTns',
 'EsFinal',
 'ProvCentroidLat',
 'ProvCentroidLon',
 'ZonaCentroidLat',
 'ZonaCentroidLon']]

#Agrupo y sumarizo cantidad por año
#data = data.groupby(["Provincia","Cultivo","LugarEntrega",'Ano','EsFinal','ProvCentroidLat','ProvCentroidLon','ZonaCentroidLat','ZonaCentroidLon']).agg({'CantTns':'sum'}).reset_index()

#Guardo en output el csv para mapflow powerbi
data.to_csv('./Data/Output/MapFlowData.csv', encoding='utf-8')


#Guardo en output el Json para mapflow powerbi
#with open('./Data/Output/MapFlowData.json', 'w', encoding='utf-8') as file:
#    data.to_json(file, force_ascii=False,default_handler=str)

"""
#Cargo shape de departamentos
depto_df = gpd.read_file("./Data/Shapes/departamento.shp")
depto_df.head(5)

#muni_df = gpd.read_file("./Data/Shapes/municipio.shp")
#muni_df.head(5)

####################################
## ASIGNAR PROVINCIA A CADA DEPTO ##
####################################

#me genero una lista con el nombre prov y poligono
prov = lga_df[["Provincia","ProvGeometry"]]
prov = gpd.GeoDataFrame(prov, geometry='ProvGeometry')
prov.set_index('Provincia', inplace=True)

#genero lista con nombre de provicias a los que pertenece cada depto
#INVERTIR EL LOOP
a = []
for ind in prov.index:
    for indi in depto_df.index:
        if prov['ProvGeometry'][ind].contains(depto_df['geometry'][indi]):
            a.append(str(indi)+"."+ind)
            #print(ind,"contiene",depto_df["nam"][indi])

#spliteo a
indice = [i.split('.', 1)[0] for i in a]
Provincia = [i.split('.', 1)[1] for i in a]
#genero diccionario
zipbObj = zip(indice, Provincia)
DictProv = dict(zipbObj)
#covierto las keys a int
DictProv = {int(k):v for k,v in DictProv.items()}
#genero la columna provincia en base a los keys del dict
depto_df["Provincia"] = depto_df.index.map(DictProv)

#VER LOS NULOS ?¿?¿??
len(depto_df[depto_df.Provincia.isnull()])


#Paso a mayúsculas y saco los ascentos

#Tomar los poligonos deptos, evaluar si estan dentro del poligono de provincia
#si estan dentro les asigno el nombre de la provincia

#Join con Zonas

#Junto los shapes 



"""


"""
¿¿¿???¿?AGRUPAR¿???¿?¿? VER QUE ONDA MAPFLOW POWERBI
b = data.groupby(['Provincia']).agg({"CantTns":'sum'})
b = b.sort_values('CantTns',ascending=False)
b.reset_index(level=0, inplace=True)
"""


# %%
