import tokenizer


SAMPLE_PROGRAMS = [
(
'This program prints the 5th fibonacci number. Spaces are counted, since Python also cares about whitespace.',
'''
fib = lambda n:
  if n == 0 or n == 1:
    return n
  return fib(n-1) + fib(n-2)

print(fib(5))
'''),

(
'This program shows a parsing error from an invalid variable/identifier name:',
'''
my_str = 'abcd'
my_bad_$_str_name = 'def'
print(my_bad_$_str_name)
'''),

(
'This program shows a parsing error from an unrecognized operator:',
'''
my_str = !'abcd'
print(my_str)
'''),

(
'This program prints a square of size n:',
'''
print_square = lambda n:
  for i in range(n):
    for j in range(n):
      print('*')
print_square(4)
'''),

(
'This program runs forever!',
'''
i = 0
while i == 0:
  i = i * 2
'''),
]

if __name__ == '__main__':
    n = 1
    for desc, p in SAMPLE_PROGRAMS:
        print(f'======= Program #{n} =======')
        print(f'Description: {desc}')
        print('Program:')
        print(p)
        print()
        print('Tokens:')
        try:
            t = tokenizer.tokenize(p)
            for tt in t:
                print(f'  {tt}')
        except ValueError as e:
            print(f'Error encountered during parsing: {e}')
        print()
        print()
        n += 1
