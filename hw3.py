SAMPLE_PROGRAMS = [
("""
This is a simple program to calcuate the 7th Fibinacci number.
Shows recursion support.
""".strip(),
"""
fib = lambda n:
  if n == 0:
    return n
  if n == 1:
    return n
  return fib(n-1) + fib(n-2)

print(fib(7))
""".strip()
),

("""
This is a simple program to print a square on the screen given a side length!
Shows nested while loop.
""".strip(),
"""
print_square = lambda n:
  i = 0
  while i < n:
    j = 0
    while j < n:
      print(1)
      j += 1
    print()
    i += 1

print_square(4)
""".strip()
),

("""
This program demonstrates the ability to nest lambdas and return a lambda.
Also shows lambda capture feature in the inside lambda.
""".strip(),
"""
make_adder = lambda n:
  adder = lambda a, n:
    return a + n
  return adder

add_two = make_adder(2)
print(add_two(3))
""".strip()
),

("""
This code snippet shows the pure-function requirement: a lambda by default can't access even global variables!
""".strip(),
"""
a = 4
print_a = lambda unused:
  print(a)
print_a(3)
""".strip()
),

("""
This code snippet shows basic expression simplification and dead code elimination (please see generated Python file).
""".strip(),
"""
print_answer = lambda unused:
  dead_var = 1
  s = 3 + 4
  print(s)
print_answer(0)
""".strip()
),

]


if __name__ == '__main__':
    n = 1
    for desc, p in SAMPLE_PROGRAMS:
        print(f'======= Program #{n} =======')
        print(f'Description: {desc}')
        print('Program:')
        print(p)
        print()
        print('Compilation and run output:')
        try:
            from codegen import compile_and_execute
            compile_and_execute(p, n)

        except ValueError as e:
            print(f'Error: {e}')
        print()
        print()
        n += 1
