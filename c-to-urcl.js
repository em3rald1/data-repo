const SPEC_CHARS = '(){}[]<>;.!~:';

/**
 * 
 * @param {string} s 
 */
function split(s) {
    /** @type {string[]} */
    let t = [];
    let n = '';
    for(let c of s) {
        if(n.startsWith('STRING_GET:') && c != '"')
            n += c;
        else if(c == ' ' || c == '\r' || c == '\t') {
            if(n != '') 
                t.push(n);
            n = '';
        }
        else if(c == '\n') {
            if(n != '')
                t.push(n);
            t.push('\n');
            n = '';
        }
        else if(SPEC_CHARS.includes(c)) {
            if(n != '')
                t.push(n);
            t.push(c);
            n = '';
        }
        else if(c == '+') {
            if(n == '+')
                {t.push('++');n=''}
            else if(n == '')
                n = '+'
            else
            {
                t.push(n)
                n = '+';
            }
        }
        else if(c == '-') {
            if(n == '-')
                {t.push('--');n=''}
            else if(n == '')
                n = '-'
            else
            {
                t.push(n)
                n = '-';
            }
        }
        else if(c == '"') {
            if(!n.startsWith('STRING_GET:'))
                n = 'STRING_GET:';
            else
                {t.push(n.slice('STRING_GET:'.length));n=''}
        }
        else if('*^|&'.includes(c)) {
            if(n == '')
                n = c
            else
            {
                t.push(n)
                n = c;
            }
        }
        else if(c == '/') {
            if(n == '/'){t.push('//');n=''}
            else if(n == '')
                n = '/'
            else
            {
                t.push(n)
                n = '/';
            }
        }
        else if(c == '=') {
            if('+-/*=&^|'.includes(n[0])) {
                t.push(n[0]+c);
                n = '';
            } else if(n == '')
                n = c
            else{
                t.push(n);n=c};
        }
        else {
            const OPS = ['+','-','/','*','==','!=','^','&','|', '(']
            if(!SPEC_CHARS.includes(n) && !OPS.includes(n))
                n += c;
            else {
                if(n != '')
                    t.push(n)
                n = c;}
        }
    }
    if(n != '') t.push(n)
    return t;
}
/**
 * Deletes comments, formats pragmas, concats special chars (["<","<"] => ["<<"]), etc.
 * @param {string[]} s 
 * @returns {string[]}
 */
function util(s) {
    let no = [];
    for(let i = 0; i < s.length; i++) {
        let d = s[i];
        if(d == '<' && s[i+1] == '<') {
            no.push('<<');
            i++;
        }
        else if(d == '>' && s[i+1] == '>') {
            no.push('>>');
            i++;
        }
        else if(d == ':' && s[i+1] == ':') {
            no.push('::');
            i++;
        }
        else if(d == '//') {
            while(s[i] != '\n') {
                i++;
            };
        }
        else
            no.push(d);
    }
    return no;
}

/**
 * 
 * @param {string[]} exp 
 */
function parse_expression(exp) {
    const OPS = ['+','-','/','*','==','!=','^','&','|', '(']
    let o = [];
    let os = [];
    let i = 0;
    while(true) {
        if(OPS.includes(exp[i])) {
            os.push(exp[i]);
        }
        else if(exp[i] == ')') {
            while(os.reverse()[0] != '(') {
                if(os.reverse()[0])
                    o.push(os.pop());
                else break;
            }
        }
        else {
            o.push(exp[i]);
        }
        console.log(o, os)
        i++;
        console.log(exp[i])
        if(!exp[i]) break;
    }
    let no = [];
    console.log('e')
    while(os[0]) {
        o.push(os.pop());
    }
    for(let f of o) {
        if(f != '(') no.push(f);
    }
    return no;
}

let d = split('#include <iostream>\n// just a comment\nint main() {\n\tstd::cout << "hello world!";\n\treturn 0;\n}\n');
console.log(split('(((4+3)+3)*4'))
console.log(parse_expression(split('(((4+3)+3)*(4+3))')))