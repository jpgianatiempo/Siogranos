#%%
import pandas as pd
import numpy as np
import os
import glob

#%%
#Cargo archivo de producción de http://datosestimaciones.magyp.gob.ar/
prod = pd.read_csv("./Data/Produccion/Estimaciones.csv",sep=';',encoding='latin-1')


#%%

#Cargo datos de SIOGRANOS https://www.siogranos.com.ar/Consulta_publica/operaciones_informadas_exportar.aspx
#La descarga de datos solo habilita cada 90 días
#un csv por trimestrales desde el 2015 al 2019
path = r'./Data/Siogranos' 
all_files = glob.glob(path + "/*.csv")
li = []

#UTF-16 LE
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, sep=";",encoding='UTF-8', header=0,error_bad_lines=False,warn_bad_lines=True)
    li.append(df)

Sio2019 = pd.concat(li, axis=0, ignore_index=True)

Sio2019.to_csv('./Data/Output/FullSiogranos.csv', encoding='utf-8')

del all_files, li, path

# %%
"""
#Cargo datos de SIOGRANOS https://www.siogranos.com.ar/Consulta_publica/operaciones_informadas_exportar.aspx
#La descarga de datos solo habilita cada 180 días
#Tomo los datos del 2019
Sio20193 = pd.read_csv("./Data/Siogranos/20193TRIM.csv",sep=";",encoding='UTF-16 LE')
Sio20194 = pd.read_csv("./Data/Siogranos/20194TRIM.csv",sep=";",encoding='UTF-16 LE')
Sio20191 = pd.read_csv("./Data/Siogranos/20191TRIM.csv",sep=";",encoding='UTF-16 LE')
Sio20192 = pd.read_csv("./Data/Siogranos/20192TRIM.csv",sep=";",encoding='UTF-16 LE')

frames = [Sio20191, Sio20192, Sio20193, Sio20194]

Sio2019 = pd.concat(frames)

del [Sio20191, Sio20192, Sio20193, Sio20194]
"""

#%% 
# Producción
#Filtros, nuevas columnas, select

#De produccion tengo que seleccionar campañas
#prod = prod.loc[prod.Campana.isin(["2013/14","2014/15","2015/16","2016/17","2017/18","2018/19","2019/20"])]
#seleccionar granos
#no separo entre trigo candeal y pan | (prod.Cultivo == 'Trigo candeal')
prod = prod.loc[(prod.Cultivo == 'Maíz') | (prod.Cultivo == 'Soja total') | (prod.Cultivo == 'Trigo total')]
#de la cada campaña sacarle 20
prod['Campana'] = prod['Campana'].map(lambda x: x.lstrip('20'))
#seleccionar columnas a usar
prod = prod[['Provincia',"Cultivo","Campana","Sup. Sembrada (Ha)","Sup. Cosechada (Ha)","Producción (Tn)"]]
#agrupo por provincia, cultivo, campana y sum "Sup. Sembrada (Ha)","Sup. Cosechada (Ha)","Producción (Tn)"
prod = prod.groupby(['Provincia',"Cultivo","Campana"]).agg({"Sup. Sembrada (Ha)":'sum',"Sup. Cosechada (Ha)":'sum',"Producción (Tn)":'sum'}).reset_index()
#genero columna area perdida
prod['Sup. Perdida (Ha)'] = prod["Sup. Sembrada (Ha)"] - prod["Sup. Cosechada (Ha)"]
#genero columna % area perdida/area sembrada
prod["Porc. Sup. Perdida"] = prod['Sup. Perdida (Ha)']/prod["Sup. Sembrada (Ha)"]*100
#Defino problemas climaticos como % > 20
prod["Estres Climatico"] = np.where((prod["Porc. Sup. Perdida"] >= 20), True, False)
#Veo si hay nulos
if prod.shape == pd.notnull(prod).shape:
    print("no hay nulos")
else:
    print("hay nulos, dropeo las filas con NA")
    prod.dropna(inplace = True) 
#Creo campo año con los ultimos /de la campaña
nuevo = prod['Campana'].str.split("/",expand = True)
prod["Ano"]= nuevo[1]
del nuevo
#le agrego 20 adelante 
prod['Ano'] = "20" + prod['Ano']
#Renombro columnas: estres climatico y produccion
prod = prod.rename(columns={'Producción (Tn)': 'ProdTns', 'Estres Climatico': 'EstresClimatico'})
#re-start index
prod = prod.reset_index(drop = True)
#cambio de tipos
prod = prod.astype({"Provincia": str, "Cultivo": str, "Campana": str, "Ano": int})
#saco las columnas que no voy a usar
del prod['Campana'],prod['Sup. Sembrada (Ha)'],prod['Sup. Cosechada (Ha)'],prod['Sup. Perdida (Ha)'],prod['Porc. Sup. Perdida']


#%%
# SIOGRANOS
#juntar trigo (cambiar los dos datos)
Sio2019.loc[Sio2019.PRODUCTO == 'TRIGO CAND.', 'PRODUCTO'] = "Trigo total"
Sio2019.loc[Sio2019.PRODUCTO == 'TRIGO PAN', 'PRODUCTO'] = "Trigo total"
Sio2019.loc[Sio2019.PRODUCTO == 'MAIZ', 'PRODUCTO'] = "Maíz"
Sio2019.loc[Sio2019.PRODUCTO == 'SOJA', 'PRODUCTO'] = "Soja total"
#Renombro columna y filtro Producto = Cultivo
Sio2019 = Sio2019.rename(columns={'PRODUCTO': 'Cultivo'})
Sio2019 = Sio2019.loc[(Sio2019.Cultivo == 'Maíz') | (Sio2019.Cultivo == 'Soja total') | (Sio2019.Cultivo == 'Trigo total')]
#filtro tipo = Compraventa
Sio2019 = Sio2019.loc[(Sio2019.TIPO == "Compraventa")]
#filtro Operacion = contrato, anulacion, ampliacion
Sio2019 = Sio2019.loc[Sio2019.OPERACION.isin(["Contrato","Ampliación","Anulación"])]
"""
#Renombro columna y saco palabra cosecha
Sio2019 = Sio2019.rename(columns={'COSECHA': 'Campana'})
Sio2019['Campana'] = Sio2019['Campana'].map(lambda x: x.lstrip('COSECHA '))
#modificar valores de Campana segun lista
Modificar = {"2019":"18/19","2018":"17/18","2020":"19/20","2017":"16/17","2016":"15/16","2021":"20/21","2015":"14/15","2014":"13/14","2013":"12/13","2012":"11/12","2011":"10/11","2010":"09/10"}
#Sio2019.replace({"Campana": Modificar})
Sio2019["Campana"] = Sio2019['Campana'].map(Modificar).fillna(Sio2019['Campana'])
"""
#renombrar columnas importantes para el join
Sio2019 = Sio2019.rename(columns={'COSECHA': 'Campana','PROCEDENCIA PCIA': 'Provincia', "PROCEDENCIA LOCALID.": "Departamento"})
#Generar columna Mes y Ano
#Asigno al mayor mes de ambos y el año del 'FECHA ENTR. DESDE'
fecha1 = Sio2019['FECHA ENTR. DESDE'].str.split("/",expand = True)
fecha2 = Sio2019['FECHA ENTR. HASTA'].str.split("/",expand = True)
Sio2019["Mes"]= pd.concat([fecha1[1], fecha2[1]], axis=1).max(axis=1)
ano = fecha1[2].str.split(" ",expand=True)
Sio2019["Ano"]= ano[0]
del fecha1, fecha2, ano

#Modifico "LUGAR ENTREGA" (omito origen y destino, ya que esta la zona y si es final)
entrega = Sio2019['LUGAR ENTREGA'].str.split("/",expand = True)
Sio2019["LUGAR ENTREGA"]= entrega[0]
del entrega
#Seleccionar columnas deseadas
Sio2019 = Sio2019[["OPERACION",'Provincia','Departamento',"Cultivo","Campana",'CANT. (TN)','LUGAR ENTREGA','ES FINAL','Mes','Ano']]
#Dropeo nulos
Sio2019.dropna(inplace = True)
# Reemplazo "CANT. (TN)" , por .
Sio2019["CANT. (TN)"] = Sio2019["CANT. (TN)"].str.replace(",",".")
#Reemplazo ES FINAL -- SI por True y NO por False
Sio2019["ES FINAL"] = Sio2019["ES FINAL"].replace({'SI': True, 'NO': False})
#Cambio de tipo de datos
Sio2019 = Sio2019.astype({"OPERACION": str,"Provincia": str, "Departamento": str, "Cultivo": str, "Campana": str, "CANT. (TN)": float, "LUGAR ENTREGA": str, "ES FINAL": bool, "Mes": int, "Ano": int})
#Renombro columnas
Sio2019 = Sio2019.rename(columns={'OPERACION': 'Operacion', "CANT. (TN)": "CantTn", "LUGAR ENTREGA": "LugarEntrega", "ES FINAL": "EsFinal"})
#Remuevo acentos
Sio2019['Provincia'] = Sio2019['Provincia'].str.normalize('NFKD')\
                       .str.encode('ascii', errors='ignore')\
                       .str.decode('utf-8')
#¿Particionar data en 2: es final y no es final
Sio2019Final = Sio2019.loc[Sio2019.EsFinal == True]
Sio2019NoFinal = Sio2019.loc[Sio2019.EsFinal == False]
#Mensualizar las variables
#group by + agg python 
Sio2019Final = Sio2019Final.groupby(["Operacion","Provincia","Cultivo","LugarEntrega",'Mes','Ano']).agg({'CantTn':'sum'}).reset_index()
Sio2019NoFinal = Sio2019NoFinal.groupby(["Operacion","Provincia","Cultivo","LugarEntrega",'Mes','Ano']).agg({'CantTn':'sum'}).reset_index()

#TOMAR "OPERACION" CONTRATO, SUMAR AMPLIACION Y RESTAR ANULACION
    #Datos de destino final
FinalAnul = Sio2019Final.loc[Sio2019Final.Operacion == "Anulación"]
FinalAnul = FinalAnul.iloc[:,1:]
FinalCont = Sio2019Final.loc[Sio2019Final.Operacion == "Contrato"]
FinalCont = FinalCont.iloc[:,1:]
FinalAmp = Sio2019Final.loc[Sio2019Final.Operacion == "Ampliación"]
FinalAmp = FinalAmp.iloc[:,1:]
#Merge
Sio2019Final = pd.merge(FinalCont, FinalAnul,how='outer', on=['Provincia', 'Cultivo', 'LugarEntrega', 'Mes', 'Ano'])
Sio2019Final = pd.merge(Sio2019Final, FinalAmp,how='outer', on=['Provincia', 'Cultivo', 'LugarEntrega', 'Mes', 'Ano'])
#REEMPLAZAR NaN por 0 en CantTn_x, CantTn_y, CantTn
Sio2019Final["CantTn_x"].fillna(0, inplace=True)
Sio2019Final["CantTn_y"].fillna(0, inplace=True)
Sio2019Final["CantTn"].fillna(0, inplace=True)
#Crear nueva columna cant Cont - cant Anul + cant Amp
Sio2019Final["CantTns"] = Sio2019Final["CantTn_x"] - Sio2019Final["CantTn_y"] + Sio2019Final["CantTn"]
#eliminar las columnas no deseadas
del Sio2019Final["CantTn_x"], Sio2019Final["CantTn_y"], Sio2019Final["CantTn"], FinalAmp, FinalCont, FinalAnul
#VOLVER A HACER LOS GROUP BY 
Sio2019Final = Sio2019Final.groupby(["Provincia","Cultivo","LugarEntrega",'Mes','Ano']).agg({'CantTns':'sum'}).reset_index()

    #Datos destino no final
NoFinalAnul = Sio2019NoFinal.loc[Sio2019NoFinal.Operacion == "Anulación"]
NoFinalAnul = NoFinalAnul.iloc[:,1:]
NoFinalCont = Sio2019NoFinal.loc[Sio2019NoFinal.Operacion == "Contrato"]
NoFinalCont = NoFinalCont.iloc[:,1:]
NoFinalAmp = Sio2019NoFinal.loc[Sio2019NoFinal.Operacion == "Ampliación"]
NoFinalAmp = NoFinalAmp.iloc[:,1:]
#Merge
Sio2019NoFinal = pd.merge(NoFinalCont, NoFinalAnul,how='outer', on=['Provincia', 'Cultivo', 'LugarEntrega', 'Mes', 'Ano'])
Sio2019NoFinal = pd.merge(Sio2019NoFinal, NoFinalAmp,how='outer', on=['Provincia', 'Cultivo', 'LugarEntrega', 'Mes', 'Ano'])
#REEMPLAZAR NaN por 0 en CantTn_x, CantTn_y, CantTn
Sio2019NoFinal["CantTn_x"].fillna(0, inplace=True)
Sio2019NoFinal["CantTn_y"].fillna(0, inplace=True)
Sio2019NoFinal["CantTn"].fillna(0, inplace=True)
#Crear nueva columna cant Cont - cant Anul + cant Amp
Sio2019NoFinal["CantTns"] = Sio2019NoFinal["CantTn_x"] - Sio2019NoFinal["CantTn_y"] + Sio2019NoFinal["CantTn"]
#eliminar las columnas no deseadas
del Sio2019NoFinal["CantTn_x"], Sio2019NoFinal["CantTn_y"], Sio2019NoFinal["CantTn"], NoFinalAmp, NoFinalCont, NoFinalAnul
#VOLVER A HACER LOS GROUP BY 
Sio2019NoFinal = Sio2019NoFinal.groupby(["Provincia","Cultivo","LugarEntrega",'Mes','Ano']).agg({'CantTns':'sum'}).reset_index()

#Agregar columna EsFinal a ambos Final y NoFinal
Sio2019Final["EsFinal"] = True
Sio2019NoFinal["EsFinal"] = False
#JUNTAR SIO2019FINAL y SIO2019NOFINAL en Sio2019
Sio2019 = pd.concat([Sio2019Final, Sio2019NoFinal])
del Sio2019Final, Sio2019NoFinal
#Agregar columnas EleccionesNac y EleccionesPre
EleccionesNac = ["2015", "2017", "2019"]
EleccionesPre = ["2015","2019"]
Sio2019["EleccionesNac"] = Sio2019["Ano"].isin(EleccionesNac)
Sio2019["EleccionesPre"] = Sio2019["Ano"].isin(EleccionesPre)
del EleccionesNac, EleccionesPre

# sacar datos con CantTns <=0
Sio2019.drop(Sio2019[Sio2019.CantTns <= 0].index, inplace=True)


#%%
#Merge de ambos datos: Prod y Sio2019 en Sio2019
# Corrijo años
Modificar = {2105:2015, 2106:2016, 2107:2017, 2027:2017, 2026:2016, 2215:2015, 2108:2018, 2048:2018, 2051:2015, 2116:2016, 3017:2017}
Sio2019["Ano"] = Sio2019['Ano'].map(Modificar).fillna(Sio2019['Ano'])

#join por año, NO POR LA CAMPAÑA
Sio2019 = pd.merge(Sio2019, prod,how='left', on=['Provincia', 'Cultivo', 'Ano'])

"""
#Otro filtro de outliers es eliminar datos donde no hay prod
#filtro provincias sin produccion
Check = Sio2019.loc[Sio2019['EstresClimatico'].isnull()]
a = Check["Provincia"].unique()
b = np.intersect1d(Check["Provincia"], prod["Provincia"])
c = list(set(a) - set(b))

Sio2019 = Sio2019[~Sio2019['Provincia'].isin(c)]

del Check, a, b, c
"""

# Cambio los NaN por Falso en estresClimatico
Sio2019["EstresClimatico"].fillna(False, inplace=True)


"""
#OJO PARTE POLÉMICA
# Cambio los Nan por 0 en produccion
Sio2019["ProdTns"].fillna(0, inplace=True)
"""
#saco acento a maíz
Sio2019['Cultivo'] = Sio2019['Cultivo'].str.normalize('NFKD')\
                       .str.encode('ascii', errors='ignore')\
                       .str.decode('utf-8')
del prod

#%%
#Cargo datos del destino de entrega
#https://www.siogranos.com.ar/Consulta_publica/consulta_localidad_zona.aspx

zonas = pd.read_csv("./Data/Zonas/zonas.csv",sep=';',encoding='utf-8')

#Cambio los nombres de las columnas
# PROVINCIA por LugarEntregaProvincias 
# ZONA por 'LugarEntrega'
zonas = zonas.rename(columns={'PROVINCIA': 'LugarEntregaProvincias', "ZONA": "LugarEntrega"})

#Saco los de LugarEntregaProvincias
zonas['LugarEntregaProvincias'] = zonas['LugarEntregaProvincias'].str.normalize('NFKD')\
                       .str.encode('ascii', errors='ignore')\
                       .str.decode('utf-8')

#group by zona y sumo los strngs de provincia
zonas = zonas.groupby(["LugarEntrega"])['LugarEntregaProvincias'].unique()
zonas = zonas.to_frame()
zonas.reset_index(level=0, inplace=True)

#%%

#Join con data por LugarEntrega y paso todas las prov
data = pd.merge(Sio2019, zonas,how='left', on=['LugarEntrega'])

#Genero columna "DestinoMismaProv" TRUE/FALSE si Provincia isin LugarEntregaProvincia
def find_value_column(row):
    return row.Provincia in row.LugarEntregaProvincias

data["MismaProvDestino"] = data.apply(find_value_column, axis=1)

#Selecciono columnas deseadas
del data['LugarEntregaProvincias'], Sio2019

# Paso a categoria Mes y Año
data['Mes'] = data['Mes'].astype('category')
data['Ano'] = data['Ano'].astype('category')


#Genero csv en carpeta Output
data.to_csv('./Data/Output/data.csv', encoding='utf-8')





# %%
