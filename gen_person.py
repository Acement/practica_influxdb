import random,time,os,json
import datetime
import numpy as np
import multiprocessing as mp
import influxdb_client as idb
from influxdb_client.client.write_api import SYNCHRONOUS

with open("config.json",'r') as f:
    data = json.load(f)
gen_data = data["gen_config"]
idb_data = data["idb_config"]

with open("temperature.json") as f:
    data= json.load(f)
temperature_data = data["temperature"]

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
write_api = client_idb.write_api(write_options=SYNCHRONOUS)

#pasa la hora a int
def hour_to_int(hour):
    return ((hour[0]-gen_data["hora_apertura"])*60) + hour[1]

#suma 1 a los minutos
def next_time(hour):
    hour[1] += 1
    if hour[1]  >= 60:
        hour[0] += 1
        hour[1] = 0
    return hour

def hour_to_date(hour):
    date_sim = datetime.datetime.now()
    return datetime.datetime(int(date_sim.strftime("%Y")),int(date_sim.strftime("%m")),int(date_sim.strftime("%d")),hour[0] - gen_data["utc_zone"],hour[1],0,0)

def gen_person(nombre):
    #Variables externas
    shop       = []
    shops_list = []

    for i in gen_data["edificio"]:
        for j in i["tiendas"]:
            shop = [j,i["id"],0]
            shops_list.append(shop)

    #Genera la hora de inicio
    current_hour = [random.randint(gen_data["hora_apertura"],gen_data["hora_cierre"]-1),random.randint(0,59)]

    #Sacar la temperatura
    hora_temperatura = temperature_data[hour_to_int(current_hour)]
    print(f"Hora de comienzo: {current_hour}, Temperatura: {hora_temperatura}")

    ext_var = {
        "tiendas"    : shops_list,                  #Tiendas del mall
        "temperatura": hora_temperatura[1],         #Temperatura fuera del mall
        "num"        : 0}                           #Numero utilizado para ver si el client_mall sale del mall
    
    
    #Variables de client_mall
    client_mall = {
        "nombre"        : nombre,                                                                            #Nombre del client_mall
        "hora"          : current_hour,                                                                      #Hora del cliente
        "tienda_actual" : "Entrada",                                                                         #Tienda en la que se encuentra el client_mall
        "id_piso"       : 0,                                                                                 #Id del piso actual
        "prob_compra"   : random.randint(0,30),                                                              #Probabilidad de comprar algun item en tienda
        "prob_salir"    : round(((-np.pow(hora_temperatura[1],2)/60)+(hora_temperatura[1]/2)+(45/4)),2),     #Probabilidad de que el client_mall salga del mall
        "prob_cambio"   : random.randint(20,50)}                                                             #Probabilidad de cambiarse de tienda
    
    #Genera data
    while (ext_var.get("num") <= (100 - client_mall.get("prob_salir"))):



        #Calcula la probabilidad de que el client_mall salga
        if hora_temperatura[1] > 45 or hora_temperatura[1] < -15:    #Valores donde es 0 en la formula de probabilidad
            prob_salir = 0
        else:
            prob_salir = round(((-np.pow(hora_temperatura[1],2)/60)+(hora_temperatura[1]/2)+(45/4)),2)          #Formula para calcular la probabilidad tal que a -15ºC o 45ºC sea 0 (valores minimos) y la probabilidad a 15ºC sea 15%
        
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

                        #Sube el punto a influxdb

                        date_sim = hour_to_date(current_hour)
                        print(f"Fecha                 : {date_sim}")

                        p = idb.Point("Cliente").field("Temperatura",hora_temperatura[1]).tag("Nombre",client_mall.get("nombre")).tag("Tienda actual",client_mall.get("tienda_actual")).time(date_sim)
                        write_api.write(bucket=bucket, org=org, record=p)

                        print(f"Nombre de cliente     : {client_mall.get("nombre")}")
                        print(f"Temperatura afuera    : {hora_temperatura[1]}C")
                        print(f"Tienda actual         : {client_mall.get("tienda_actual")}")
                        if client_mall.get("hora")[1] < 10:
                            print(f"Hora                  : {client_mall.get("hora")[0]}:0{client_mall.get("hora")[1]}")
                        else:
                            print(f"Hora                  : {client_mall.get("hora")[0]}:{client_mall.get("hora")[1]}")
                        
                        print("------------------------------------------------------")

                        client_mall["hora"]= next_time(current_hour)

                        if client_mall.get("hora")[0] == gen_data["hora_cierre"]:
                            ext_var["num"] = 100
                            break
                        else:
                            hora_temperatura = temperature_data[hour_to_int(current_hour)]
                        


                    client_mall["tienda_actual"] = tiendas[temp][0]
                    client_mall["id_piso"] = tiendas[temp][1]

                else:
                    client_mall["tienda_actual"] = tiendas[temp][0]
                    client_mall["id_piso"] = tiendas[temp][1]

        date_sim = hour_to_date(current_hour)
        print(f"Fecha                 : {date_sim}")
        print(f"Nombre de cliente     : {client_mall.get("nombre")}")
        print(f"Temperatura afuera    : {hora_temperatura[1]}C")
        print(f"Probabilidad de salir : {abs(prob_salir)}%")
        print(f"Tienda actual         : {client_mall.get("tienda_actual")}")
        if client_mall.get("hora")[1] < 10:
            print(f"Hora                  : {client_mall.get("hora")[0]}:0{client_mall.get("hora")[1]}")
        else:
            print(f"Hora                  : {client_mall.get("hora")[0]}:{client_mall.get("hora")[1]}")

        #Realiza compra en la tienda actual
        if client_mall.get("tienda_actual") != "Transito" and client_mall.get("tienda_actual") != "Entrada":
            if random.randint(1,100) >= 100 - client_mall.get("prob_compra"):
                tienda_actual = client_mall.get("tienda_actual")
                print("------------------------------------------------------")
                date_sim = hour_to_date(current_hour)
                print(f"Fecha                 : {date_sim}")
                print(f"{client_mall.get("nombre")} realizo compra en tienda {tienda_actual}")
                for i in range(0,len(tiendas)):
                    if tienda_actual == tiendas[i][0]:
                        ext_var["tiendas"][i][2] += 1
                        c = idb.Point("Compras").tag("Nombre",client_mall.get("nombre")).tag("Tienda",tienda_actual).field("Compra",1).time(date_sim)
                        write_api.write(bucket=bucket, org=org, record=c)
                        break

        #Manda la informacion a la base de datos
        p = idb.Point("Cliente").field("Temperatura",hora_temperatura[1]).tag("Nombre",client_mall.get("nombre")).tag("Tienda actual",client_mall.get("tienda_actual")).time(date_sim)
        write_api.write(bucket=bucket, org=org, record=p)

        ext_var["num"] = random.randint(1,100)
        print(f"Numero                : {ext_var.get("num")}")

        client_mall["hora"] = next_time(current_hour)

        if client_mall.get("hora")[0] == gen_data["hora_cierre"]:
            ext_var["num"] = 100
        else:
            hora_temperatura = temperature_data[hour_to_int(current_hour)]

        print("------------------------------------------------------")


    print(f"{client_mall.get("nombre")} sale del mall")

    #Al terminar de generar data para influx db muestra la cantidad de veces que el cliente compro
    for i in ext_var.get("tiendas"):
        print(f"Nombre Tienda: {i[0]}, Cantidad de ventas: {i[2]}")



if __name__ == '__main__':
    name_list = []

    cant_client = gen_data["cant_clientes"]
    cant_max_client = len(gen_data["nombres"]) * len(gen_data["apellidos"]) * len(gen_data["apellidos"])           #Cantidad maxima posible de nombres diferentes

    #Checkea que la cantidad de clientes requeridos no supera a la cantidad de nombres posibles
    if cant_client > cant_max_client:
        print(f"Error! la cantidad de clientes es mayor a la cantidad de nombres posibles")
        print(f"Se cambio a cantidad cantidad de nombres posibles: {cant_max_client}")
        cant_client = cant_max_client

    #Genera los nombres de los clientes
    for i in range(0,cant_client):
        gen_name = random.choice(gen_data["nombres"]) + " " + random.choice(gen_data["apellidos"]) + " " + random.choice(gen_data["apellidos"])     #Crea un nombre aleatorio segun lista

        #Verificar que no se repitan los nombres
        while gen_name in name_list:
            gen_name= random.choice(gen_data["nombres"]) + " " + random.choice(gen_data["apellidos"]) + " " + random.choice(gen_data["apellidos"])
        name_list.append(gen_name)
    
    #Inicia los procesos en paralelo
    #mp.Pool().map(gen_person,name_list)

    for i in name_list:
        gen_person(i)

    print(name_list)
    print("Generacion de datos terminada")
    print(f"cant clientes = {cant_client}")
    print(f"org           = {org}")
    print(f"url           = {url}")
    print(f"bucket        = {bucket}")