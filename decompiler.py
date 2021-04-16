import sys

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

class Decompiler:
    def __init__(self, buffer=bytearray([])):
        self.buffer = buffer
        self.cbi = -1
        self.output = ''
    def p(self, d = ''):
        self.output += d + '\n'
    def f(self):
        self.cbi += 1
        return self.buffer[self.cbi]
    def d(self):
        while True:
            try:
                d = self.f()
            except IndexError:
                return self.output
            if d == ISA['mov']:
                r1 = self.f()
                r2 = self.f()
                self.p(f'MOV R{r1+1}, R{r2+1}')
            elif d == ISA['imm']:
                r1 = self.f()
                i2 = self.f()
                self.p(f'IMM R{r1+1}, {i2}')
            elif d == ISA['addrr']:
                r1 = self.f()
                r2 = self.f()
                r3 = self.f()
                self.p(f'ADD R{r1+1}, R{r2+1}, R{r3+1}')