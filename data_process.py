import os
import numpy as np
import influxdb_client as idb
from influxdb_client.client.write_api import SYNCHRONOUS

#Seteando client_mall de influxdb
token = os.environ.get("INFLUXDB_TOKEN") #Token API que nos da InfluxDB
org = "Practica 2024"                    #Organizacion creada en InfluxDB
url = "http://localhost:8086"            #Direccion al servicio de Influxdb
bucket="Test mall 3"                     #Bucket donde se sacaran las medidas

#Iniciando client_mall
client_idb = idb.InfluxDBClient(
    url = url,
    token = token,
    org = org
)

query_api = client_idb.query_api()

def main():
    query1 = f'from(bucket: "{bucket}")\
            |> range(start: -1h)\
            |> group(columns: ["Nombre"])'
    result = query_api.query(org=org, query=query1)

    for table in result:
        for record in table.records:
            print(f"Nombre: {record.values.get("Nombre")}, Timestamp: {record.get_time()}")

if __name__ == "__main__":
    main()