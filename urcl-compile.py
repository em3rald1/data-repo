ISA = {
    'addrr': 0,
    'addir': 1,
    'addii': 2,
    'subrr': 3,
    'subir': 4,
    'subii': 5,
    'subri': 100,
    'rshr': 6,
    'rshl': 7,
    'lshr': 8,
    'lshl': 9,
    'incr': 10,
    'incl': 11,
    'decr': 12,
    'decl': 13,
    'xorrr': 14,
    'xorlr': 15,
    'xorll': 16,
    'orrr': 17,
    'orlr': 18,
    'orll': 19,
    'andrr': 20,
    'andlr': 21,
    'andll': 22,
    'notr': 23,
    'notl': 24,
    'mov': 25,
    'imm': 26,
    'lodr': 27,
    'lodl': 28,
    'stral': 29,
    'strar': 30,
    'strrl': 31,
    'strrr': 32,

    'brar': 33,
    'bral': 34,

    'brcr': 35,
    'brcl': 36,

    'bncr': 37,
    'bncl': 38,

    'brzr': 39,
    'brzl': 40,

    'bnzr': 41,
    'bnzl': 42,

    'nop': 43,
    'hlt': 44,
    'pshl': 45,
    'pshr': 46,
    'pop': 47,

    'calr': 48,
    'call': 49,

    'ret': 50,

    'sav': 51,
    'rsr': 52,

    'in': 53,
    'outr': 54,
    'outl': 55,

    'mltrr': 60,
    'mltlr': 61,
    'mltll': 62,
    'divrr': 63,
    'divlr': 64,
    'divrl': 65,
    'divll': 66,
    'modrr': 67,
    'modlr': 68,
    'modrl': 69,
    'modll': 70,

    'brllrr': 71,
    'brllrl': 72,
    'brlllr': 73,
    'brlrrr': 74,
    'brlrrl': 75,
    'brlrlr': 76,
    'brglrr': 77,
    'brglrl': 78,
    'brgllr': 79,
    'brgrrr': 80,
    'brgrrl': 81,
    'brgrlr': 82,
    'brelrr': 83,
    'brelrl': 84,
    'brerrr': 85,
    'brerrl': 86,
    'bnelrr': 87,
    'bnelrl': 88,
    'bnerrr': 89,
    'bnerrl': 90,
}

def split(d):
    n = ''
    t = []
    for c in d:
        if c == ' ' or c == '\t':
            if n != '':
                t.append(n)
            n = ''
        elif c == '\n':
            if n != '':
                t.append(n)
            t.append('\n')
            n = ''
        elif c == '/':
            if n == '/':
                t.append('//')
                n = ''
            elif n != '':
                t.append(n)
                n = '/'
            elif n == '':
                n = '/'
        else:
            if n == '/':
                t.append(n)
                n = ''
            n += c
    if n != '':
        t.append(n)
    return t

def utilize_comments(tokens):
    cci = -1
    nt = []
    while True:
        try:
            cci += 1
            d = tokens[cci]
        except IndexError:
            return nt 
        if d == "'":
            cci += 1
            d = tokens[cci]
            ns = ''
            ns += d
            while d != "'":
                cci += 1
                d = tokens[cci]
                ns += d
            nt.append(ns)
        elif d == '"':
            cci += 1
            d = tokens[cci]
            ns = ''
            ns += d
            while d != '"':
                cci += 1
                d = tokens[cci]
                ns += d
            nt.append(ns)
        elif d.startswith('"'):
            if d.endswith('"'):
                nt.append(d)
            else:
                cci += 1
                d2 = tokens[cci]
                while not d2.endswith('"'):
                    d += " " +d2
                    cci += 1
                    d2 = tokens[cci]
                d += " " + d2
                nt.append(d)
            
        elif d == '//':
            while d != '\n':

                try:
                    cci += 1
                    d = tokens[cci]
                except IndexError:
                    return nt
        else:
            nt.append(d)

def utilize_commas(tokens):
    t = []
    for i in tokens:
        #print(i)
        if (not i.startswith('"') and not i.endswith('"')) and (not i.startswith("'") and not i.endswith("'")):
            t.append(i.replace(',',''))
        else:
            t.append(i)
    return t

def ic(s=''):
    # converts word to integer in multiple ways
    if s.startswith('0x'):
        print(f'REQ HEX {s}, OUT: {int(s[2:], 16)}')
        return int(s[2:], 16)
    elif s.startswith('0b'):
        print(f'REQ BIN {s}, OUT: {int(s[2:], 2)}')
        return int(s[2:], 2)
    elif s.startswith('.'):
        print(f'REQ LABEL {s}, OUT: {s}')
        return s
    elif s.isdecimal():
        print(f'REQ DEC {s}, OUT: {int(s)}')
        return int(s)
    elif s.startswith('R') or s.startswith('$'):
        print(f'REQ REG {s}, OUT: {int(s[1:])-1}')
        return int(s[1:])-1
    elif s.startswith('\'') and s.endswith('\''):
        print(f'REQ CHAR {s}, OUT: {ord(s[1:-1])}')
        return ord(s[1:-1])
    else:
        return False

def reg(s=''):  return s.startswith('R') or s.startswith('$')
def lab(s=''):  return s.startswith('.')
def hex_(s=''):  return s.startswith('0x')
def bin_(s=''):  return s.startswith('0b')
def cha(s=''):  return s.startswith('\'') and s.endswith('\'') and len(s) == 3
def dec(s=''):  return s.isdecimal() or hex_(s) or bin_(s) or cha(s) or lab(s)

class NCompiler:
    def __init__(self, code, library=False):
        self.code = code
        self.tokens = utilize_commas(utilize_comments(split(code)))
        self.cci = -1
        self.cti = 0
        self.cl = library
        self.labels = {}
        self.output = [0]*65565
    def clo(self):
        nd = self.output[::-1]
        i = 0
        while nd[i] == 0:
            i += 1
        self.output = nd[i-8:][::-1]
    def po(self):
        nd = []
        for i in self.output:
            if type(i) == str:
                i = str(i)
                if i.startswith('.'):
                    nd.append(self.labels[i[1:]])
            else:
                nd.append(i)
        self.output = nd
    def f(self):
        self.cci+= 1
        return self.tokens[self.cci]
    def include(self, file):
        d1 = utilize_commas(utilize_comments(split(open(file, 'r').read())))
        self.tokens += d1
    def p(self, d):
        self.output[self.cti] = d
        self.cti += 1
    def c(self):
        if not self.cl:
            while True:
                try:
                    d = self.f()
                except IndexError:
                    self.po()
                    self.clo()
                    return self.output
                print(d) if d != '\n' else None
                if d == 'INCLUDE':
                    self.include(self.f()[1:-1])
                elif d == 'MOV':
                    de = self.f()
                    d1 = self.f()
                    if reg(de) and reg(d1):
                        self.p(ISA['mov'])
                        self.p(ic(de))
                        self.p(ic(d1))
                elif d == 'IMM':
                    de = self.f()
                    d1 = self.f()
                    #print(de, d1)
                    if dec(d1) and reg(de):
                        print('e')
                        self.p(ISA['imm'])
                        self.p(ic(de))
                        self.p(ic(d1))
                        #print(self.output)
                elif d.startswith('.'):
                    self.labels[d[1:]] = self.cti
                elif d == 'HLT':
                    self.p(ISA['hlt'])
                elif d == 'ADD':
                    de = self.f()
                    d1 = self.f()
                    d2 = self.f()
                    print(de, d1, d2)
                    if reg(d1) and reg(d2):
                        self.p(ISA['addrr'])
                        self.p(ic(de))
                        self.p(ic(d1))
                        self.p(ic(d2))
                    elif dec(d1) and reg(d2):
                        self.p(ISA['addir'])
                        self.p(ic(de))
                        self.p(ic(d1))
                        self.p(ic(d2))
                    elif reg(d1) and dec(d2):
                        self.p(ISA['addir'])
                        self.p(ic(de))
                        self.p(ic(d2))
                        self.p(ic(d1))
                        print('done add')
                elif d == 'SUB':
                    de = self.f()
                    d1 = self.f()
                    d2 = self.f()
                    print(de, d1, d2)
                    if reg(d1) and reg(d2):
                        self.p(ISA['subrr'])
                        self.p(ic(de))
                        self.p(ic(d1))
                        self.p(ic(d2))
                    elif dec(d1) and reg(d2):
                        self.p(ISA['subir'])
                        self.p(ic(de))
                        self.p(ic(d1))
                        self.p(ic(d2))
                    elif reg(d1) and dec(d2):
                        self.p(ISA['subri'])
                        self.p(ic(de))
                        self.p(ic(d1))
                        self.p(ic(d2))
                        print('done sub')
                

def convert_to_BE(o):
    no = []
    for i in o:
        no.append(i & 0xff)
        no.append((i >> 8) & 0xff)
    return no

def convert_to_str(o):
    stro = b''
    for i in o:
        stro += bytes([i])
    return stro
                

import sys
data = open(sys.argv[1], 'r').read()
ca = NCompiler(data)
out = ca.c()
print(out)
print(convert_to_BE(out))
print(bytes(convert_to_BE(out)))
dat = convert_to_BE(out)
o = bytearray(dat.__len__())
k = 0
while True:
    if k == dat.__len__(): break
    o[k] = convert_to_BE(out)[k]
    #print(dat[k])
    k += 1

print(o)
open(sys.argv[2], 'wb+').write(o)