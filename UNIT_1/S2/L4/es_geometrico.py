import math
quadrato = ""
cerchio = ""
rettangolo = ""

a = input("scegli tra queste figure geometriche: \nquadrato\ncerchio\nrettangolo:\n")
if a == "quadrato":
    lato  = input("determina la lunghezza di un lato: ")
    lato = int(lato)
    moltiplicazione = lato*4
    print("il perimetro del quadrato è ")  
    print(moltiplicazione)

if a == "cerchio":
    diametro = input("inserisci il diametro: ")
    diametro = int(diametro)
    circonferenza = math.pi * diametro 
    print("la circonferenza del cerchio è: ") 
    print(circonferenza)

if a == "rettangolo":
    base = input("inserisci la base: ")
    base = int(base)
    lunghezza = input("inserisci la lunghezza: ")
    lunghezza = int(lunghezza)
    calcolo = (base*2) + (lunghezza*2)
    print("il perimetro del rettangolo è : ")
    print(calcolo)

print("programma terminato")
