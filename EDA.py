#datos del destino de entrega
#https://www.siogranos.com.ar/Consulta_publica/consulta_localidad_zona.aspx


Sio2019.columns.tolist()
Sio2019.dtypes
Sio2019.shape
Sio2019.head(5)

#Saco outliers por quantiles min y max
q_low = Sio2019["CantTns"].quantile(0.01)
q_hi  = Sio2019["CantTns"].quantile(0.99)
Sio2019 = Sio2019[(Sio2019["CantTns"] < q_hi) & (Sio2019["CantTns"] > q_low)]
