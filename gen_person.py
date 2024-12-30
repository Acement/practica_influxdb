import random,time,os,json
import numpy as np
import multiprocessing as mp
import influxdb_client as idb
from influxdb_client.client.write_api import SYNCHRONOUS

with open("config.json",'r') as f:
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
write_api = client_idb.write_api(write_options=SYNCHRONOUS)

def gen_person(nombre):
    #Variables externas
    shop = []
    shops_list = []

    for i in data["gen_config"]["edificio"]:
        for j in i["tiendas"]:
            shop = [j,i["id"],0]
            shops_list.append(shop)

    ext_var = {
        "tiendas": shops_list,                                      #Tiendas del mall
        "temperatura":data["gen_config"]["temperatura"],            #Temperatura fuera del mall
        "num": 0}                                                   #Numero utilizado para ver si el client_mall sale del mall

    #Variables de client_mall
    client_mall = {
        "nombre": nombre,                                                                                                               #Nombre del client_mall
        "tienda_actual": "Entrada",                                                                                                     #Tienda en la que se encuentra el client_mall
        "id_piso": 0,                                                                                                                   #Id del piso actual
        "prob_compra": random.randint(0,30),                                                                                            #Probabilidad de comprar algun item en tienda
        "prob_salir":round(((-np.pow(data["gen_config"]["temperatura"],2)/60)+(data["gen_config"]["temperatura"]/2)+(45/4)),2),         #Probabilidad de que el client_mall salga del mall
        "prob_cambio": random.randint(20,50)}                                                                                           #Probabilidad de cambiarse de tienda
    
    #Genera data
    while (ext_var.get("num") <= (100 - client_mall.get("prob_salir"))):
        
        #Genera temperatura
        temperatura = round((ext_var.get("temperatura") + (random.randint(-5 + data["gen_config"]["temp_cambio"],5 + data["gen_config"]["temp_cambio"]))/10),2)

        if temperatura > 45:            #Temperatura Maxima
            temperatura = 45
        elif temperatura < -15:         #Temperatura Minima
            temperatura = -15

        ext_var["temperatura"] = temperatura
        data["gen_config"]["temperatura"] = temperatura
        with open("config.json",'w') as f:
            json.dump(data,f,indent=1)

        #Calcula la probabilidad de que el client_mall salga
        if temperatura > 45 or temperatura < -15:                                               #Si se pasa de los limites la prob de que salga es 1% (Al generar numeros aleatorios para ver si sale, tiene que generar 100)
            prob_salir = 0
        else:
            prob_salir = round(((-np.pow(temperatura,2)/60)+(temperatura/2)+(45/4)),2)          #Formula para calcular la probabilidad tal que a -15ºC o 45ºC sea 0 (valores minimos) y la probabilidad a 15ºC sea 15%
        
        client_mall["prob_salir"] = prob_salir

        #Elige una tienda y se cambia a ella
        tiendas = ext_var.get("tiendas")
        if random.randint(1,100) >= 100 - client_mall.get("prob_cambio"):
            temp = random.randint(0,len(tiendas) - 1)

            #Si esta en la entrada cambia a tienda en cualquier piso
            if client_mall["tienda_actual"] == "Entrada":
                client_mall["tienda_actual"] = tiendas[temp][0]
                client_mall["id_piso"] = tiendas[temp][1]

            else:
                diff_piso = abs(client_mall["id_piso"] - tiendas[temp][1])

                if diff_piso != 0:
                    for i in range(0,diff_piso):
                        client_mall["tienda_actual"] = "Transito"
                        client_mall["id_piso"] = 0

                        #La temeperatura tambien cambia en transito
                        temperatura = round((ext_var.get("temperatura") + (random.randint(-5 + data["gen_config"]["temp_cambio"],5 + data["gen_config"]["temp_cambio"]))/10),2)

                        if temperatura > 45:            #Temperatura Maxima
                            temperatura = 45
                        elif temperatura < -15:         #Temperatura Minima
                            temperatura = -15

                        ext_var["temperatura"] = temperatura
                        data["gen_config"]["temperatura"] = temperatura
                        #sube la temperatura generata al JSON
                        with open("config.json",'w') as f:
                            json.dump(data,f,indent=1)

                        #Sube el punto a influxdb
                        p = idb.Point("Cliente").field("Temperatura",ext_var.get("temperatura")).tag("Nombre",client_mall.get("nombre")).tag("Tienda actual",client_mall.get("tienda_actual"))
                        write_api.write(bucket=bucket, org=org, record=p)

                        
                        print(f"Nombre de cliente: {client_mall.get("nombre")}")
                        print(f"Temperatura afuera: {temperatura}C")
                        print(f"Tienda actual: {client_mall.get("tienda_actual")}")
                    
                        time.sleep(1)

                    client_mall["tienda_actual"] = tiendas[temp][0]
                    client_mall["id_piso"] = tiendas[temp][1]

                else:
                    client_mall["tienda_actual"] = tiendas[temp][0]
                    client_mall["id_piso"] = tiendas[temp][1]

        print(f"Nombre de cliente: {client_mall.get("nombre")}")
        print(f"Temperatura afuera: {temperatura}C")
        print(f"Probabilidad de salir: {abs(prob_salir)}%")
        print(f"Tienda actual: {client_mall.get("tienda_actual")}")

        #Realiza compra en la tienda actual
        if client_mall.get("tienda_actual") != "Transito":
            if random.randint(1,100) >= 100 - client_mall.get("prob_compra"):
                tienda_actual = client_mall.get("tienda_actual")
                print(f"{client_mall.get("nombre")} realizo compra en tienda {tienda_actual}")
                for i in range(0,len(tiendas)):
                    if tienda_actual == tiendas[i][0]:
                        ext_var["tiendas"][i][2] += 1
                        c = idb.Point("Compras").tag("Nombre",client_mall.get("nombre")).tag("Tienda",tienda_actual).field("Compra",1)
                        write_api.write(bucket=bucket, org=org, record=c)
                        break

        #Manda la informacion a la base de datos
        p = idb.Point("Cliente").field("Temperatura",ext_var.get("temperatura")).tag("Nombre",client_mall.get("nombre")).tag("Tienda actual",client_mall.get("tienda_actual"))
        write_api.write(bucket=bucket, org=org, record=p)

        ext_var["num"] = random.randint(1,100)
        print(f"Numero: {ext_var.get("num")}")

        time.sleep(1)

    print(f"{client_mall.get("nombre")} sale del mall")

    #Al terminar de generar data para influx db muestra la cantidad de veces que el cliente compro
    for i in ext_var.get("tiendas"):
        print(f"Nombre Tienda: {i[0]}, Cantidad de ventas: {i[2]}")

if __name__ == '__main__':
    name_list = []

    cant_client = data["gen_config"]["cant_clientes"]
    cant_max_client = len(data["gen_config"]["nombres"]) * len(data["gen_config"]["apellidos"]) * len(data["gen_config"]["apellidos"])           #Cantidad maxima posible de nombres diferentes

    #Checkea que la cantidad de clientes requeridos no supera a la cantidad de nombres posibles
    if cant_client > cant_max_client:
        print(f"Error! la cantidad de clientes es mayor a la cantidad de nombres posibles")
        print(f"Se cambio a cantidad cantidad de nombres posibles: {cant_max_client}")
        cant_client = cant_max_client

    #Genera los nombres de los clientes
    for i in range(0,cant_client):
        gen_name = random.choice(data["gen_config"]["nombres"]) + " " + random.choice(data["gen_config"]["apellidos"]) + " " + random.choice(data["gen_config"]["apellidos"])     #Crea un nombre aleatorio segun lista

        #Verificar que no se repitan los nombres
        while gen_name in name_list:
            gen_name= random.choice(data["gen_config"]["nombres"]) + " " + random.choice(data["gen_config"]["apellidos"]) + " " + random.choice(data["gen_config"]["apellidos"])
        name_list.append(gen_name)
    
    #Inicia los procesos en paralelo
    mp.Pool().map(gen_person,name_list)

    print(name_list)
    print("Generacion de datos terminada")
    print(f"cant clientes = {cant_client}")
    print(f"org           = {org}")
    print(f"url           = {url}")
    print(f"bucket        = {bucket}")