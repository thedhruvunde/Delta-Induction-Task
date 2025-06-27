import getpass
from multiprocessing.resource_tracker import getfd

def mod_exp(base, exponent, modulus):
    result = 1
    base %= modulus
    while exponent > 0:
        if exponent % 2 == 1:  # If odd exponent
            result = (result * base) % modulus
        exponent //= 2
        base = (base * base) % modulus
    return result


p = int(input("Set Public Parameter p: "))
for i in range(2,p):
    if p%i == 0:
        print("Not Valid Input, Number Should be a Prime!")
        exit()
    else:
        pass
g = int(input("Set Public Parameter g: "))

print(f"Public parameters:\n  Prime (p): {p}\n  Generator (g): {g}\n")

a = int(getpass.getpass("Set parameter a: "))
A = mod_exp(g, a, p)
b = int(getpass.getpass("Set parameter b: "))
B = mod_exp(g, b, p)

print(f"public key (A): {A}\n")

print(f"public key (B): {B}\n")

shared_secret_a = mod_exp(B, a, p)
shared_secret_b = mod_exp(A, b, p)

print(f"Shared secret computed by A: {shared_secret_a}")
print(f"Shared secret computed by B:   {shared_secret_b}")

if shared_secret_a == shared_secret_b:
    print("\nKey exchange successful. Shared secret matches.")
else:
    print("\nKey exchange failed. Shared secrets do not match.")
