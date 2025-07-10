#LOL filname
p = int(input("Give p: "))
g = int(input("Give g: "))
A = int(input("Give A: "))
B = int(input("Give B: "))

def mod_exp(base, exponent, modulus):
    result = 1
    base %= modulus
    while exponent > 0:
        if exponent % 2 == 1:  # If odd exponent
            result = (result * base) % modulus
        exponent //= 2
        base = (base * base) % modulus
    return result

def gen_pvt_key(g, p, pub_key):
    recovered_pvt_key = 0
    if pub_key != g:
        for i in range(1, p+1):
            if mod_exp(g, i, p) == pub_key:
                recovered_pvt_key = i
                break
    else:
        for i in range(2, p+1):
            if mod_exp(g, i, p) == pub_key:
                recovered_pvt_key = i
                break
    return recovered_pvt_key
recovered_a = gen_pvt_key(g, p, A)
recovered_b = gen_pvt_key(g, p, B)

if mod_exp(B, recovered_a, p) == mod_exp(A, recovered_b, p):
    print(f"Successfully Recovered! \na: {recovered_a} \nb: {recovered_b}")
else:
    print(f"Error while calculation, a: {recovered_a}, b: {recovered_b}")
