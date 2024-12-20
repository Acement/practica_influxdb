import random,time
import numpy as np

#Variables externas
Tiendas = [['a',0],['b',0],['c',0],['d',0]]
temperatura=15
prob_salir = round(((-1/45)*np.pow(temperatura,2))+((2/3)*temperatura)+15,2)

#Variables de cliente
nombre = "Juan"
tienda_actual = ''
prob_compra = 30
num = 0


#Genera data
while (num <= (100 - prob_salir)):
    #Genera temperatura
    temperatura = round((temperatura + (random.randint(-10,11))/10),2)
    if temperatura > 45:
        temperatura = 45
    elif temperatura < -15:
        temperatura = -15

    #Calcula la probabilidad de que el cliente salga
    if temperatura > 45 or temperatura < -15:
        prob_salir = 0
    else:
        prob_salir = round(((-1/45)*np.pow(temperatura,2))+((2/3)*temperatura)+15,2)
    print(f"Temperatura afuera: {temperatura}C")
    print(f"Probabilidad de salir: {abs(prob_salir)}%")

    #Elige una tienda
    temp = random.randint(0, len(Tiendas)-1)
    print(f"Tienda actual: {Tiendas[temp][0]}")

    #Realiza compra
    if random.randint(1,100) >= 100 - prob_compra:
        print(f"{nombre} realizo compra en tienda {Tiendas[temp][0]}")
        Tiendas[temp][1] += 1
        

    num = random.randint(1,100)
    print(f"Numero: {num}")

    
    #time.sleep(1)

print(f"{nombre} sale del mall")

for i in Tiendas:
    print(f"Nombre Tienda: {i[0]}, Cantidad de ventas: {i[1]}")