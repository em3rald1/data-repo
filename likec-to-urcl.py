from optimize_urcl import Optimizer

PRINT_CONST = """.print
\tCAL .sa
\tPOP R1 // char*
\tIMM R2, 0 // i = 0;
\t.print2
\t\tADD R3, R2, R1 // char*[i]
\t\tLOD R3, R3
\t\tBRE .print_end, R3, 0
\t\tOUT %79, R3
\t\tINC R2, R2
\t\tJMP .print2
\t.print_end
\t\tCAL .ra
\t\tRET"""

SAVE_RESTORE_CONST = """.sa
\tSAV R1
\tSAV R2
\tSAV R3
\tSAV R4
\tSAV R5
\tSAV R6
\tSAV R7
\tSAV R8
\tSAV R9
\tSAV R10
\tSAV R11
\tRET
.ra
\tRSR R11
\tRSR R10
\tRSR R9
\tRSR R8
\tRSR R7
\tRSR R6
\tRSR R5
\tRSR R4
\tRSR R3
\tRSR R2
\tRSR R1
\tRET"""

GETS_CONST = """.gets
\tCAL .sa
\tPOP R1 // char* | destination
\tIMM R2, 0
\t.gets2
\t\tIN R3, %79
\t\tADD R4, R2, R1
\t\tBRE .gets_backspace, R3, 8
\t\tBRE .gets_end, R3, 13
\t\tOUT %79, R3
\t\tSTR R4, R3
\t\tINC R2, R2
\t\tJMP .gets2
\t\t.gets_backspace
\t\t\tOUT %79, 8
\t\t\tOUT %79, 0x20
\t\t\tOUT %79, 8
\t\t\tSTR R4, 0
\t\t\tJMP .gets2
\t.gets_end
\t\tCAL .ra
\t\tRET"""

# base data

STD_DATA = [ SAVE_RESTORE_CONST ]
STDIO_FUNCTIONS = [ GETS_CONST, PRINT_CONST ]

STD_TYPES = [
    {
        'type_name': 'int',
        'ref_to': 'lit_raw_val',
        'use_as_addr': True
    },
    {
        'type_name': 'bool',
        'ref_to': 'lit_raw_val',
        'use_as_addr': False,
        'possible_values': [1, 0]
    },
    {
        'type_name': 'int*',
        'ref_to': 'mem_addr',
        'use_as_addr': False,
        'max_value': 0x7fff,
        'min_value': 0x1fff
    },
    {
        'type_name': 'char',
        'ref_to': 'lit_raw_val',
        'use_as_addr': False,
        'max_value': 0xff
    }
]

######################
#
# Syntax:
#   #include <std_library_name>
#   #include "local_file.c"
#   type varName = value;
#   type funcName(type argName) {
#       func2Name(...arguments);
#       return data;
#   };
#   struct {
#       type propertyName;
#       type property2Name;
#   } structName;
#
#   struct structName varName;
#   varName->propertyName = value;
#
######################

SPLIT_CHARS_SAVE = [
    '(', ')', '\n', '[', '.', ']', '{', '}', '#', ';'
]

SPLIT_CHARS_DEL = [
    '\t', '\r'
]

MATH_DOUBLE_POSSIBLE_OPS = [
    '+', '-', '<', '>', '/'
]

MATH_OPS = [
    '+', '-', '>>', '<<', '&', '^', '|', '/', '*', '='
]

STD_TYPES_NAMES = [
    'int', 'char', 'bool'
]

def split(s=''):
    n = ''
    t = []
    st = False
    for c in s:
        if st:
            if c == '"':
                t.append(f'"{n}"')
                n = ''
                st = False
            else:
                n += c
        elif c == ' ':
            if n != '':
                t.append(n)
            n = ''
        elif c in SPLIT_CHARS_SAVE:
            if n != '':
                t.append(n)
            t.append(c)
            n = ''
        elif c in SPLIT_CHARS_DEL:
            if n != '':
                t.append(n)
            n = ''
        elif c == '"':
            st = True
        elif c in MATH_DOUBLE_POSSIBLE_OPS:
            if n == c:
                t.append(c+c)
                n = ''
            elif n != '':
                t.append(n)
                n = c
            else:
                n = c
        elif c == '=':
            if n in MATH_OPS:
                t.append(n+c)
                n = ''
            elif n != '':
                t.append(n)
                n = c
            else:
                n = c
        else:
            if n in MATH_DOUBLE_POSSIBLE_OPS:
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
        self.output1 = 'CAL .main\nHLT\n'
        self.linked_std = SAVE_RESTORE_CONST + '\n'
        self.output2 = ''
        self.linked = []
        self.var_off = 0x400
        self.vars = {}
        self.cf = []
        self.functions = {}
    def f(self):
        self.cci += 1
        return self.tokens[self.cci]
    def p(self, d=''):
        self.output1 += ('\t'*self.cf.__len__()) + d + '\n'
    def p2(self, d=''):
        self.output2 += d + '\n'
    def link(self, lib):
        if lib == ['stdio', '.', 'h']:
            if not lib in self.linked:
                self.linked_std += STDIO_FUNCTIONS[0] + '\n' + STDIO_FUNCTIONS[1]
                self.linked.append('stdio')
                self.functions['print'] = ['char*']
                self.functions['gets'] = ['char*']
    def c(self):
        while True:
            try:
                d = self.f()
            except IndexError:
                break
            if d == '#': # pragma
                pragma = self.f()
                if pragma == 'include':
                    if self.f() == '<':
                        data = []
                        lib = self.f()
                        while lib != '>':
                            data.append(lib)
                            lib = self.f()
                        self.link(data)
            elif d == 'int': # typed variable assignment start
                varName = self.f()
                if varName.isascii() and not varName.isnumeric():
                    eqs = self.f()
                    if eqs == '=':
                        data = []
                        d1 = self.f()
                        while d1 != ';':
                            data.append(d1)
                            d1 = self.f()
                        if len(data): # simple assignment
                            if data[0].isnumeric():
                                self.vars[varName] = [d, self.var_off]
                                self.p(f'STR {self.var_off}, {data[0]}')
                                self.var_off += 1
                            else:
                                self.vars[varName] = [d, self.var_off]
                                self.p(f'LOD R1, {self.vars[data[0]][1]}')
                                self.p(f'STR {self.var_off}, R1')
                                self.var_off += 1
                        else:
                            pass # TODO
                    elif eqs == ';':
                        self.vars[varName] = [d, self.var_off]
                        self.var_off += 1
                    elif eqs == '(': # function assignment
                        args = []
                        t1 = self.f()
                        d1 = self.f()
                        while not (d1 == ')' or t1 == ')'):
                            args.append([t1, d1])
                            t1 = self.f()
                            d1 = self.f()
                        self.p(f'.{varName}')
                        for arg in args[::-1]:
                            self.vars[arg[1]] = [arg[0], self.var_off]
                            self.p('POP R1')
                            self.p(f'STR {self.var_off}, R1')
                        self.cf.append(varName)
            elif d == 'return':
                data = []
                d1 = self.f()
                while d1 != ';':
                    data.append(d1)
                    d1 = self.f()
                if len(data) == 1: # simple return
                    if data[0].isnumeric():
                        self.p(f'PSH {data[0]}')
                        self.p('RET')
                    else:
                        self.p(f'LOD R1, {self.vars[data[0]][1]}')
                        self.p(f'PSH R1')
                        self.p('RET')
                    self.cf.pop()
            elif d == 'char*':
                varName = self.f()
                if varName.isascii() and not varName.isnumeric():
                    eqs = self.f()
                    if eqs == '=':
                        data = []
                        d1 = self.f()
                        while d1 != ';':
                            data.append(d1)
                            d1 = self.f()
                        if data[0].startswith('"') and data[0].endswith('"'):
                            # string
                            self.vars[varName] = ['char*', self.var_off]
                            self.p2(f'.str_{varName}')
                            self.p2(f'\tDW {data[0]}')
                            self.p2(f'\tDW 0')
                            self.p(f'STR {self.var_off}, .str_{varName}')
                            self.var_off += 1
            elif d in self.functions:
                opb = self.f()
                if opb == '(':
                    args = []
                    d1 = self.f()
                    while d1 != ')':
                        args.append(d1)
                        d1 = self.f()
                    args = args[::-1]
                    for arg in args:
                        if arg.isnumeric():
                            self.p(f'PSH {arg}')
                        else:
                            self.p(f'LOD R1, {self.vars[arg][1]}')
                            self.p(f'PSH R1')
                    self.p(f'CAL .{d}')
                        
        return self.output1 + self.output2 + self.linked_std

import sys # sus
data = open(sys.argv[1], 'r').read()
c = Compiler(data)
print(c.c())
print(c.tokens)
print(Optimizer(c.c()).Optimize())

open(sys.argv[2], 'w').write(Optimizer(c.c()).Optimize())