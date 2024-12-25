import random,time,os
import numpy as np
import multiprocessing as mp
import influxdb_client as idb
from influxdb_client.client.write_api import SYNCHRONOUS

nombres = ["Pedro", "Juan", "Diego", "Ana", "Pablo", "Fernanda", "Alida", "Jose", "Andres", "Emilia"]
apellidos = ["Cisterna", "Salas", "Saez", "Celis", "Fernandez", "Cid", "Inostroza","Perez", "Peso", "Gonzales"]

#Seteando client_mall de influxdb
token = os.environ.get("INFLUXDB_TOKEN") #Token API que nos da InfluxDB
org = "Practica 2024"                    #Organizacion creada en InfluxDB
url = "http://localhost:8086"            #Direccion al servicio de Influxdb
bucket="Test mall"                     #Bucket donde se guardaran las medidas

#Iniciando client_mall
client_idb = idb.InfluxDBClient(
    url = url,
    token = token,
    org = org
)
write_api = client_idb.write_api(write_options=SYNCHRONOUS)



def gen_person(nombre):
    #Variables externas
    ext_var = {
        "tiendas": [['a',0],['b',0],['c',0],['d',0]],                   #Tiendas del mall
        "temperatura":15,                                               #Temperatura fuera del mall
        "num": 0}                                                       #Numero utilizado para ver si el client_mall sale del mall

    #Variables de client_mall
    client_mall = {
        "nombre": nombre,      #Nombre del client_mall
        "tienda_actual": "Transito",                                            #Tienda en la que se encuentra el client_mall
        "prob_compra": random.randint(0,30),                                    #Probabilidad de comprar algun item en tienda
        "prob_salir":round(((-np.pow(15,2)/60)+(15/2)+(45/4)),2),               #Probabilidad de que el client_mall salga del mall
        "prob_cambio": random.randint(20,50)}                                   #Probabilidad de cambiarse de tienda
    #Genera data
    while (ext_var.get("num") <= (100 - client_mall.get("prob_salir"))):
        print(f"Nombre de cliente: {client_mall.get("nombre")}")
        #Genera temperatura
        temperatura = round((ext_var.get("temperatura") + (random.randint(-10,11))/10),2)
        if temperatura > 45:
            temperatura = 45
        elif temperatura < -15:
            temperatura = -15
        ext_var["temperatura"] = temperatura

        #Calcula la probabilidad de que el client_mall salga
        if temperatura > 45 or temperatura < -15:
            prob_salir = 0
        else:
            prob_salir = round(((-np.pow(temperatura,2)/60)+(temperatura/2)+(45/4)),2)
        
        client_mall["prob_salir"] = prob_salir

        print(f"Temperatura afuera: {temperatura}C")
        print(f"Probabilidad de salir: {abs(prob_salir)}%")

        #Elige una tienda
        tiendas = ext_var.get("tiendas")
        if random.randint(1,100) >= 100 - client_mall.get("prob_cambio"):
            temp = random.randint(0,len(tiendas) - 1)
            client_mall["tienda_actual"] = tiendas[temp][0]
        print(f"Tienda actual: {client_mall.get("tienda_actual")}")

        #Realiza compra en la tienda actual
        if client_mall.get("tienda_actual") != "Transito":
            if random.randint(1,100) >= 100 - client_mall.get("prob_compra"):
                tienda_actual = client_mall.get("tienda_actual")
                print(f"{client_mall.get("nombre")} realizo compra en tienda {tienda_actual}")
                for i in range(0,len(tiendas)):
                    if tienda_actual == tiendas[i][0]:
                        ext_var["tiendas"][i][1] += 1
                        c = idb.Point("Compras").tag("Tienda",tienda_actual).field("Compra",1)
                        write_api.write(bucket=bucket, org=org, record=c)
                        break

        
        #Manda la informacion a la base de datos
        p = idb.Point("Cliente").field("Temperatura",ext_var.get("temperatura")).tag("Nombre",client_mall.get("nombre")).tag("Tienda actual",client_mall.get("tienda_actual"))
        write_api.write(bucket=bucket, org=org, record=p)

        ext_var["num"] = random.randint(1,100)
        print(f"Numero: {ext_var.get("num")}")

    
        time.sleep(1)

    print(f"{client_mall.get("nombre")} sale del mall")

    for i in ext_var.get("tiendas"):
        print(f"Nombre Tienda: {i[0]}, Cantidad de ventas: {i[1]}")


if __name__ == '__main__':
    nombres_list = []

    for i in range(0,50):
        gen_nombre = random.choice(nombres) + " " + random.choice(apellidos) + " " + random.choice(apellidos)
        #Verificar que no se repitan los nombres
        while gen_nombre in nombres_list:
            gen_nombre = random.choice(nombres) + " " + random.choice(apellidos) + " " + random.choice(apellidos)
        nombres_list.append(gen_nombre)
    

    mp.Pool().map(gen_person,nombres_list)

    print(nombres_list)
    print("Generacion de datos terminada")