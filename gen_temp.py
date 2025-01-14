import json, random

#Carga los datos de configuracion
with open("config.json",'r') as f:
    data = json.load(f)
gen_data = data["gen_config"]
ext_data = data["idb_config"]

#Funcion para generar las temperaturas para simular
def gen_temperature():
    open_time   = 60 * (gen_data["hora_cierre"] - gen_data["hora_apertura"]) #tiempo abierto en minutos
    temperature = gen_data["temperatura"]

    simulated_temp = []
    #Genera la temperatura por minuto
    for i in range(0,open_time + 1):
        temperature = round(temperature + ((random.randint(-5 + gen_data["temp_cambio"],5 + gen_data["temp_cambio"]))/10),2)
        if temperature > gen_data["temp_max"]:
            temperature = gen_data["temp_max"]
        elif temperature < gen_data["temp_min"]:
            temperature = gen_data["temp_min"]
        simulated_temp.append(temperature)

    hour      = gen_data["hora_apertura"]
    minute    = 0
    json_data = []

    #Asigna una hora a la temperatura
    for i in range(0,open_time + 1):
        if minute < 10:
            print(f"Hora: {hour}:0{minute}, Temperatura: {simulated_temp[i]}")
            temp = [f"{hour}:0{minute}",simulated_temp[i]]
        else:
            print(f"Hora: {hour}:{minute}, Temperatura: {simulated_temp[i]}")
            temp = [f"{hour}:{minute}",simulated_temp[i]]

        json_data.append(temp)

        minute += 1

        if minute == 60:
            minute = 0
            hour   +=1

    #Guarda la temperatura simulada en un JSON
    with open("temperature.json",'r') as f:
        data = json.load(f)

    data["temperature"] = json_data

    with open("temperature.json",'w') as f:
        json.dump(data,f,indent= 2)

if __name__ == "__main__":
    gen_temperature()