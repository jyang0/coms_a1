def fib(n):
    if n==0:
        return n

    if n==1:
        return n

    return fib(n-1)+fib(n-2)

print(fib(7), end="")
