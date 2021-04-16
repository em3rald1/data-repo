function compile(code) {
    let r = 1;
    let out = '';
    for(let f of code) {
        switch(f) {
            case '+': {
                out += `INC R${r}, R${r}\n`;
                break;
            }
            case '-': {
                out += `DEC R${r}, R${r}\n`;
                break;
            }
            case '>':{
                r++;
                break;
            }
            case '<': {
                if(r == 1) break;
                r--;
                break;
            }
            case '.': {
                out += `OUT %79, R${r}\n`;
                break;
            }
            case ',': {
                out += `IN R${r}, %79\n`;
                break;
            }
        }
    }
    out += 'HLT';
    return out;
}

/**
 * 
 * @param {string} code 
 */

function optimize_(code) {
    let l = 0;
    let lines = code.split('\n');
    let lastl = '';
    let out = '';
    for(let i = 0; i < lines.length; i++) {
        let l1 = lines[i];
        let l2 = lines[i+1];
        if(l1 == l2) {
            if(l1.startsWith('INC')) {
                let i2 = 2;
                while(lines[i+2] == l1) {
                    i2++;
                    i++;
                }
                out += `ADD ${l1.split(' ')[1].replace(',','').trim()}, ${l1.split(' ')[1].replace(',','').trim()}, ${i2}\n`;
            }
            else if(l1.startsWith('DEC')) {
                let i2 = 2;
                while(lines[i+2] == l1) {
                    i2++;
                    i++;
                }
                out += `SUB ${l1.split(' ')[1].replace(',','').trim()}, ${l1.split(' ')[1].replace(',','').trim()}, ${i2}\n`;
            }
        }
        else {
            out += l1 + '\n';
        }
    }
    return out;
}

console.log(optimize_(compile('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.+++++++++++++++++++++++++++++.+++++++..+++.-------------------------------------------------------------------------------.+++++++++++++++++++++++++++++++++++++++++++++++++++++++.++++++++++++++++++++++++.+++.------.--------.-------------------------------------------------------------------.-----------------------.')));