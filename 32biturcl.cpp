#include <iostream>
#include <vector>
#include <fstream>
#include "is.h"
#if defined(_WIN32) || defined(WIN32)
#include <conio.h>
#else
#include <unistd.h>
#include <termios.h>
int getch()
{
    int ch;
    struct termios oldt, newt;
    tcgetattr( STDIN_FILENO, &oldt );
    newt = oldt;
    newt.c_lflag &= ~( ICANON | ECHO );
    tcsetattr( STDIN_FILENO, TCSANOW, &newt );
    ch = getchar();
    tcsetattr( STDIN_FILENO, TCSANOW, &oldt );
    return ch;
}
#endif

using std::vector;
using std::cin;
using std::cout;

typedef unsigned long long u64;
typedef unsigned long u32;
typedef unsigned short u16;
typedef unsigned char u8;
typedef bool u1;

class emu32 
{
    public:
        vector<u32> memory;
        vector<u32> _ports;
        vector<u32> registers;
        u64 rip;
        u1 z, c, n;
        emu32() 
        {
            memory.reserve(0xfffff);
            _ports.reserve(0xff);
            registers.reserve(0xff);
            for(int i = 0; i < 0xff; i++)
            {
                _ports[i] = 0;
                registers[i] = 0;
            }
            for(int i = 0; i < 0xfffff) memory[i] = 0;
            rip = 0;
            z = 1;
            c = 0;
            n = 0;
        }
        u32 fetch() {
            return memory[rip++];
        }
        void uf(u64 d) {
            if (d == 0) z = 1; // ZERO
            if (d > UINT32_MAX) c = 1; // OVERFLOW
            if (d > 0b10000000000000000000000000000000) n = 1; // SIGN BIT
        }
        void push(u32 d) {
            memory[registers[0xff-3]] = d;
            registers[0xff-3]--;
        }
        u32 pull() {
            registers[0xff-3]++;
            return memory[registers[0xff-3]];
        }

        void save(u32 r) {
            memory[registers[0xff-2]] = registers[r];
            registers[0xff-2]--;
        }
        void restore(u32 r) {
            registers[0xff-2]++;
            registers[r] = memory[registers[0xff-2]];
        }

        void call(u32 d) {
            memory[registers[0xff-1]] = rip;
            registers[0xff-1]--;
            rip = d;
        }
        void retr() {
            registers[0xff-1]++;
            rip = memory[registers[0xff-1]];
        }

        bool step() {
            u1 res = 0;
            u32 i = fetch();
            switch (i)
            {
                case addrr: {
                    u32& d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1 + o2;
                    uf(o1+o2);
                    break;
                }
                case addrl: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1 + o2;
                    uf(o1+o2);
                    break;
                }

                case subrr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1 - o2;
                    uf(o1-o2);
                    break;
                }
                case subrl: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1 - o2;
                    uf(o1-o2);
                    break;
                }
                case sublr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = fetch();
                    u32 o2 = registers[fetch()];
                    d = o1 - o2;
                    uf(o1-o2);
                    break;
                }

                case rsh: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    d = o1 >> 1;
                    uf(o1>>1);
                    break;
                }
                case lsh: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    d = o1 << 1;
                    uf(o1<<1);
                    break;
                }

                case inc: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    d = o1+1;
                    uf(o1+1);
                    break;
                }
                case dec: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    d = o1-1;
                    uf(o1-1);
                    break;
                }

                case xorrr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1^o2;
                    uf(o1^o2);
                    break;
                }
                case xorrl: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1^o2;
                    uf(o1^o2);
                    break;
                }
                case orrr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1|o2;
                    uf(o1|o2);
                    break;
                }
                case orrl: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1|o2;
                    uf(o1|o2);
                    break;
                }
                case andrr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1&o2;
                    uf(o1&o2);
                    break;
                }
                case andrl: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1&o2;
                    uf(o1&o2);
                    break;
                }

                case mltrr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1*o2;
                    uf(o1*o2);
                    break;
                }
                case mltrl:
                {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1*o2;
                    uf(o1*o2);
                    break;
                }

                case divrr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1/o2;
                    uf(o1/o2);
                    break;
                }
                case divrl: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1/o2;
                    uf(o1/o2);
                    break;
                }
                case divlr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = fetch();
                    u32 o2 = registers[fetch()];
                    d = o1/o2;
                    uf(o1/o2);
                    break;
                }

                case modrr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1%o2;
                    uf(o1%o2);
                    break;
                }
                case modrl: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1%o2;
                    uf(o1%o2);
                    break;
                }
                case modlr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = fetch();
                    u32 o2 = registers[fetch()];
                    d = o1%o2;
                    uf(o1%o2);
                    break;
                }

                case imm: {
                    u32 &d = registers[fetch()];
                    d = fetch();
                    break;
                }
                case mov: {
                    u32 &d = registers[fetch()];
                    d = registers[fetch()];
                    break;
                }

                case lodl: {
                    u32 &d = registers[fetch()];
                    d = memory[fetch()];
                    break;
                }
                case lodr: {
                    u32 &d = registers[fetch()];
                    d = memory[registers[fetch()]];
                    break;
                }

                case stral: {
                    u32 &d = memory[fetch()];
                    d = fetch();
                    break;
                }
                case strar: {
                    u32 &d = memory[fetch()];
                    d = registers[fetch()];
                    break;
                }
                case strrl: {
                    u32 &d = memory[registers[fetch()]];
                    d = fetch();
                    break;
                }
                case strrr: {
                    u32 &d = memory[registers[fetch()]];
                    d = registers[fetch()];
                    break;
                }

                case pshr: {
                    push(registers[fetch()]);
                    break;
                }
                case pshl: {
                    push(fetch());
                    break;
                }

                case pop: {
                    registers[fetch()] = pull();
                    break;
                }

                case sav: {
                    save(fetch());
                    break;
                }
                case rsr: {
                    restore(fetch());
                    break;
                }

                case jmpl: {
                    rip = fetch();
                    break;
                }
                case jmpr: {
                    rip = registers[fetch()];
                    break;
                }
                
                case brcl: {
                    u32 d = fetch();
                    if(c) rip = d;
                    break;
                }
                case brcr: {
                    u32 d = registers[fetch()];
                    if(c) rip = d;
                    break;
                }

                case bncl: {
                    u32 d = fetch();
                    if(!c) rip = d;
                    break;
                }
                case bncr: {
                    u32 d = registers[fetch()];
                    if(!c) rip = d;
                    break;
                }

                case brzl: {
                    u32 d = fetch();
                    if(z) rip = d;
                    break;
                }
                case brzr: {
                    u32 d = registers[fetch()];
                    if(z) rip = d;
                    break;
                }

                case bnzl: {
                    u32 d = fetch();
                    if(!z) rip = d;
                    break;
                }
                case bnzr: {
                    u32 d = registers[fetch()];
                    if(!z) rip = d;
                    break;
                }

                case brpl: {
                    u32 d = fetch();
                    if(!n) rip = d;
                    break;
                }
                case brpr: {
                    u32 d = registers[fetch()];
                    if(!n) rip = d;
                    break;
                }

                case brnl: {
                    u32 d = fetch();
                    if(n) rip = d;
                    break;
                }
                case brnr: {
                    u32 d = registers[fetch()];
                    if(n) rip = d;
                    break;
                }

                case cmprr: {
                    uf(registers[fetch()]-registers[fetch()]);
                    break;
                }
                case cmprl: {
                    uf(registers[fetch()]-fetch());
                    break;
                }
                case cmplr: {
                    uf(fetch()-registers[fetch()]);
                    break;
                }

                case cali: {
                    call(fetch());
                    break;
                }
                case calr: {
                    call(registers[fetch()]);
                    break;
                }
                case ret: {
                    retr();
                    break;
                }

                case hlt: {
                    res = 1;
                    break;
                }

                case in: {
                    u32 &r = registers[fetch()];
                    u32 p = fetch();
                    if(p == 78) {
                        // input from keyboard
                        _ports[p] = getch();
                    }
                    r = _ports[p];
                    break;
                }
                case outr: {
                    u32 r = registers[fetch()];
                    u32 p = fetch();
                    if(p == 78) {
                        std::cerr << r;
                    }
                    _ports[p] = r;
                    break;
                }
                case outl: {
                    u32 r = fetch();
                    u32 p = fetch();
                    if(p == 78) {
                        std::cerr << r;
                    }
                    _ports[p] = r;
                    break;
                }

                case bsll: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1 << o2;
                    uf(o1 << o2);
                    break;
                }
                case bslr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1 << o2;
                    uf(o1 << o2);
                    break;
                }

                case bsrl: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = fetch();
                    d = o1 >> o2;
                    uf(o1 >> o2);
                    break;
                }
                case bsrr: {
                    u32 &d = registers[fetch()];
                    u32 o1 = registers[fetch()];
                    u32 o2 = registers[fetch()];
                    d = o1 >> o2;
                    uf(o1 >> o2);
                    break;
                }
            }
            return res;
        }

        void loadMemory(vector<u8> data) {
            std::ifstream data(fn, std::ios::binary);
            vector<u8> readData(std::istreambuf_iterator<char>(data), {});
            u32 *dataPtr = reinterpret_cast<u32 *>(readData.data());
            std::vector<u32> s(dataPtr, dataPtr + readData.size() / 4);

            for (int i = 0; i < s.size(); i++)
            {
                memory[i] = s[i];
            }
            for (int i = s.size() + 1; i < 0xffff; i++)
                memory[i] = 0;
        }
};

int main() {
    emu32 emu;
}