E = 2.718282
PI = 3.141593

def power(x, y):
    if y == 0:
        return 1
    temp = power(x, y/2)
    if y%2 == 0:
        return temp*temp
    return x*temp*temp

def sqrt(x):
    # ref: https://en.wikipedia.org/wiki/Methods_of_computing_square_roots#Babylonian_method
    temp = 0
    rs = (x+1)/2
    while temp!=rs:
        temp = rs
        rs = (rs+x/rs)/2
    return rs

def factorial(n):
    if n < 1:
        return 1
    else:
        return n * factorial(n-1)

def convert(degree):
    pi = 3.141592653589793238462643383279
    radian = degree*(pi/180)
    return radian

def sin(x):
    sin_approx = 0
    for n in range(20):
        coef = (-1) ** n
        num = x ** (2 * n + 1)
        denom = factorial(2 * n + 1)
        sin_approx += ((coef) / (denom)) * (num)

    return sin_approx

def cos(x):
    cos_approx = 0
    for n in range(20):
        coef = (-1) ** n
        num = x ** (2 * n)
        denom = factorial(2 * n)
        cos_approx += ((coef) / (denom)) * (num)

    return cos_approx

def tan(x):
    tan = (sin(x)) / (cos(x))
    return tan

def abs(a):
    return -a if a <0 else a
