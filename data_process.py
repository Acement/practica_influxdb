import os,json
import numpy as np
import influxdb_client as idb
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime

#Cargando JSON
with open("config.json") as f:
    data = json.load(f)
gen_data = data["gen_config"]
idb_data = data["idb_config"]
dt_data  = data["fecha_config"]

#Fecha donde se saca las medidas
date_query_start = datetime.datetime(dt_data["año"],dt_data["mes"],dt_data["dia"],gen_data["hora_apertura"] - gen_data["utc_zone"],0,0)
date_query_stop  = datetime.datetime(dt_data["año"],dt_data["mes"],dt_data["dia"],gen_data["hora_cierre"]- gen_data["utc_zone"],0,0)

#Seteando client_mall de influxdb
token  = os.environ.get("INFLUXDB_TOKEN")           #Token API que nos da InfluxDB
org    = idb_data["org"]                            #Organizacion creada en InfluxDB
url    = idb_data["url"]                            #Direccion al servicio de Influxdb
bucket = idb_data["bucket"]                         #Bucket donde se guardaran las medidas

#Iniciando client_mall
client_idb = idb.InfluxDBClient(
    url = url,
    token = token,
    org = org
)

query_api = client_idb.query_api()

def sort_by_value(arr): #el valor para la comparacion tiene que estar en arr[0]
    for i in range(len(arr) - 1, 0 ,-1):
        swap = False
        for j in range(i):
            if arr[j][0] > arr[j+1][0]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swap = True
        if not swap:
            break
    return arr
        
#Una fincion que improme una separacion
def separation():
    print("-----------------------------------------------")

#Menu para elegir opciones
def menu():
    print("Elija Opcion:\n")
    print("1.Tiempo promedio por persona en mall")
    print("2.Cantidad de personas por hora")
    print("3.Ventas totales por tiendas")
    print("4.Ventas totales por hora")
    
    print("\n0.Salir")
    return input("\nIngrese opcion: ")

#Calcula el tiempo que cada cliente pasa en el mall y el tiempo promedio
def mean_time():
    query = f'from(bucket: "{bucket}")\
            |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
            |> filter(fn: (r) => r._measurement == "Cliente")\
            |> group(columns: ["Nombre"])'
    result = query_api.query(org=org, query=query)

    #Saca el nombre y las timestamps de influxdb y las guarda en una lista
    person_list = []
    for table in result:
        for record in table.records:
            date = record.get_time()
            time_measure = datetime.datetime(int(date.strftime("%Y")),int(date.strftime("%m")),int(date.strftime("%d")),int(date.strftime("%H")) + gen_data["utc_zone"],int(date.strftime("%M")),int(date.strftime("%S")))
            name_measure= record.values.get("Nombre")

            if name_measure != None:
                print(f"Nombre: {name_measure}, Timestamp: {time_measure}, hora en int: {time_measure.strftime("%H:%M:%S")}")
                if len(person_list) == 0:
                    print("Agregado a lista de persona")
                    person_data = [name_measure,time_measure.strftime("%H:%M:%S"),time_measure.strftime("%H:%M:%S")]
                    person_list.append(person_data)
                else:
                    for i in range(0,len(person_list)):
                        if i == len(person_list)-1 and person_list[i][0] != name_measure:
                            print("Nombre no esta en la lista, Agregando...")
                            person_data = [name_measure,time_measure.strftime("%H:%M:%S"),time_measure.strftime("%H:%M:%S")]
                            person_list.append(person_data)
                        elif i != len(person_list) and person_list[i][0] == name_measure:
                            if person_list[i][1] > time_measure.strftime("%H:%M:%S"):
                                print("Menor tiempo")
                                person_list[i][1] = time_measure.strftime("%H:%M:%S")
                            if person_list[i][2] < time_measure.strftime("%H:%M:%S"):
                                print("Mayor tiempo")
                                person_list[i][2] = time_measure.strftime("%H:%M:%S")
    
    if len(person_list) == 0:
        print("No hay data")
        exit()

    #Calcula el tiempo que se queda en el mall
    person_time_list = []
    for person in person_list:
        enter = person[1].split(":")
        for i in range (0,len(enter)):
            enter[i] = int(enter[i])
        out = person[2].split(":")
        for i in range (0,len(out)):
            out[i] = int(out[i])

        second = out[2] - enter[2]
        minute = out[1] - enter[1]
        hour   = out[0] - enter[0]

        if second < 0:
            second += 60
            minute -= 1

        if minute < 0:
            minute  += 60
            hour -= 1


        if second / 10 < 1:
            if minute / 10 < 1:
                print(f"Persona: {person[0]}, Entrada: {person[1]}, Salida: {person[2]}, Tiempo total: {hour}:0{minute}:0{second}")
            else:
                print(f"Persona: {person[0]}, Entrada: {person[1]}, Salida: {person[2]}, Tiempo total: {hour}:{minute}:0{second}")
        else:
            if minute / 10 < 1:
                print(f"Persona: {person[0]}, Entrada: {person[1]}, Salida: {person[2]}, Tiempo total: {hour}:0{minute}:{second}")
            else:
                print(f"Persona: {person[0]}, Entrada: {person[1]}, Salida: {person[2]}, Tiempo total: {hour}:{minute}:{second}")

        person_time_list.append(minute + (hour *60))

    #Calcula el tiempo prometio que se quedan las personas
    add = 0
    for i in person_time_list:
        add += i
    mean = add/len(person_time_list)

    temp = mean % 60

    mean -= temp
    mean = mean/60

    print()
    if mean < 1:
        print(f"Tiempo promedio de estadia: {temp} minutos")
    else:
        if  temp < 10:
            print(f"Tiempo promedio de estadia: {int(mean)}:0{int(temp)} horas")
        else:
            print(f"Tiempo promedio de estadia: {int(mean)}:{int(temp)} horas")

def mall_sells():
    query = f'from(bucket: "{bucket}")\
    |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
    |> filter(fn: (r) => r._measurement == "Compras")\
    |> filter(fn: (r) => r._field == "Compra")'
    result = query_api.query(org=org, query=query)

    shops_list = []
    for table in result:
        for record in table.records:
            shop_name = record.values.get("Tienda")
            if len(shops_list) == 0:
                shop = [shop_name,1]
                shops_list.append(shop)

            for i in range(0,len(shops_list)):
                if i == len(shops_list) - 1 and shops_list[i][0] != shop_name:
                    shop = [shop_name,1]
                    shops_list.append(shop)

                elif i != len(shops_list) and shops_list[i][0] == shop_name:
                    shops_list[i][1] += 1
                    break
    
    shops_list = sort_by_value(shops_list)

    add = 0
    for i in shops_list:
        print(f"Tienda {i[0]} vendio {i[1]} productos")
        add += i[1]

    print(f"\nVentas totales: {add}")
            

def sells_per_hour():
    query = f'from(bucket: "{bucket}")\
    |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
    |> filter(fn: (r) => r._measurement == "Compras")\
    |> filter(fn: (r) => r._field == "Compra")'
    result = query_api.query(org=org, query=query)

    hour_list = []
    for table in result:
        for record in table.records:
            time_data = record.get_time()
            hour =  int(time_data.strftime("%H")) + gen_data["utc_zone"]

            if len(hour_list) == 0:
                hour_list.append([hour,1])
            
            for i in range(0,len(hour_list)):
                if i == len(hour_list) - 1 and hour_list[i][0] != hour:
                    add_hour = [hour,1]
                    hour_list.append(add_hour)

                elif i != len(hour_list) and hour_list[i][0] == hour:
                    hour_list[i][1] += 1
                    break

    hour_list = sort_by_value(hour_list)
    
    add = 0
    for i in hour_list:
        print(f"De {i[0]}:00 a {i[0] + 1}:00 se realizaron {i[1]} ventas")
        add += i[1]

    print(f"\nVentas totales: {add}")
            
def people_per_hour():
    query = f'from(bucket: "{bucket}")\
            |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
            |> filter(fn: (r) => r._measurement == "Cliente")\
            |> group(columns: ["Nombre"])'
    result = query_api.query(org=org, query=query)

    hour_list = []

    for i in range(gen_data["hora_apertura"],gen_data["hora_cierre"]):
                temp = [i,[]]
                hour_list.append(temp)

    for table in result:
        for record in table.records:
            hour_data = record.get_time()
            hour = int(hour_data.strftime("%H")) + gen_data["utc_zone"]
            name_data = record.values.get("Nombre")
            
            

            for i in hour_list:
                if i[0] == hour:
                    if name_data not in i[1]:
                        i[1].append(name_data)
                    break

    #hour_list = sort_by_value(hour_list)

    for i in hour_list:
        print(f"De {i[0]}:00 a {i[0] + 1}:00 hubieron {len(i[1])} personas")




def main():
    x = False
    while x == False:
        try:
            opt = int(menu())
            match opt:
                case 1:
                    separation()
                    try:
                        print("Opcion 1\n")
                        mean_time()
                    except:
                        print("Error!")
                    separation()
                
                case 2:
                    separation()
                    try:
                        print("Opcion 2\n")
                        people_per_hour()
                    except:
                        print("ERROR!")
                    separation()

                case 3:
                    separation()
                    try:
                        print("Opcion 3\n")
                        mall_sells()
                    except:
                        print("ERROR!")
                    separation()

                case 4:
                    separation()
                    try:
                        print("Opcion 4\n")
                        sells_per_hour()
                    except:
                        print("ERROR!")
                    separation()

                
                case 0:
                    separation()
                    print("Saliendo...")
                    separation()
                    x = True
                
                case _:
                    separation()
                    print("ERROR! No es una opcion")
                    separation()
        except:
            separation()
            print("ERROR! Ingrese un numero")
            separation()
    
    #mean_time()
    #mall_sells()
    #sells_per_hour()
    #people_per_hour()

    

if __name__ == "__main__":
    main()