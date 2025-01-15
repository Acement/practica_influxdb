import os,json
import numpy as np
import influxdb_client as idb
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
import matplotlib.pyplot as plt
from matplotlib import style

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

#Bubble sort modificado
def sort_by_value(arr):#el valor para la comparacion tiene que estar en arr[0]
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
    print("5.Ventas por hora por tienda")
    print("6.Personas por tiendas por minuto")
    
    print("\n0.Salir")
    return input("\nIngrese opcion: ")

#Calcula el tiempo que cada cliente pasa en el mall y el tiempo promedio
def mean_time():
    
    #Consulta a influxdb
    query = f'from(bucket: "{bucket}")\
            |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
            |> filter(fn: (r) => r._measurement == "Cliente")\
            |> group(columns: ["Nombre"])'
    result = query_api.query(org=org, query=query)

    #Saca el nombre y las timestamps de influxdb y las guarda en una lista
    person_list = []
    for table in result:
        for record in table.records:
            date         = record.get_time()
            name_measure = record.values.get("Nombre")
            #Guarda el primer nombre y sus timestamp
            if name_measure != None:
                print(f"Nombre: {name_measure}, Timestamp: {date}, Hora: {date.strftime("%H:%M:%S")}")
                if len(person_list) == 0:
                    print("Agregado a lista de persona")
                    person_data = [name_measure,date.strftime("%H:%M:%S"),date.strftime("%H:%M:%S")]
                    person_list.append(person_data)
                else:
                    for i in range(0,len(person_list)):
                        #Agrega el nombre a la lista si no lo encuentra
                        if i == len(person_list)-1 and person_list[i][0] != name_measure:
                            print("Nombre no esta en la lista, Agregando...")
                            person_data = [name_measure,date.strftime("%H:%M:%S"),date.strftime("%H:%M:%S")]
                            person_list.append(person_data)
                        #si encuentra el nombre compara el timestamp y verifica si es mayor o menor
                        elif i != len(person_list) and person_list[i][0] == name_measure:
                            if person_list[i][1] > date.strftime("%H:%M:%S"):
                                print("Menor tiempo")
                                person_list[i][1] = date.strftime("%H:%M:%S")
                            elif person_list[i][2] < date.strftime("%H:%M:%S"):
                                print("Mayor tiempo")
                                person_list[i][2] = date.strftime("%H:%M:%S")
    
    if len(person_list) == 0:
        print("No hay data")
        exit()

    #Calcula el tiempo que se queda en el mall
    person_time_list = []
    total_time_list = []
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
                total_hour= f"{hour}:0{minute}:0{second}"
            else:
                total_hour= f"{hour}:{minute}:0{second}"
        else:
            if minute / 10 < 1:
                total_hour= f"{hour}:0{minute}:{second}"
            else:
                total_hour= f"{hour}:{minute}:{second}"
                
        #Lo mete a lista con los tiempos totales que se quedaron las personas
        if len(total_time_list) == 0:
            temp = [total_hour,1]
            total_time_list.append(temp)
        else:
            for i in range(0,len(total_time_list)):
                if i == len(total_time_list) - 1 and total_time_list[i][0] != total_hour:
                    temp = [total_hour,1]
                    total_time_list.append(temp)
                elif i != len(total_time_list) and total_time_list[i][0] == total_hour:
                   total_time_list[i][1] += 1
                   break


        person_time_list.append(minute + (hour *60))

    #Ordena la lista de menor a mayor tiempo de estadia
    total_time_list = sort_by_value(total_time_list)

    x = []
    y = []

    for i in total_time_list:
        x.append(i[0])
        y.append(i[1])
        print(i)

    #genera el grafico
    xpoint = np.array(x)
    ypoint = np.array(y)

    barplot = plt.bar(xpoint,ypoint)

    plt.title("Tiempo de estadia")
    plt.xlabel("Tiempo")
    plt.ylabel("Cantidad")
    plt.xticks(rotation=90)

    plt.bar_label(barplot, labels=ypoint,label_type="center")

    figure = plt.gcf()
    figure.set_size_inches(19.20,10.80)
    
    #Guarda el grafico
    plt.savefig("graph/tiempoEstadia.png", dpi = 300, bbox_inches="tight")
    plt.close()

    
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

#calcula las ventas del mall
def mall_sells():

    #Hace la consulta
    query = f'from(bucket: "{bucket}")\
    |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
    |> filter(fn: (r) => r._measurement == "Compras")\
    |> filter(fn: (r) => r._field == "Compra")'
    result = query_api.query(org=org, query=query)

    shops_list = []

    #Genera lista con las tiendas
    for i in gen_data["edificio"]:
        for j in i["tiendas"]:
            shop = [j,0]
            shops_list.append(shop)

    #Saca la informacion de la consulta realizada
    for table in result:
        for record in table.records:
            shop_name = record.values.get("Tienda")
            
            for i in shops_list:
                if shop_name == i[0]:
                    i[1] += 1
    
    x   = []
    y   = [] 
    add = 0
    #Imprime los datos en el terminal y los agrega a una lista
    for i in shops_list:
        print(f"Tienda {i[0]} vendio {i[1]} productos")
        x.append(i[0])
        y.append(i[1])
        add += i[1]
    
    #genera el grafico
    xpoint = np.array(x)
    ypoint = np.array(y)

    barplot = plt.bar(xpoint,ypoint)

    plt.title("Cantidad de ventas totales por tiendas")
    plt.xlabel("Tiendas")
    plt.ylabel("Cantidad de Ventas")
    plt.xticks(rotation=90)


    plt.bar_label(barplot, labels=ypoint,label_type="center")

    print(f"\nVentas totales: {add}")

    #Guarda el grafico
    plt.savefig("graph/VentasTotales.png", dpi = 300, bbox_inches="tight")
    plt.close()

            
#Calcula las ventas del mall por hora
def sells_per_hour():
    
    #Consulta a influxdb
    query = f'from(bucket: "{bucket}")\
    |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
    |> filter(fn: (r) => r._measurement == "Compras")\
    |> filter(fn: (r) => r._field == "Compra")'
    result = query_api.query(org=org, query=query)

    #Genera una lista con la hora y sus valores en 0
    hour_list = []
    for i in range(gen_data["hora_apertura"],gen_data["hora_cierre"]):
        temp = [i,0]
        hour_list.append(temp)

    #Recorre la consulta
    for table in result:
        for record in table.records:
            time_data = record.get_time()
            hour      = int(time_data.strftime("%H")) + gen_data["utc_zone"]
            #Agrega venta a la hora
            for i in hour_list:
                if i[0] == hour:
                    i[1] += 1

    x   = []
    y   = []
    add = 0

    #Imprime los valores y los guarda en listas para generar los graficos
    for i in hour_list:
        print(f"De {i[0]}:00 a {i[0] + 1}:00 se realizaron {i[1]} ventas")
        x.append(f"{i[0]}:00 - {i[0] + 1}:00")
        y.append(i[1])
        add += i[1]

    xpoint = np.array(x)
    ypoint = np.array(y)

    barplot = plt.bar(xpoint,ypoint)

    plt.title("Cantidad de ventas por hora")
    plt.xlabel("Hora")
    plt.ylabel("Cantidad de Ventas")
    plt.xticks(rotation=90)

    plt.bar_label(barplot, labels=ypoint,label_type="center")

    print(f"\nVentas totales: {add}")

    #Guarda el grafico
    plt.savefig("graph/VentasPorHora.png", dpi = 300, bbox_inches="tight")
    plt.close()


#Personas por hora     
def people_per_hour():
    
    #Hace consulta a influxdb
    query = f'from(bucket: "{bucket}")\
            |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
            |> filter(fn: (r) => r._measurement == "Cliente")\
            |> group(columns: ["Nombre"])'
    result = query_api.query(org=org, query=query)

    hour_list = []

    #Genera una lista con las horas
    for i in range(gen_data["hora_apertura"],gen_data["hora_cierre"]):
                temp = [i,[]]
                hour_list.append(temp)

    #Recorre la consulta
    for table in result:
        for record in table.records:
            hour_data = record.get_time()
            hour      = int(hour_data.strftime("%H")) + gen_data["utc_zone"]
            name_data = record.values.get("Nombre")
            
            

            for i in hour_list:
                if i[0] == hour:
                    if name_data not in i[1]:
                        i[1].append(name_data)
                    break

    x = []
    y = []

    for i in hour_list:
        print(f"De {i[0]}:00 a {i[0] + 1}:00 hubieron {len(i[1])} personas")
        x.append(f"{i[0]}:00 - {i[0] + 1}:00")
        y.append(len(i[1]))

    xpoint = np.array(x)
    ypoint = np.array(y)

    barplot = plt.bar(xpoint,ypoint)

    plt.title("Cantidad de personas por hora")
    plt.xlabel("Hora")
    plt.ylabel("Cantidad de Personas")
    plt.xticks(rotation=90)

    plt.bar_label(barplot, labels=ypoint,label_type="center")

    plt.savefig("graph/PersonasPorHora.png", dpi = 300, bbox_inches="tight")
    plt.close()

#Imprime las ventas por hora
def sales_per_shop_per_hour():
    
    #Consulta a influxdb
    query = f'from(bucket: "{bucket}")\
    |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
    |> filter(fn: (r) => r._measurement == "Compras")\
    |> filter(fn: (r) => r._field == "Compra")'
    result = query_api.query(org=org, query=query)

    hour_list = []          #[hora,[[piso1,[[tienda1,ventas],[tienda2,ventas],...]],[piso2,[[tienda1,ventas],[tienda2,ventas],...]],...]]
    for i in range (gen_data["hora_apertura"],gen_data["hora_cierre"]):
        hour = [i]
        for j in gen_data["edificio"]:
            floor = [j["id"]]
            for k in j["tiendas"]:
                shop = [k,0]
                floor.append(shop)
            hour.append(floor)
        hour_list.append(hour)

    add = 0

    #Recorre la consulta
    for tables in result:
        for record in tables.records:
            time_data = record.get_time()
            hour      = int(time_data.strftime("%H")) + gen_data["utc_zone"]
            shop_name = record.values.get("Tienda")

            for i in hour_list:
                if hour == i[0]:
                    num_floor = int(shop_name[0])
                    for j in range(1,len(i[num_floor])):
                        if i[num_floor][j][0] == shop_name:
                            add += 1
                            i[num_floor][j][1] += 1
                            break
                    break
    
    x_total = []            #Guarda la hora
    y_total = []            #Guarda las ventas totales por hora
    for i in hour_list:
        x_shop  = []            #Guarda el nombre de las tiendas
        y_shop  = []            #Guarda las ventas de la hora por tienda
        
        add_per_hour = 0

        print(f"Hora: {i[0]}:00\n")
        for j in range(1,len(i)):
            for k in gen_data["edificio"]:
                if k["id"] == i[j][0]:
                    print(f"Piso:{k["nombre_piso"]}")
                    break
            for k in range(1,len(i[j])):
                print(f"Tienda {i[j][k][0]} hizo {i[j][k][1]} ventas",end = " | ")
                x_shop.append(i[j][k][0])
                y_shop.append(i[j][k][1])
                add_per_hour += i[j][k][1]
            print()
        print(f"Ventas de la hora: {add_per_hour}")
        x_total.append(f"{i[0]}:00")
        y_total.append(add_per_hour)

        #Grafico de tiendas por hora

        xpoint = np.array(x_shop)
        ypoint = np.array(y_shop)

        barplot = plt.bar(xpoint,ypoint)

        plt.title(f"{i[0]}:00 a {i[0] + 1}:00")
        plt.xlabel("Tienda")
        plt.ylabel("Cantidad de Ventas")
        plt.xticks(rotation=90)


        plt.bar_label(barplot, labels=ypoint,label_type="center")

        plt.savefig(f"graph/ventasPTPH/{i[0]}_ventas.png", dpi = 300, bbox_inches="tight")
        plt.close()


        separation()

    #Grafico de total de ventas por hora 
    xpoint = np.array(x_total)
    ypoint = np.array(y_total)

    barplot = plt.bar(xpoint,ypoint)

    plt.title(f"Ventas del dia")
    plt.xlabel("Hora")
    plt.ylabel("Cantidad de Ventas")
    plt.xticks(rotation=90)

    plt.bar_label(barplot, labels=ypoint,label_type="center")

    #Guarda el grafico
    plt.savefig(f"graph/ventasPTPH/total_ventas.png", dpi = 300, bbox_inches="tight")
    plt.close()

    print(f"\nSe realizaron {add} ventas en total")

#Personas por tiendas por minuto
def people_per_store_per_minute():

    #Consulta a influxdb
    query = f'from(bucket: "{bucket}")\
            |> range(start: {date_query_start.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {date_query_stop.strftime("%Y-%m-%dT%H:%M:%SZ")})\
            |> filter(fn: (r) => r._measurement == "Cliente")\
            |> group(columns: ["Nombre"])'
    result = query_api.query(org=org, query=query)

    hour_list = []

    #genera una lista con horas que tambiambien incluyen los minutos
    for i in range(gen_data["hora_apertura"],gen_data["hora_cierre"]):
        hour = [i]
        for j in range(0,60):
            minute = [j,[]]
            hour.append(minute)
        hour_list.append(hour)

    #Recorre la consulta
    for table in result:
        for record in table.records:
            hour_data = record.get_time()
            hour = int(hour_data.strftime("%H"))+ gen_data["utc_zone"]
            minute = int(hour_data.strftime("%M"))
            shop_name = record.values.get("Tienda actual")

            pos_hour = hour - gen_data["hora_apertura"]
            pos_minute = minute +1


            if len(hour_list[pos_hour][pos_minute][1]) == 0:

                shop = [shop_name,1]
                hour_list[pos_hour][pos_minute][1].append(shop)
            else:
                for i in hour_list[pos_hour][pos_minute][1]:
                    if i[0] == shop_name:
                        i[1] += 1
                        break
                    elif i[0] != shop_name and i == hour_list[pos_hour][pos_minute][1][len(hour_list[pos_hour][pos_minute][1]) - 1]:
                        shop = [shop_name,1]
                        hour_list[pos_hour][pos_minute][1].append(shop)
                        break

    #Imprime los valores y los guarda en lista x e y para crear los graficos
    for i in hour_list:
        add_per_hour = 0
        x = []
        y = []
        for j in range(1,len(i)):
            add_per_minute = 0
            if i[j][0] < 10:
                print(f"{i[0]}:0{i[j][0]}",end = ": ")
                x.append(f"{i[0]}:0{i[j][0]}")
            else:
                print(f"{i[0]}:{i[j][0]}",end = ": ")
                x.append(f"{i[0]}:{i[j][0]}")
            print(i[j][1])
            for k in i[j][1]:
                add_per_hour += k[1]
                add_per_minute += k[1]
            y.append(add_per_minute)
        
        #Crea el grafico

        xpoint = np.array(x)
        ypoint = np.array(y)

        barplot = plt.bar(xpoint,ypoint)

        plt.title(f"Personas por minuto de {i[0]}:00 a {i[0] + 1}:00")
        plt.xlabel("Hora")
        plt.ylabel("Cantidad de Personas")
        plt.xticks(rotation=90)

        plt.bar_label(barplot, labels=ypoint,label_type="center")

        figure = plt.gcf()
        figure.set_size_inches(19.20,10.80)

        #Guarda el grafico
        plt.savefig(f"graph/personasPM/{i[0]}_ventas.png", dpi = 300, bbox_inches="tight")
        plt.close()


        print(f"\nPersonas por hora: {add_per_hour}")
        separation()





def main():
    style.use("ggplot")


    #Logica del menu
    x = False
    while x == False:
        try:
            opt = int(menu())
            match opt:

                #Opcion 1: Tiempos promedios
                case 1:
                    separation()
                    try:
                        print("Opcion 1\n")
                        mean_time()
                    except:
                        print("Error!")
                    separation()
                
                #Opcion 2: Personas por hora
                case 2:
                    separation()
                    try:
                        print("Opcion 2\n")
                        people_per_hour()
                    except:
                        print("ERROR!")
                    separation()

                #Opcion 3: Ventas por tienda
                case 3:
                    separation()
                    try:
                        print("Opcion 3\n")
                        mall_sells()
                    except:
                        print("ERROR!")
                    separation()

                #Opcion 4: Ventas por hora
                case 4:
                    separation()
                    try:
                        print("Opcion 4\n")
                        sells_per_hour()
                    except:
                        print("ERROR!")
                    separation()

                #Opcion 5: Ventas por tienda por hora
                case 5:
                    separation()
                    try:
                        print("Opcion 5\n")
                        sales_per_shop_per_hour()
                    except:
                        print("ERROR!")
                    separation()

                #Opcion 6: Personas por tienda por minuto, Grafico: Personas por minuto
                case 6:
                    separation()
                    try:
                        print("Opcion 6\n")
                        people_per_store_per_minute()
                    except:
                        print("ERROR!")
                    separation()
                
                #Opcion 0: Salir
                case 0:
                    separation()
                    print("Saliendo...")
                    separation()
                    x = True
                
                #default
                case _:
                    separation()
                    print("ERROR! No es una opcion")
                    separation()

        #default
        except:
            separation()
            print("ERROR! Ingrese un numero")
            separation() 

#Arranca el programa
if __name__ == "__main__":
    main()