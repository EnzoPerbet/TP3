def addition(a, b):
    return a + b

def soustraction(a, b):
    return a - b

def multiplication(a, b):
    return a * b

def division(a, b):
    if b == 0:
        raise ValueError("Division par zéro impossible")
    return a / b

def puissance(a, b):
    return a ** b

def modulo(a, b):
    if b == 0:
        raise ValueError("Modulo par zéro impossible")
    return a % b

def calcul_complexe(a, b):
    return puissance(a, b) + 10
