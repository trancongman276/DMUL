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

def sin(x):
    # rs = 1
    # if (x>360) x-=360
    # if (x<0) x+=360

    # if (x==180 || x==0)
    #     return 0

    # if (x > 270) rs = -1
    # else if (x > 180){
    #     x -= 180
    #     rs = -1
    # }
    # elif (x > 90) x = 180 - x
    pass

def cos(x):
    pass

def tan(x):
    pass

def abs(a):
    return -a if a <0 else a
