C_SET_DEL = [
    ',', ';', '\t', '\r'
]

C_SET_SAVE = [
    '(', ')', '.', '%', '\n'
]

def split(s=''):
    n = ''
    t = []
    ins = False
    for c in s:
        if ins and not c == '"':
            n += c
        elif c == '"':
            if ins:
                t.append('"'+n+'"')
                n = ''
            ins = not ins
        elif c == ' ':
            if n != '':
                t.append(n)
            n = ''
        elif c in C_SET_DEL:
            if n != '':
                t.append(n)
            n = ''
        elif c in C_SET_SAVE:
            if n != '':
                t.append(n)
            t.append(c)
            n = ''
        elif c == '/':
            if n != '':
                t.append(n)
            n = c
        else:
            n += c
    if n != '':
        t.append(n)
    return t

class Compiler:
    def __init__(self, code=''):
        self.code = code
        self.tokens = split(code)
        self.cci = -1
        self.output = ''
    def p(self, d=''):
        self.output += d + '\n'
    def p2(self, d=''):
        self.output += d
    def f(self):
        self.cci += 1
        return self.tokens[self.cci]
    def c(self):
        while True:
            try:
                d = self.f()
            except IndexError:
                return self.output
            if d.startswith('//'):
                while self.f() != '\n':
                    pass
            if d == 'CAL':
                dot = self.f()
                if dot == '.':
                    label = self.f()
                    opb = self.f()
                    if opb == '(':
                        args = []
                        d1 = self.f()
                        while d1 != ')':
                            args.append(d1)
                            d1 = self.f()
                        for arg in args[::-1]:
                            if arg.startswith('R') or arg.startswith('$'):
                                self.p(f'PSH {arg}')
                            elif arg.isnumeric():
                                self.p(f'PSH {arg}')
                        self.p(f'CAL .{label}')
                    else:
                        self.cci -= 1
                        self.p(f'CAL .{label}')
            elif d == 'NAME':
                label = self.f()
                self.p(f'.{label}')
            elif d == 'ARGS':
                count = int(self.f())
                for i in range(count):
                    self.p(f'POP R{i+1}')
            elif d != '\n':
                self.p2(d + " ")
            elif d == '\n':
                self.p('\n')

data = """CAL .func1(5, 4)
HLT
NAME func1
ARGS 2
ADD R4, R1, R2
RET"""

print(Compiler(data).c())