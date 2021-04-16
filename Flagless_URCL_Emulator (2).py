#flagless URCL V1.0.1 emulator

#imports
import sys

#function definitions
def importCode(name):
    while True:
        try:
            file = open(name, "r") #test if file exists
            break
        except:
            print("Cannot find file: " + str(name) + "\n")
            print("Enter name again")
            return ""
    code = file.readlines()
    file.close()
    return code
def cleanCode(code):
    final = []
    for i in range(len(code)):
        temp = code[i].find("//") #remove comments
        if not(temp == -1):
            code[i] = code[i][:temp]
        code[i] = "".join(code[i].split()) #remove whitespace
        if code[i] == "":
            pass
        else:       #normal code
            final.append(code[i])
    return final
def read(code, char, end):
    num = 0
    answer = ""
    while len(code) > (char + num):
        if code[char + num] in end:
            break
        else:
            answer += code[char + num]
            num += 1
    char += num + 1
    return answer, char
def status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels):
    temp = "\n\nTotal Cycles = " + str(cycles) + "\nInstruction = " + str(memory[PC]) + "\nPC = " + str("0x" + hex(PC)[2:].upper()) + "\nRegisters:\n"
    for i in range(len(registers) - 1):
        temp += "R" + str(i + 1) + " = " + str("0x" + hex(registers[i + 1])[2:].upper()) + "\n"
    temp += "Memory:\n"
    for i in range(len(memory)):
        if memoryMap[i] == 1:
            if str(i) in labels[1]:
                temp += "M0x" + hex(i)[2:].upper() + " = " + str("0x" + hex(memory[i])[2:].upper()) + " " + labels[0][labels[1].index(str(i))] + "\n"
            else:
                temp += "M0x" + hex(i)[2:].upper() + " = " + str("0x" + hex(memory[i])[2:].upper()) + "\n"
    tempSave = ""
    x = len(memory) - 1
    for i in range(SAVESTACK):
        tempSave += "M0x" + hex(x)[2:].upper() + " = " + str("0x" + hex(memory[x])[2:].upper()) + "\n"
        x -= 1
    tempValue = ""
    for i in range(VALUESTACK):
        tempValue += "M0x" + hex(x)[2:].upper() + " = " + str("0x" + hex(memory[x])[2:].upper()) + "\n"
        x -= 1
    tempCall = ""
    for i in range(CALLSTACK):
        tempCall += "M0x" + hex(x)[2:].upper() + " = " + str("0x" + hex(memory[x])[2:].upper()) + "\n"
        x -= 1
    temp += "Call Stack:\nCSP = " + str("0x" + hex(CSP)[2:].upper()) + "\n" + tempCall + "Value Stack:\nVSP = " + str("0x" + hex(VSP)[2:].upper()) + "\n" + tempValue + "Save Stack:\nSSP = " + str("0x" + hex(SSP)[2:].upper()) + "\n" + tempSave
    temp2 = []
    for i in output:
        temp2.append("0x" + hex(i)[2:].upper())
    temp += "Outputs: " + str(temp2) + "\n"
    temp3 = ""
    for i in output:
        try:
            temp3 += chr(int(i))
        except:
            temp3 += "<" + str(i) + ">"
    temp += "\n***************************\nASCII outputs:\n" + temp3 + "\n***************************"
    print(temp)
def outputPrint(output):
    temp2 = []
    for i in output:
        temp2.append("0x" + hex(i)[2:].upper())
    temp = "Outputs: " + str(temp2)
    temp3 = ""
    for i in output:
        try:
            temp3 += chr(int(i))
        except:
            temp3 += "<" + str(i) + ">"
    temp += "\n***************************\nASCII outputs:\n" + temp3 + "\n***************************"
    print(temp)
def readOps(code, char):
    temp = []
    temp2 = ""
    num = 0
    while (char + num) < len(code):
        if code[char + num] not in ",)":
            temp2 += code[char + num]
            num += 1
        else:
            if len(temp2) == 1:
                if temp2.isnumeric():
                    temp2 = "0" + temp2
            temp.append(temp2)
            temp2 = ""
            if code[char + num] == ")":
                break
            num += 1
    char += num + 1
    if temp2 != "":
        temp.append(temp2)
    if temp == []:
        pass
    elif temp[0] == "":
        temp = []
    return temp
def retrieve(op, registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code):
    if op[:1] == "R":
        if registersMap[int(op[1:])] == 1:
            answer = registers[int(op[1:])]
            species = "R"
        else:
            answer = "FATAL - Tried to read an uninitialised register\nIn instruction: " + memory[PC] + "\nOn line: " + str(PC)
    elif (op[:1] == "M") or ((memory[PC][:3] == "LOD") and op.isnumeric() and (memory[PC][::-1][:len(op)] == op[::-1])) or (memory[PC][:3] in ["RET", "POP", "RSR"]):
        if memoryMap[int(op[1:]) + len(code)] == 1:
            if op[:1].isnumeric():
                answer = memory[int(op)]
            else:
                answer = memory[int(op[1:]) + len(code)]
            species = "M"
        elif memoryMap[int(op)] == 1:
            if op[:1].isnumeric():
                answer = memory[int(op)]
            else:
                answer = memory[int(op[1:]) + len(code)]
            species = "M"
        else:
            answer = "FATAL - Tried to read an uninitialised word in memory\nIn instruction: " + memory[PC] + "\nOn line: " + str(PC)
            species = "None"
    elif op.isnumeric():
        answer = int(op)
        species = "I"
    elif op == "CSP":
        answer = CSP
        species = "R"
    elif op == "VSP":
        answer = VSP
        species = "R"
    elif op == "SSP":
        answer = SSP
        species = "R"
    else:
        answer = "FATAL - unrecognised operand: " + op + "\nIn instruction: " + memory[PC] + "\nOn line: " + str(PC)
        species = "None"
    return answer, species
def ifError(ops):
    for i in range(len(ops)):
        if type(ops[i]) == str:
            while True: input(ops[i])
def write(op, value, registers, memory, registersMap, memoryMap, PC, code):
    if op[:1] == "R":
        registers[int(op[1:])] = value
        registersMap[int(op[1:])] = 1
    elif (op[:1] == "M") or ((memory[PC][:3] == "STR") and op.isnumeric() and ((memory[PC][3:3 + len(op)] == op) or (memory[PC][3:4] == "R"))) or (memory[PC][:3] in ["CAL", "PSH", "SAV"]):
        if op[:1].isnumeric():
            memory[int(op)] = value
            memoryMap[int(op)] = 1
        else:
            try:
                memory[int(op[1:]) + len(code)] = value
                memoryMap[int(op[1:]) + len(code)] = 1
            except:
                while True: input("FATAL - Attempted to write to a memory address that isn't inside of the valid address space\nAttempted to write to: " + op + "\nwhen the offset is added this address is: " + str(int(op[1:]) + len(code)) + "\nOn instruction: " + memory[PC] + "\nOn line: " + str(PC))
    else:
        while True: input("FATAL - Invalid write location: " + op + "\nIn instruction: " + memory[PC] + "\nOn line: " + str(PC))
    return registers, memory, registersMap, memoryMap
def correctValue(value, BITS):
    value = int(value)
    x = 2 ** BITS
    while value > x - 1:
        value -= x
    while value < 0:
        value += x
    return value
def opsCount(ops, length, PC, instruction):
    if len(ops) != length:
        while True: input("FATAL - Expected " + str(length) + " operands in instruction: " + instruction + "\nOn line: " + str(PC) + "\nFound " + str(len(ops)) + " operands instead")

#main
#import code
while True:
    mainName = input("Enter name of .urcl file (without the extention): ")
    code = importCode(mainName + ".urcl")
    if code != "":
        break
code = cleanCode(code)

#find header info
BITS = ""
MINREG = ""
MINRAM = ""
for i in range(len(code)):

    if code[i][:4] == "BITS":
        if code[i].find("=") == -1:
            BITS = int(code[i][4:])
        elif code[i][4:6] in ["==", ">=", "<="]:
            BITS = int(code[i][6:])
        else:
            try:
                BITS = int(code[i][4:])
            except:
                while True: input("FATAL - Invalid BITS header in code: " + code[i])
        code[i] = ""

    elif code[i][:6] == "MINREG":
        try:
            MINREG = int(code[i][6:])
        except:
            while True: input("FATAL - Invalid MINREG header in code: " + code[i])
        code[i] = ""

    elif code[i][:6] == "MINRAM":
        try:
            MINRAM = int(code[i][6:])
        except:
            while True: input("FATAL - Invalid MINRAM header in code: " + code[i])
        code[i] = ""

    elif code[i][:3] == "RUN":
        if code[i][3:] == "ROM":
            while True: input("FATAL - RUN ROM is not supported in this emulator, only RUN RAM is supported")
        code[i] = ""

    elif code[i][:6] == "IMPORT":
        while True: input("FATAL - Libraries are currently not supported in this emulator")
if BITS == "":
    BITS = 8
if MINREG == "":
    MINREG = 8
if MINRAM == "":
    MINRAM = 16
code = cleanCode(code)

#convert labels to absolutes
temp = []
labels = [[], []]
for i in range(len(code)):
    if code[i][:1] == ".":
        labels[0].append(code[i])
        labels[1].append(str(len(temp)))
    else:
        temp.append(code[i])
code = temp
for i in range(len(code)):
    for j in range(len(labels[0])):
        if code[i].find(labels[0][j]):
            if (code[i][code[i].find(labels[0][j]):code[i].find(labels[0][j]) + len(labels[0][j]) + 1] == labels[0][j]) or (code[i][code[i].find(labels[0][j]):code[i].find(labels[0][j]) + len(labels[0][j]) + 1] == labels[0][j] + ",") or (code[i][code[i].find(labels[0][j]):code[i].find(labels[0][j]) + len(labels[0][j]) + 1] == labels[0][j] + ")"):
                code[i] = code[i].replace(labels[0][j], labels[1][j])

#convert hex and bin to base 10
for i in range(len(code)):
    while code[i].find("0x") != -1:
        num, char = read(code[i], code[i].find("0x"), ",)")
        num2 = str(int(num, 0))
        code[i] = code[i].replace(num, num2, 1)
    while code[i].find("0b") != -1:
        num, char = read(code[i], code[i].find("0b"), ",)")
        num2 = str(int(num, 0))
        code[i] = code[i].replace(num, num2, 1)

#setup reg and ram
x = (2 ** BITS) - 1
registers = [x for i in range(MINREG + 1)]
registers[0] = 0
registersMap = [0 for i in range(MINREG + 1)]
registersMap[0] = 1
memory = [x for i in range(x + 1)]
memoryMap = [0 for i in range(x + 1)]

#setup stacks
while True:
    try:
        CALLSTACK = int(input("Enter Call Stack size in words: "))#
        break
    except:
        print("Invalid value")
while True:
    try:
        VALUESTACK = int(input("Enter Value Stack size in words: "))
        break
    except:
        print("Invalid value")
while True:
    try:
        SAVESTACK = int(input("Enter Save Stack size in words: "))
        break
    except:
        print("Invalid value")
SSP = x + 1 - SAVESTACK
VSP = SSP - VALUESTACK
CSP = VSP - CALLSTACK
callSize = 0
valueSize = 0
saveSize = 0
output = []
output2 = []

#put instructions in memory
if (len(code) + CALLSTACK + VALUESTACK + SAVESTACK) > (x + 1):
    while True: input("FATAL - Code is too long (" + str(len(code) + CALLSTACK + VALUESTACK + SAVESTACK) + " words) and cannot fit in the " + str(x + 1) + " word RAM\nEither make the word length longer or make the stacks smaller to run this code")
for i in range(len(code)):
    if code[i][:2] == "DW":
        memory[i] = int(code[i][2:])
        memoryMap[i] = 1
    else:
        memory[i] = code[i]

#loop setup
PC = 0
cycles = 0
while True:
    frequency = input("Enter how often the emulators status should be printed (type 'All' for a status every cycle or 'None' to only print output): ")
    if frequency in ["All", "None"]:
        break
    else:
        print("Invalid Value")

#loop
while True:
    branch = 0

    if frequency == "All":
        status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels)
    elif output != output2:
        outputPrint(output)
    output2 = []
    for i in output:
        output2.append(i)
    if ((cycles % 1000) == 999) and (frequency == "All"):
        input("1000 instructions have been executed, press Enter to continue: ")
    elif ((cycles % 1000) == 999) and (frequency == "None"):
        status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels)
        input("1000 instructions have been executed, press Enter to continue: ")

    instruction = memory[PC]
    if type(instruction) == int:
        while True: input("FATAL - Tried to execute a memory value which is not an instruction\nOn line: " + str(PC))
    if instruction.isnumeric():
        while True: input("FATAL - Tried to execute a memory value which is not an instruction\nOn line: " + str(PC))

    ops = readOps(instruction, 3)
    species = ["Unknown"]
    for i in range(len(ops) - 1):
        ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
        species.append(temp)

    #core instructions
    if instruction[:3] == "ADD":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] + ops[2]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "RSH":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] / 2
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "LOD":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "MI"):
            if memoryMap[ops[1]] == 0:
                while True: input("FATAL - Tried to read from an uninitialised RAM location, on line: " + str(PC) + "\nIn instruction: " + instruction)
            ops[1] = memory[ops[1]]
        answer = ops[1]

        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "STR":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1]
        answer = correctValue(answer, BITS)
        if ops[0][:1] == "R":
            ops[0], temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            ops[0] = str(ops[0])
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "BRA":
        opsCount(ops, 1, PC, instruction)
        PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
        if temp not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        branch = 1

    elif instruction[:3] == "BGE":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] >= ops[2]:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "NOR":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ~(ops[1] | ops[2])
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "CAL":
        opsCount(ops, 1, PC, instruction)
        registers, memory, registersMap, memoryMap = write(str(CSP), PC + 1, registers, memory, registersMap, memoryMap, PC, code)
        CSP += 1
        PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
        if temp not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        branch = 1
        callSize += 1
        if callSize > CALLSTACK:
            status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels)
            while True: input("FATAL - Call Stack overflow\nOn instruction: " + instruction + "\nOn line: " + str(PC))

    elif instruction[:3] == "RET":
        opsCount(ops, 0, PC, instruction)
        CSP -= 1
        PC, temp = retrieve(str(CSP), registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
        branch = 1
        callSize -= 1
        if callSize < 0:
            status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels)
            while True: input("FATAL - Call Stack underflow\nOn instruction: " + instruction + "\nOn line: " + str(PC))

    elif instruction[:3] == "PSH":
        opsCount(ops, 1, PC, instruction)
        ops[0], temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
        if temp not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        registers, memory, registersMap, memoryMap = write(str(VSP), ops[0], registers, memory, registersMap, memoryMap, PC, code)
        VSP += 1
        valueSize += 1
        if valueSize > VALUESTACK:
            status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels)
            while True: input("FATAL - Value Stack overflow\nOn instruction: " + instruction + "\nOn line: " + str(PC))

    elif instruction[:3] == "POP":
        opsCount(ops, 1, PC, instruction)
        VSP -= 1
        answer, temp = retrieve(str(VSP), registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)
        valueSize -= 1
        if valueSize < 0:
            status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels)
            while True: input("FATAL - Value Stack underflow\nOn instruction: " + instruction + "\nOn line: " + str(PC))

    elif instruction[:3] == "SAV":
        opsCount(ops, 1, PC, instruction)
        ops[0], temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
        if temp not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        registers, memory, registersMap, memoryMap = write(str(SSP), ops[0], registers, memory, registersMap, memoryMap, PC, code)
        SSP += 1
        saveSize += 1
        if saveSize > SAVESTACK:
            status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels)
            while True: input("FATAL - Save Stack overflow\nOn instruction: " + instruction + "\nOn line: " + str(PC))

    elif instruction[:3] == "RSR":
        opsCount(ops, 1, PC, instruction)
        SSP -= 1
        answer, temp = retrieve(str(SSP), registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)
        saveSize -= 1
        if saveSize < 0:
            status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels)
            while True: input("FATAL - Save Stack underflow\nOn instruction: " + instruction + "\nOn line: " + str(PC))

    elif instruction[:3] == "HLT":
        opsCount(ops, 0, PC, instruction)
        status(cycles, PC, registers, memory, memoryMap, CALLSTACK, VALUESTACK, SAVESTACK, CSP, VSP, SSP, output, labels)
        input("Press Enter to close: ")
        sys.exit()

    #basic instructions
    elif instruction[:3] == "SUB":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] - ops[2]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "MOV":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "NOP":
        opsCount(ops, 0, PC, instruction)

    elif instruction[:3] == "IMM":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "LSH":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] * 2
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "INC":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] + 1
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "DEC":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] - 1
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "NEG":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = -ops[1]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "AND":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] & ops[2]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:2] == "OR":

        ops = readOps(instruction, 2)
        species = ["Unknown"]
        for i in range(len(ops) - 1):
            ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            species.append(temp)
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] | ops[2]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "NOT":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ~ops[1]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:4] == "XNOR":

        ops = readOps(instruction, 4)
        species = ["Unknown"]
        for i in range(len(ops) - 1):
            ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            species.append(temp)
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ~(ops[1] ^ ops[2])
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "XOR":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] ^ ops[2]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:4] == "NAND":

        ops = readOps(instruction, 4)
        species = ["Unknown"]
        for i in range(len(ops) - 1):
            ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            species.append(temp)
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ~(ops[1] & ops[2])
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "BRL":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] < ops[2]:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BRG":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] > ops[2]:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BRE":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] == ops[2]:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BNE":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] != ops[2]:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BOD":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if (ops[1] % 2) == 1:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BEV":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if (ops[1] % 2) == 0:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BLE":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] <= ops[2]:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BRZ":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] == 0:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BNZ":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] != 0:
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BRN":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] >= (2 ** (BITS - 1)):
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:3] == "BRP":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] < (2 ** (BITS - 1)):
            PC, temp = retrieve(ops[0], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            branch = 1

    elif instruction[:2] == "IN":

        ops = readOps(instruction, 2)
        species = ["Unknown"]
        opsCount(ops, 2, PC, instruction)
        outputPrint(output)
        
        while True:
            try:
                temp = input("Enter an input value for IN instruction: " + instruction + "\nOn line: " + str(PC) + "\nnumbers must have a prefix (0x, od, 0b) otherwise it will be converted to ASCII values: ")
                if len(temp) > 1:
                    answer = int(temp, 0)
                else:
                    answer = ord(temp)
                print("Input = 0x" + hex(answer)[2:].upper())
                break
            except:
                print("Invalid input")
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "OUT":
        
        ops = readOps(instruction, 3)
        opsCount(ops, 2, PC, instruction)
        if (ops[1].find("'") == -1) and (ops[1].find('"') == -1):
            ops[1], temp = retrieve(ops[1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            ifError(ops[1:])

        output.append(ops[1])

    #complex instructions
    elif instruction[:3] == "MLT":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] * ops[2]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "DIV":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] / ops[2]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "MOD":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] % ops[2]
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "BSR":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] / (2 ** ops[2])
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "BSL":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        answer = ops[1] * (2 ** ops[2])
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "SRS":
        opsCount(ops, 2, PC, instruction)
        ifError(ops[1:])
        if species[1] not in "RI":
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] >= (2 ** (BITS - 1)):
            answer = (ops[1] / 2) + (2 ** (BITS - 1))
        else:
            answer = ops[1] / 2
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "BSS":
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        while ops[2] > 0:
            if ops[1] >= (2 ** (BITS - 1)):
                answer = (ops[1] / 2) + (2 ** (BITS - 1))
            else:
                answer = ops[1] / 2
            ops[2] -= 1
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "SETE":

        ops = readOps(instruction, 4)
        species = ["Unknown"]
        for i in range(len(ops) - 1):
            ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            species.append(temp)
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] == ops[2]:
            answer = 1
        else:
            answer = 0
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "SETNE":

        ops = readOps(instruction, 5)
        species = ["Unknown"]
        for i in range(len(ops) - 1):
            ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            species.append(temp)
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] != ops[2]:
            answer = 1
        else:
            answer = 0
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "SETG":

        ops = readOps(instruction, 4)
        species = ["Unknown"]
        for i in range(len(ops) - 1):
            ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            species.append(temp)
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] > ops[2]:
            answer = 1
        else:
            answer = 0
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "SETL":

        ops = readOps(instruction, 4)
        species = ["Unknown"]
        for i in range(len(ops) - 1):
            ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            species.append(temp)
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] < ops[2]:
            answer = 1
        else:
            answer = 0
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "SETGE":

        ops = readOps(instruction, 5)
        species = ["Unknown"]
        for i in range(len(ops) - 1):
            ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            species.append(temp)
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] >= ops[2]:
            answer = 1
        else:
            answer = 0
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    elif instruction[:3] == "SETLE":

        ops = readOps(instruction, 5)
        species = ["Unknown"]
        for i in range(len(ops) - 1):
            ops[i + 1], temp = retrieve(ops[i + 1], registers, memory, PC, memoryMap, registersMap, CSP, VSP, SSP, code)
            species.append(temp)
        opsCount(ops, 3, PC, instruction)
        ifError(ops[1:])
        if (species[1] not in "RI") or (species[2] not in "RI"):
            while True: input("FATAL - invalid operand types in instruction: " + instruction + "\nOn line: " + str(PC))
        if ops[1] <= ops[2]:
            answer = 1
        else:
            answer = 0
        answer = correctValue(answer, BITS)
        registers, memory, registersMap, memoryMap = write(ops[0], answer, registers, memory, registersMap, memoryMap, PC, code)

    else:
        while True: input("FATAL - Unrecognised instruction: " + instruction + "\nOn line: " + str(PC))

    if branch == 0:
        PC += 1
    cycles += 1
    registers[0] = 0











