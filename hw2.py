SAMPLE_PROGRAMS = [
("""
This is a simple program to calcuate the nth Fibinacci number.
""".strip(),
"""
fib = lambda n, unused:
  if n == 0:
    return n
  if n == 1:
    return n
  return fib(n-1, 0) + fib(n-2, 0)

print(fib(5, 1))
""".strip()
),

("""
This is a simple program to print a square on the screen given a side length!
""".strip(),
"""
print_square = lambda n:
  i = 0
  while i < n:
    j = 0
    while j < n:
      print(1)
      j += 1
    i += 1

print_square(4)
""".strip()
),

("""
This program demonstrates the abillity to nest lambdas.
""".strip(),
"""
make_adder = lambda n:
  adder = lambda a:
    return a + n
  return adder

add_two = make_adder(2)
print(add_two(3))
""".strip()
),

("""
This code snippet shows error handling when we forget to close parenthesis in func call:
""".strip(),
"""
p = lambda n:
  return p + 1
p(4
""".strip()
),

("""
This code snippet shows error handling if we tried to put an expression as a lambda arg:
""".strip(),
"""
p = lambda p + 4:
  return p + 1
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
        print('Tree:')
        try:
            from parser import parse_S, preprocess_tokens, clean_and_flatten_tree, print_node_tree
            import tokenizer
            t = tokenizer.tokenize(p)
            p = preprocess_tokens(t)
            result = parse_S(p, 0)
            if result.next_i != len(p):
                raise ValueError('ERROR did not reach end')
            flat_result = clean_and_flatten_tree(result.node)
            print_node_tree(flat_result, 0)

        except ValueError as e:
            print(f'Error encountered during parsing: {e}')
        print()
        print()
        n += 1
