import os,json
import numpy as np
import influxdb_client as idb
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime

#Cargando JSON
with open("config.json") as f:
    data = json.load(f)

#Seteando client_mall de influxdb
token  = os.environ.get("INFLUXDB_TOKEN")           #Token API que nos da InfluxDB
org    = data["idb_config"]["org"]                  #Organizacion creada en InfluxDB
url    = data["idb_config"]["url"]                  #Direccion al servicio de Influxdb
bucket = data["idb_config"]["bucket"]               #Bucket donde se guardaran las medidas

#Iniciando client_mall
client_idb = idb.InfluxDBClient(
    url = url,
    token = token,
    org = org
)

query_api = client_idb.query_api()

def mean_time():
    query = f'from(bucket: "{bucket}")\
            |> range(start: -15m)\
            |> filter(fn: (r) => r._measurement == "Cliente")\
            |> group(columns: ["Nombre"])'
    result = query_api.query(org=org, query=query)

    #Saca el nombre y las timestamps de influxdb y las guarda en una lista
    person_list = []
    for table in result:
        for record in table.records:
            time_measure = record.get_time()
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

        sec = 0
        min = 0

        sec = out[2] - enter[2]
        if sec == 0 and enter[1] < out[1]:
            min = 1
        elif sec < 0:
            sec = 60 + sec
            min = 1
        
        min = out[1] - enter[1] - min


        if sec / 10 < 1:
            print(f"Persona: {person[0]}, Entrada: {person[1]}, Salida: {person[2]}, Tiempo total: {min}:0{sec}")
        else:
            print(f"Persona: {person[0]}, Entrada: {person[1]}, Salida: {person[2]}, Tiempo total: {min}:{sec}")

        person_time_list.append(sec + (min * 60))

    #Calcula el tiempo prometio que se quedan las personas
    add = 0
    for i in person_time_list:
        add += i
    mean = add/len(person_time_list)
    print()
    print(f"Tiempo promedio de estadia: {mean}")

def mall_sells():
    query = f'from(bucket: "{bucket}")\
    |> range(start: -1h)\
    |> filter(fn: (r) => r._measurement == "Compras")\
    |> filter(fn: (r) => r._field == "Compra")'
    

    result = query_api.query(org=org, query=query)

    shops_list = []
    for table in result:
        for record in table.records:
            shop_name = record.values.get("Tienda")
            if len(shops_list) == 0:
                shop = [shop_name,1]
                print("Se agrego la primera tienda")
                print(shop)
                shops_list.append(shop)

            for i in range(0,len(shops_list)):
                if i == len(shops_list) - 1 and shops_list[i][0] != shop_name:
                    shop = [shop_name,1]
                    print("Nueva tienda agregada-------------------------------")
                    print(shop)
                    shops_list.append(shop)

                elif i != len(shops_list) - 1 and shops_list[i][0] == shop_name:
                    print("Agrega venta a tienda")
                    shops_list[i][1] += 1
                    print(shops_list[i])
                    break
                
    for i in shops_list:
        print(f"Tienda {i[0]} vendio {i[1]} productos")

def main():
    mean_time()
    print()
    mall_sells()

    

if __name__ == "__main__":
    main()