def int2base(x, base=2):
    if x < 0:
        sign = -1
    elif x == 0:
        return '0'  # digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[x % base])
        x = x // base

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)
