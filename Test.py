#Importar librerias
import influxdb_client, os, time, random, psutil
from influxdb_client.client.write_api import SYNCHRONOUS

#Setear Valores
token = os.environ.get("INFLUXDB_TOKEN") #Token API que nos da InfluxDB
org = "Practica 2024"                    #Organizacion creada en InfluxDB
url = "http://localhost:8086"            #Direccion al servicio de Influxdb
bucket="testing"                         #Bucket donde se guardaran las medidas

#Para iniciar el cliente, se nececita un objeto cliente con los valores anteriores
client = influxdb_client.InfluxDBClient(
    url = url,
    token = token,
    org = org
)

#Se inicia un write client
write_api = client.write_api(write_options=SYNCHRONOUS)

#Se crea un objeto point con el cual se guardara la informacion en InfluxDB 
p = influxdb_client.Point("my_measurament").tag("location","Prague").field("Temperature",25.3)
write_api.write(bucket=bucket, org=org, record=p)

#Ejemplo

#Este ejemplo les da a las medidas la misma timestamp
for i in range(0,5):
    #Agregando numeros aleatorios
    number = random.randint(1,100)
    print(f"Numero Generado: {number}")
    r = influxdb_client.Point("Random Numbers").tag("type","num").field("Number",number)
    

    #Agregando uso de memoria
    mem_usage = psutil.virtual_memory()
    mem_percentage = mem_usage.percent
    print(f"Uso de memoria: {mem_percentage}%")
    m = influxdb_client.Point("Memory Usage").tag("type","mem").field("Percentage",mem_percentage)

    #Agregando uso de CPU
    cpu_usage = psutil.cpu_percent()
    print(f"Uso de CPU: {cpu_usage}%")
    c = influxdb_client.Point("CPU Usage").tag("type","cpu").field("Percentage",cpu_usage)

    #manda a influxDB las medidas al mismo tiempo
    write_api.write(bucket=bucket, org=org, record=[r,m,c])


    time.sleep(2)

#Hacemos una query en este caso quiero que me muestre el uso de cpu, memoria y el numero aleatorio en una misma linea

query_api = client.query_api()

#Creamos la query
query = 'from(bucket: "testing")\
    |> range(start: -5m)\
    |> filter(fn: (r) => r.type == "cpu" or r.type == "mem" or r.type == "num")'
    
#range: Cuanto en funcion del tiempo se quiere mostrar de la base de datos, en este caso seria 3 minutos
#filter: filtra los valores a leer

#Toma los valores guardados en Influxdb
result = query_api.query(org=org, query=query)
results = []

#Imprime las mediciones sacadas de Influxdb
for table in result:
    for record in table.records:
        if record.values.get("type") == "cpu":
            print(f"CPU Usage: {record.get_value()}%, Timestamp: {record.get_time()}")
        elif record.values.get("type") == "mem":
            print(f"Memory Usage: {record.get_value()}%, Timestamp: {record.get_time()}")
        elif record.values.get("type") == "num":
            print(f"Number Generated: {record.get_value()}, Timestamp: {record.get_time()}")
        results.extend((record.get_field(), record.get_value(), record.values.get("type")))

#get_value(): saca los valores de la medida
#get_time(): saca el tiempo de medicion
#value.get("<tag>"): saca los valores asignados como tag        

#print(results)
                       
