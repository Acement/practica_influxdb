# practica_influxdb

## Descripción

Programa que simula el tránsito de personas dentro un mall a lo largo del día, la salida de las personas va a depender de la temperatura que haya fuera del mall.

Estos datos serán subidos a influxdb para que luego otro programa python los descargue y genere métricas con estos datos, las cuales se usarán para generar gráficos.

El programa consta de dos partes:

* Generación y simulación: 
	- gen_person.py: Llama a la generación de temperaturas y luego las usa para simular el tránsito de personas.
	- gen_temp.py: Genera las temperaturas para ser usadas en la simulación y las guarda en temperature.json.

* Procesamiento de datos:
	- data_process.py: Hace las consultas a influxdb y genera métricas y gráficos.

## Requerimientos

* Ubuntu 24.04.1 o superior
* Influxdb 2.7.11 o superior
* Python 3.12.3 o superior
* Librerías de python: 
  - venv
  - influxdb-client 1.48.0 o superior
  - matplotlib 3.10.0 o superior
  - numpy 2.2.0 o superior
  - psutil 6.1.1 o superior

Para instalar influxdb visite: https://www.influxdata.com/downloads/

## Instalación

En la carpeta donde se desea guardar el programa, abrir la terminal y ejecutar el siguiente comando git:

```cmd 
git clone https://github.com/Acement/practica_influxdb
```

Luego de clonar el repositorio, mover la terminal a la carpeta usando el siguiente comando:

```cmd 
cd practica_influxdb
```

Después Setear las variables de entorno dentro del archivo .env:

```cmd 
INFLUXDB_TOKEN=<Token generado por influxdb>
```

## Configuración

La configuración del programa se encuentra dentro de  config.json, que está separado en 3 partes:

* gen_config: La configuración de la generación de datos.

| Argumento | Descripcion |
| -------- | ----------- |
| cant_clientes | Cantidad de clientes que se van a crear para la simulación. |
| hora_apertura | Hora en la que se abre el mall. |
| hora_cierre | Hora en la que se cierra el mall. |
| temp_max | Temperatura máxima que puede haber fuera del mall. |
| temp_min | Temperatura mínima que puede haber fuera del mall. |
| nombres | Nombres con los que se generarán las personas. |
| apellidos | Apellidos con los que se generara las personas. |
| edificio | (*)Se explicará luego. |
| temperatura | Temperatura en la comienza la simulación. |
| temp_cambio | Controla el cambio de la temperatura, dependiendo del valor la temperatura subirá, bajará o se mantendrá. |
| utc_zone |  Zona horaria en formato UTC. |

(*)edificio: El edificio donde se hará la simulación se separa en las siguientes valores:

| Argumento | Descripcion |
| -------- | ----------- |
| nombre_piso | Nombre del piso con las tiendas. |
| id | Identificación del piso. |
| tiendas | Lista con las tiendas que se ubican en piso. |

  
* idb_config: La configuración de influxdb.

| Argumento | Descripcion |
| -------- | ----------- |
| org | Organización creada en influxdb. |
| url | URL donde se accede a influxdb, en este caso se usa http://localhost:8086. |
| bucket | Bucket creado en influxdb donde se guarda y sacan las mediciones. |

  
* fecha_config: La configuración de la fecha donde se va a guardar.


| Argumento | Descripcion |
| -------- | ----------- |
| año | Año con el cual se guardarán las mediciones. |
| mes | Mes con el cual se guardarán las mediciones. |
| dia | Dia con el cual se guardarán las mediciones. |


## Ejecución

Para generar los datos tienes que ejecutar:

```cmd 
python3 gen_person.py
```

lo cual ejecutará la generación de la temperatura y la simulación y lo subirá a influxdb. Esto es necesario hacerlo antes de ejecutar data_process.py

Para la generacion de graficos primero tenemos que ejecutar:

```cmd 
python3 data_process.py
```
Lo cual abrirá el programa que mostrará un menú con las siguientes opciones:

### 1.- Tiempo promedio por persona en mall:

Muestra el tiempo que cada persona estuvo en el mall, también genera un gráfico que muestra cuántas personas se quedaron x cantidad de tiempo.

El gráfico se guarda en: graph/tiempoEstadia.png

### 2.-Cantidad de personas por hora:

Muestra la cantidad de personas que estuvieron en el mall por hora, con lo cual genera un gráfico que muestra dicha métrica.

El gráfico se guarda en: graph/PersonasPorHora.png

### 3.-Ventas totales por tiendas:

Muestra las ventas totales por tienda que se hicieron a lo largo del día, también genera un gráfico con estos datos.

El gráfico se guarda en: graph/VentasTotales.png

### 4.- Ventas totales por hora:

Muestra la suma de las ventas de todas las tiendas que se hicieron por hora, también genera un gráfico con estos datos.

El gráfico se guarda en: graph/VentasPorHora.png

### 5.- Ventas por hora por tienda:

Junta las dos métricas anteriores, generando un gráfico que muestra las ventas de las tiendas individualmente por hora, y genera una serie de gráficos que muestra las ventas por hora

Los gráficos se guardan en: graph/ventasPTPH

### 6.- Personas por tiendas por minuto

Muestra la cantidad de gente que hubieron por tienda por minuto, con lo cual se generan una serie de gráfico que muestra el total de personas que hubieron por minuto y los separa por hora

Los gráficos se guardan en: graph/personasPMs


## Funciones

Generación de datos: El programa es capaz de generar la temperatura y las personas para poder realizar la simulación.

Simulador de agente: El programa es capaz de simular la entrada y salida de personas a un mall, para poder ver como la temperatura afecta a la estadía.

Subida y bajada de datos: el programa es capaz de subir y bajar datos desde la base de datos creada en influxdb

Generación de métricas: El programa es capaz de generar métricas usando los datos sacados de influxdb.

Generación de gráficos: El programa es capaz de generar gráficos a partir de las métricas.


