def make_adder(n):
    def adder(a):
        return a+n

    return adder

add_two=make_adder(2)
print(add_two(3), end="")
