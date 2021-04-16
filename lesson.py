from math import pi

def calcDiameter(s):
    # S = 2*pi*Radius = pi*Diameter
    return s/pi

def calcRadius(s):
    return (s/pi)/2

def calcLengthByRadius(r):
    return 2*r*pi

def calcLengthByDiameter(d):
    return d*pi

if __name__ == '__main__':
    args = input('$ ')
    if not args:
        exit(1)
    else:
        print('Length of circle if value is radius (R): ', calcLengthByRadius(float(args)))
        print('Length of circle if value is diameter (d): ', calcLengthByDiameter(float(args)))
        print('Radius/Diameter if value is length of circle (C): ', calcRadius(float(args)), '/', calcDiameter(float(args)))