const convert = require("./readUINT16ARRAY");
const rls = require('readline-sync');
const ISA = {
    addrr: 0,
    addir: 1,
    addii: 2,
    subrr: 3,
    subir: 4,
    subii: 5,
    rshr: 6,
    rshl: 7,
    lshr: 8,
    lshl: 9,
    incr: 10,
    incl: 11,
    decr: 12,
    decl: 13,
    xorrr: 14,
    xorlr: 15,
    xorll: 16,
    orrr: 17,
    orlr: 18,
    orll: 19,
    andrr: 20,
    andlr: 21,
    andll: 22,
    notr: 23,
    notl: 24,
    mov: 25,
    imm: 26,
    lodr: 27,
    lodl: 28,
    stral: 29,
    strar: 30,
    strrl: 31,
    strrr: 32,

    brar: 33,
    bral: 34,

    brcr: 35,
    brcl: 36,

    bncr: 37,
    bncl: 38,

    brzr: 39,
    brzl: 40,

    bnzr: 41,
    bnzl: 42,

    nop: 43,
    hlt: 44,
    pshl: 45,
    pshr: 46,
    pop: 47,

    calr: 48,
    call: 49,

    ret: 50,

    sav: 51,
    rsr: 52,
    // I/O

    in: 53,
    outr: 54,
    outl: 55
};

class EMU {
    constructor() {
        this.mem = new Uint16Array(0xffff);
        this.regs = new Uint16Array(0xff);
        this.ports = new Uint8Array(0xff);
        this.regs[0xff-3] = 0x7fff; // vsp
        this.regs[0xff-2] = 0x8fff; // csp
        this.regs[0xff-1] = 0x8fff; // ssp
        this.ip = 0;
        this.z = true;
        this.v = false;
        this.n = false;
        this.lv = 0;
    }

    fetch() {
        return this.mem[this.ip++];
    }
    push(d) {
        this.mem[this.regs[0xff-3]] = d;
        this.regs[0xff-3]--;
    }
    pop() {
        this.regs[0xff-3]++;
        return this.mem[this.regs[0xff-3]];
    }
    call(d) {
        this.mem[this.regs[0xff-2]] = this.ip;
        this.regs[0xff-2]--;
        this.ip = d;
    }

    ret() {
        this.regs[0xff-2]++;
        this.ip = this.mem[this.regs[0xff-2]];
    }

    sav(r) {
        this.mem[this.regs[0xff-1]] = this.regs[r];
        this.regs[0xff-1]--;
    }
    rsr(r) {
        this.regs[0xff-1]++;
        this.regs[r] = this.mem[this.regs[0xff-1]];
    }
    up_f(r) {
        this.z = r == 0;
        this.v = r > Math.pow(2, 16);
        this.n = r < 0;
    }
    step() {
        let res = false;
        let i = this.fetch();
        //console.log(i)
        if(this.ports[78] != 0) {
            process.stdout.write(new Uint8Array([this.ports[78]]))
            this.ports[78] = 0;
        }

        switch(i) {
            case ISA.addii: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.fetch();
                this.regs[d] = o1+o2;
                this.up_f(o1+o2);
                break;
            }
            case ISA.addir: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1+o2;
                this.up_f(o1+o2);
                break; 
            }
            case ISA.addrr: {
                let d = this.fetch();
                let o1 = this.regs[this.fetch()];
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1+o2;
                this.up_f(o1+o2);
                break; 
            }
            case ISA.subir: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1-o2;
                this.up_f(o1-o2);
                break;
            }
            case ISA.subrr: {
                let d = this.fetch();
                let o1 = this.regs[this.fetch()];
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1-o2;
                this.up_f(o1-o2);
                break;
            }
            case ISA.subii: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.fetch();
                this.regs[d] = o1-o2;
                this.up_f(o1-o2);
                break;
            }
            case ISA.rshl: {
                let d = this.fetch();
                let o = this.fetch();
                this.regs[d] = o >> 1;
                this.up_f(o >> 1);
                break;
            }
            case ISA.rshr: {
                let d = this.fetch();
                let o = this.regs[this.fetch()];
                this.regs[d] = o >> 1;
                this.up_f(o >> 1);
                break;
            }
            case ISA.lshl: {
                let d = this.fetch();
                let o = this.fetch();
                this.regs[d] = o << 1;
                this.up_f(o << 1);
                break;
            }
            case ISA.lshr: {
                let d = this.fetch();
                let o = this.regs[this.fetch()];
                this.regs[d] = o << 1;
                this.up_f(o << 1);
                break;
            }
            case ISA.incl: {
                let d = this.fetch();
                let o = this.fetch();
                this.regs[d] = o+1;
                this.up_f(o+1);
                break;
            }
            case ISA.incr: {
                let d = this.fetch();
                let o = this.regs[this.fetch()];
                this.regs[d] = o+1;
                this.up_f(o+1);
                break;
            }
            case ISA.decl: {
                let d = this.fetch();
                let o = this.fetch();
                this.regs[d] = o-1;
                this.up_f(o-1);
                break;
            }
            case ISA.decr: {
                let d = this.fetch();
                let o = this.regs[this.fetch()];
                this.regs[d] = o-1;
                this.up_f(o-1);
                break;
            }
            case ISA.xorrr: {
                let d = this.fetch();
                let o1 = this.regs[this.fetch()];
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1^o2;
                this.up_f(o1^o2);
                break;
            }
            case ISA.xorlr: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1^o2;
                this.up_f(o1^o2);
                break;
            }
            case ISA.xorll: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.fetch();
                this.regs[d] = o1^o2;
                this.up_f(o1^o2);
                break;
            }

            case ISA.orrr: {
                let d = this.fetch();
                let o1 = this.regs[this.fetch()];
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1|o2;
                this.up_f(o1|o2);
                break;
            }
            case ISA.orlr: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1|o2;
                this.up_f(o1|o2);
                break;
            }
            case ISA.orll: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.fetch();
                this.regs[d] = o1|o2;
                this.up_f(o1|o2);
                break;
            }

            case ISA.andrr: {
                let d = this.fetch();
                let o1 = this.regs[this.fetch()];
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1&o2;
                this.up_f(o1&o2);
                break;
            }
            case ISA.andlr: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.regs[this.fetch()];
                this.regs[d] = o1&o2;
                this.up_f(o1&o2);
                break;
            }
            case ISA.andll: {
                let d = this.fetch();
                let o1 = this.fetch();
                let o2 = this.fetch();
                this.regs[d] = o1&o2;
                this.up_f(o1&o2);
                break;
            }
            case ISA.notr: {
                let d = this.fetch();
                let o = this.regs[this.fetch()];
                this.regs[d] = ~o;
                this.up_f(~o);
                break;
            }
            case ISA.notl: {
                let d = this.fetch();
                let o = this.fetch();
                this.regs[d] = ~o;
                this.up_f(~o);
                break;
            }
            case ISA.mov: {
                let d = this.fetch();
                let s = this.regs[this.fetch()];
                this.regs[d] = s;
                break;
            }
            case ISA.imm: {
                let d = this.fetch();
                let s = this.fetch();
                //console.log(d, s)
                this.regs[d] = s;
                break;
            }

            case ISA.lodl: {
                let d = this.fetch();
                let a = this.fetch();
                this.regs[d] = this.mem[a];
                break;
            }
            case ISA.lodr: {
                let d = this.fetch();
                let a = this.regs[this.fetch()];
                this.regs[d] = this.mem[a]
                break;
            }

            case ISA.stral: {
                let a = this.fetch();
                let d = this.fetch();
                this.mem[a] = d;
                break;
            }
            case ISA.strar: {
                let a = this.fetch();
                let d = this.regs[this.fetch()];
                this.mem[a] = d;
                break;
            }
            case ISA.strrl: {
                let a = this.regs[this.fetch()];
                let d = this.fetch();
                this.mem[a] = d;
                break;
            }
            case ISA.strrr: {
                let a = this.regs[this.fetch()];
                let d = this.regs[this.fetch()];
                this.mem[a] = d;
                break;
            }

            case ISA.bral: {
                let a = this.fetch();
                this.ip = a;
                break;
            }
            case ISA.brar: {
                let a = this.regs[this.fetch()];
                this.ip = a;
                break;
            }

            case ISA.brcr: {
                let a = this.regs[this.fetch()];
                if(this.v) this.ip = a;
                break;
            }
            case ISA.brcl: {
                let a = this.fetch();
                if(this.v) this.ip = a;
                break;
            }

            case ISA.bncr: {
                let a = this.regs[this.fetch()];
                if(!this.v) this.ip = a;
                break;
            }
            case ISA.bncl: {
                let a = this.fetch();
                if(!this.v) this.ip = a;
                break;
            }
            case ISA.brzr: {
                let a = this.regs[this.fetch()];
                if(this.z) this.ip = a;
                break;
            }
            case ISA.brzl: {
                let a = this.fetch();
                if(this.z) this.ip = a;
                break;
            }
            case ISA.bnzr: {
                let a = this.regs[this.fetch()];
                if(!this.z) this.ip = a;
                break;
            }
            case ISA.bnzl: {
                let a = this.fetch();
                if(!this.z) this.ip = a;
                break;
            }
            case ISA.nop: {
                break;
            }
            case ISA.hlt: {
                res = true;
                break;
            }
            case ISA.pshl: {
                this.push(this.fetch());
                break;
            }
            case ISA.pshr: {
                this.push(this.regs[this.fetch()]);
                break;
            }
            case ISA.pop: {
                this.regs[this.fetch()] = this.pop();
                break;
            }
            case ISA.call: {
                this.call(this.fetch());
                break;
            }
            case ISA.calr: {
                this.call(this.regs[this.fetch()]);
                break;
            }
            case ISA.ret: {
                this.ret();
                break;
            }
            case ISA.sav: {
                this.sav(this.fetch());
                break;
            }
            case ISA.rsr: {
                this.rsr(this.fetch());
                break;
            }
            case ISA.in: {
                let r = this.fetch();
                let p = this.fetch();
                if(p == 77) {
                    let d = Buffer.from(rls.question()[0])[0];
                    this.ports[p] = d;
                    this.regs[p] = d;
                }
                //process.stdin.setRawMode(true).read(1);
                this.regs[r] = this.ports[p];

                break;
            }
            case ISA.outr: {
                let p = this.fetch();
                let r = this.fetch();
                this.ports[p] = this.regs[r];
                break;
            }
            case ISA.outl: {
                let p = this.fetch();
                let r = this.fetch();
                this.ports[p] = r;
                break;
            }
        }
        return res;
    }
    debug() {
        console.log('REGISTERS:')
        for(let i = 0; i < this.regs.length; i++) {
            if(this.regs[i] != 0) {
                console.log(`$${i}: ${this.regs[i]}`);
            }
        }
        console.log('PORTS:');
        for(let i = 0; i < this.ports.length; i++) {
            if(this.ports[i] != 0) {
                console.log(`%${i}: ${this.ports[i]}`)
            }
        }
        console.log('ZERO FLAG: ' + (this.z ? 1 :0))
        console.log('OVERFLOW FLAG: ' + (this.v ? 1 : 0))
        console.log('NEGATIVE FLAG: ' + (this.n?1:0));
    }
    run(code, offset, start_offset, debug=false) {
        this.ip = start_offset;
        for(let i = 0; i < code.length; i++) {
            this.mem[i+offset] = code[i];
        }
        let i = false;
        while (!i) {
            i = this.step();
            if(i) break;
        }
        if(debug) this.debug();
    }
}
let fs = require('fs');
const data = fs.readFileSync(process.argv[2]);
//console.log(data)
let code = convert(data);
//console.log(code)
let urcl = new EMU();
urcl.run(code, 0, 0, true);