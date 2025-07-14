from z3 import *

SECRET_VALUE = 315525
MAX_LEN = 28

chars = [BitVec(f'c{i}', 8) for i in range(MAX_LEN)]
solver = Solver()

# Constraint: printable ASCII
for c in chars:
    solver.add(c >= 32, c <= 126)

val = BitVecVal(0, 32)

# Fully signed modeling
for i in range(MAX_LEN):
    c8 = chars[i]
    c = SignExt(24, c8)  # signed char to 32-bit

    idx = BitVecVal(i, 32)
    const_100 = BitVecVal(100, 32)
    const_7 = BitVecVal(7, 32)
    const_i_plus_1 = BitVecVal(i + 1, 32)

    term = (c * c) + (c * (const_100 - idx)) + idx + (c * const_7) + ((c | idx) & (idx + 3))
    term -= SRem(c * c, const_i_plus_1)

    val += term

solver.add(val == SECRET_VALUE)

# Solve
if solver.check() == sat:
    model = solver.model()
    result = ''.join([chr(model[c].as_long()) for c in chars])
    print("[+] Matched input:", result)
else:
    print("[-] No solution found")
