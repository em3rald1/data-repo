INSTRUCTIONS_DEL = [
    'IMM', 'MOV', 'POP'
]

ONE_OP_INSTRUCTIONS_REPLACE_IMM = [
    'PSH'
]

ONE_OP_INSTRUCTIONS_DEL_IMM = [
    'POP', 'RSR', 'IN'
]

def split(s=''):
    return s.splitlines()

class Optimizer:
    def __init__(self, code=''):
        self.code = code
        self.lines = code.splitlines()
        self.cli = -1
        self.output = ''
    def f(self):
        self.cli += 1
        return self.lines[self.cli]
    def p(self, d=''):
        self.output += d + '\n'
    def Optimize(self):
        while True:
            try:
                d = self.f()
            except IndexError:
                return self.output
            if d:
                if d.split()[0] in INSTRUCTIONS_DEL:
                    r1 = d.split()[1].replace(',','')
                    nd = self.f()
                    if nd.split()[0] in ONE_OP_INSTRUCTIONS_REPLACE_IMM:
                        r2 = nd.split()[1].replace(',','')
                        if r1 == r2:
                            self.p(f'PSH {d.split()[2]}')
                        else:
                            self.p(d)
                            self.p(nd)
                    elif nd.split()[0] in ONE_OP_INSTRUCTIONS_DEL_IMM:
                        r2 = nd.split()[1].replace(',', '')
                        if r1 == r2:
                            self.p(nd)
                        else:
                            self.p(d)
                            self.p(nd)
                else:
                    self.p(d)

print(Optimizer('MOV R1, R2\nIN R1, %79').Optimize())