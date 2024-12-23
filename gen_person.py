import random,time
import numpy as np

#Variables externas
ext_var = {
    "tiendas": [['a',0],['b',0],['c',0],['d',0]],
    "temperatura":15,
    "num": 0}

#Variables de cliente
cliente = {
    "nombre": "Juan",                                               #Nombre del cliente
    "tienda_actual": "Transito",                                            #Tienda en la que se encuentra el cliente
    "prob_compra": 80,                                              #Probabilidad de comprar algun item en tienda
    "prob_salir":round(((-1/45)*np.pow(15,2))+((2/3)*15)+15,2),     #Probabilidad de que el cliente salga del mall
    "prob_cambio": 50}                                              #Probabilidad de cambiarse de tienda


def main():
    #Genera data
    while (ext_var.get("num") <= (100 - cliente.get("prob_salir"))):
        #Genera temperatura
        temperatura = round((ext_var.get("temperatura") + (random.randint(-10,11))/10),2)
        if temperatura > 45:
            temperatura = 45
        elif temperatura < -15:
            temperatura = -15
        ext_var["temperatura"] = temperatura

        #Calcula la probabilidad de que el cliente salga
        if temperatura > 45 or temperatura < -15:
            prob_salir = 0
        else:
            prob_salir = round(((-1/45)*np.pow(temperatura,2))+((2/3)*temperatura)+15,2)
        
        cliente["prob_salir"] = prob_salir

        print(f"Temperatura afuera: {temperatura}C")
        print(f"Probabilidad de salir: {abs(prob_salir)}%")

        #Elige una tienda
        tiendas = ext_var.get("tiendas")
        if random.randint(1,100) >= 100 - cliente.get("prob_cambio"):
            temp = random.randint(0,len(tiendas) - 1)
            cliente["tienda_actual"] = tiendas[temp][0]
        print(f"Tienda actual: {cliente.get("tienda_actual")}")

        #Realiza compra
        if cliente.get("tienda_actual") != "Transito":
            if random.randint(1,100) >= 100 - cliente.get("prob_compra"):
                tienda_actual = cliente.get("tienda_actual")
                print(f"{cliente.get("nombre")} realizo compra en tienda {tienda_actual}")
                for i in range(0,len(tiendas)):
                    if tienda_actual == tiendas[i][0]:
                        ext_var["tiendas"][i][1] += 1
        

        ext_var["num"] = random.randint(1,100)
        print(f"Numero: {ext_var.get("num")}")

    
        #time.sleep(1)

    print(f"{cliente.get("nombre")} sale del mall")

    for i in ext_var.get("tiendas"):
        print(f"Nombre Tienda: {i[0]}, Cantidad de ventas: {i[1]}")


if __name__ == '__main__':
    main()