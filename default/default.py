PI = 3.141592653589793238462643383279
E = 2.718282

def POWER(x, y: int):
    if x == 0:
        return 0
    if y == 0:
        return 1
    temp = POWER(x, int(y/2))
    if y%2 == 0:
        return temp*temp
    return x*temp*temp

def SQRT(x):
    # ref: https://en.wikipedia.org/wiki/Methods_of_computing_square_roots#Babylonian_method
    if x < 0:
        return 0
    temp = 0
    rs = (x+1)/2
    while temp!=rs:
        temp = rs
        rs = (rs+x/rs)/2
    return rs

def FACTORIAL(n):
    return 1 if n < 1 else n * FACTORIAL(n-1)

def DEGREE2RAD(degree):
    return degree*(PI/180)

def SIN(x):
    sin_approx = 0
    for n in range(20):
        coef = POWER(-1, n)
        num = POWER(x, 2 * n + 1)
        denom = FACTORIAL(2 * n + 1)
        sin_approx += (coef / denom) * num
    return sin_approx

def COS(x):
    cos_approx = 0
    for n in range(20):
        coef = POWER(-1, n)
        num = POWER(x, 2 * n)
        denom = FACTORIAL(2 * n)
        cos_approx += (coef / denom) * num
    return cos_approx

def TAN(x):
    return SIN(x) / COS(x)

def ABS(a):
    return -a if a <0 else a
