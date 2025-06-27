from z3 import *

SECRET_VALUE = 315525
MAX_LEN = 30

# Create symbolic characters
chars = [BitVec(f'c{i}', 8) for i in range(MAX_LEN)]
solver = Solver()

val = 0
for i in range(MAX_LEN):
    c = chars[i]

    # Constrain to printable ASCII (excluding newline)
    solver.add(c >= ord('a'), c <= ord('z'))
    solver.add(c >= ord('A'), c <= ord('Z'))

    term = ((c * c) + (c * (100 - i)) + i + (c * 7) + ((c | i) & (i + 3)))
    term -= ((c * c) % (i + 1))
    val += term

# Target value condition
solver.add(val == SECRET_VALUE)

if solver.check() == sat:
    model = solver.model()
    result = ''.join([chr(model[c].as_long()) for c in chars])
    print("Valid input string:", result)
else:
    print("No solution found.")
