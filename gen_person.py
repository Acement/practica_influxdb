import random,time
import numpy as np

#Variables externas
Tiendas = [['a',0],['b',0],['c',0],['d',0]]
temperatura=15
prob_salir = round(((-1/45)*np.pow(temperatura,2))+((2/3)*temperatura)+15,2)

#Variables de cliente
nombre = "Juan"
tienda_actual = ''
prob_compra = 3
num = 0



while (num <= (100 - prob_salir)):
    temperatura = round((temperatura + (random.randint(-10,11))),2)
    if temperatura > 45:
        temperatura = 45
    elif temperatura < -15:
        temperatura = -15

    if temperatura > 45 or temperatura < -15:
        prob_salir = 0
    else:
        prob_salir = round(((-1/45)*np.pow(temperatura,2))+((2/3)*temperatura)+15,2)
    print(f"Temperatura afuera: {temperatura}C")
    print(f"Probabilidad de salir: {abs(prob_salir)}%")
    tienda_actual = random.choice(Tiendas)

    print(f"Tienda actual: {tienda_actual[0]}")

    num = random.randint(1,100)
    print(f"Numero: {num}")

    
    time.sleep(1)

print(f"{nombre} sale del mall")