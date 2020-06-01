# Comercialización Interna de Granos

Cada año, en la Argentina circulan aproximadamente 120 millones de toneladas de granos. No obstante, pese a la preponderancia del sector dentro de la economía argentina, existe un desconocimiento del comportamiento de la comercialización interna de los granos.

## Objetivo

El presente proyecto tiene como objetivo dar una solución superadora y moderna mediante la generación de una herramienta que permita visualizar y analizar el comportamiento histórico de la comercialización interna de granos desde comienzos del 2015 hasta el último día del 2019.

### Pasos a seguir

* Preprocesamiento de datos
* Análisis exploratorio de datos
* Visualización geográfica de los flujos de comercialización

## Datos

* Base de datos [SIO-GRANOS](https://www.siogranos.com.ar/Consulta_publica/operaciones_informadas_exportar.aspx): Contiene todos los registros de compra-venta de cada grano según su localidad de origen y destino final.
* Zonificación del destino de entrega de granos [SIO-GRANOS](https://www.siogranos.com.ar/Consulta_publica/consulta_localidad_zona.aspx) .
* Base de datos de producción del [Ministerio de Agroindustria de la Nación](http://datosestimaciones.magyp.gob.ar/reportes.php?reporte=Estimaciones).
* Shapes files de localidades y provincias de Argentina, fuente [Datos Gobierno](https://datos.gob.ar/dataset/ign-unidades-territoriales/archivo/ign_01.02.02).

## Hipótesis
* Las zonas más alejadas a los puertos tienen una mayor comercialización hacia zonas aledañas, debido al mayor costo de transporte.
* Los flujos comerciales varían según el tipo de grano, debido a la estacionalidad de su cosecha.
* En zonas con problemas climáticos, se aumenta la comercialización hacia destinos finales (sin pasar por acopios), porque los productores tienen mayor poder de negociación.
* Las campañas que se encuentran atravesadas por elecciones presidenciales tienen una mayor dilatación de la comercialización, producto de las expectativas sobre posibles cambios en las políticas agrícolas.

## Scripts en python

* prepro.py:
```
Realiza el preprocesamiento de los datos de SIO-GRANOS y de producción.
Devuelve un csv listo para usar en ./Data/Output/data.csv
Campos:
* Provincia: Provincia de origen.
* Cultivo: Tipo de cultivo, opciones Maíz, Soja o Trigo.
* LugarEntrega: Zona de entrega según SIO-GRANOS.
* Mes: Mes del flujo de comercialización.
* Ano: Año del flujo de comercialización.
* CantTns: Cantidad de granos comercializada en toneladas.
* EsFinal: Boolean que indica si es destino final o no.
* EleccionesNac: Boolean que indica si en el año hubo elecciones nacionales.
* EleccionesPre: Boolean que indica si en el año hubo elecciones presidenciales.
* ProdTns: Cantidad de granos producida en toneladas.
* EstresClimatico: Boolean que indica si hubo una pérdida de área superior al 20%.
* MismaProvDestino: Boolean que indica si la zona de entrega incluye la provincia de origen.

```

* EDA.py:
```
Próximamente.
Toma el csv preprocesado y realiza un análisis exploratorio de datos.
```

* DataVis.py:
```
Próximamente.
Toma el csv preprocesado y realiza la visualización geográfica de los flujos de comercialización interna de granos.
```

## Autor

**Juan Pablo Gianatiempo** - [jpgianatiempo](https://github.com/jpgianatiempo)



