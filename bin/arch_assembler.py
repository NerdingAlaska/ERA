import sys, os, parser
from pathlib import Path

def assemblyCompile():
    # Seek out the arch folder
    curPath = Path.getcwd()
    nextPath = curPath + '/sys'
    os.chdir(nextPath)

#The below code segment has been moved to the parser.py file but is left here until the parser.py file has been updated and this legacy code is removed
'''
    # Parse the microcode.txt
    with open('microcode.txt', 'r') as micro:
        contents = [l.split()[0].split(',') for l in micro.readlines()]

    # Making the microcode dictionary
    microDict = {c[0]: int(c[1]) for c in contents}

    # Parsing flags.txt
    with open('flags.txt', 'r') as flags:
        contents = [(l.split()[0], int(l.split()[1])) for l in flags.readlines()]

    # Making the flags dictionary
    flagsDict = {c[0]: c[1] for c in contents}

    # Initial parse of assembly.txt
    with open('assembly.txt', 'r') as assemblyFile:
        contents = [l.split()[:3] for l in assemblyFile.readlines()]

    # Come back to the initial working directory
    os.chdir(curPath)
    try:
        # This could all be one list comprehension but it's more readable this way
        assemblyList = [(l[0], [flagsDict[f] for f in l[1].split(',')], [microDict[m] for m in l[2].split(',')]) for l
                        in contents]
        # We can take this opportunity to also gather the encoding for all the assembly codes in order
        assemblyEncoding = []
        for a in assemblyList:
            if a[0] not in assemblyEncoding:
                assemblyEncoding.append(a[0])
        assemblyEncoding = {a: hex(b)[2:] for (a, b) in zip(assemblyEncoding, range(len(assemblyEncoding)))}
        # The end result is a list of lists, the inner lists each having the microcode definitions for each assembly instruction,
        # in tuple form and in order.
        intermediateAssembly = [[a for a in assemblyList if a[0] == b[0]] for b in assemblyList]
        assemblyList = []
        # Getting the unique list, since the previous step made x copies of each assembly instruction, where x is the number of steps in that instruction
        for a in intermediateAssembly:
            if a not in assemblyList:
                assemblyList.append(a)
        print(assemblyList[1])
        for s in range(len(assemblyList)):
            for t in range(len(assemblyList[s])):
                if len(assemblyList[s][t][1]) > 0:
                    result = 0
                    for flag in assemblyList[s][t][1]:
                        result += int(flag)
                    assemblyList[s][t] = (assemblyList[s][t][0], result, assemblyList[s][t][2])
                else:
                    assemblyList[s] = (assemblyList[s][t][0], int(assemblyList[s][t][1][0]), assemblyList[s][t][2])

        return (assemblyList, assemblyEncoding, flagsDict)
    except (bbSyntaxError, KeyError) as bbE:
        print("Syntax Error: Improper microcode definition: ", bbE)
'''

def CPUROMWrite(assemblyList, assemblyEncoding, flagsDict):
    # Move to output folder
    curPath = os.getcwd()
    os.chdir(curPath + "/output")
    # We can go ahead and split out the flag differences from the instructions
    flagAssemblyList = [[s for s in c if s[1] != 0] for c in assemblyList]
    flagAssemblyList = [c for c in flagAssemblyList if len(c) > 0]
    assemblyList = [[s for s in c if s[1] == 0] for c in assemblyList]
    entryList = []
    for c in range(len(flagAssemblyList)):
        for s in range(len(flagAssemblyList[c])):
            flagAssemblyList[c][s] = (flagAssemblyList[c][s][0], flagAssemblyList[c][s][1], flagAssemblyList[c][s][2])
    # Open the output file
    with open("CPUROM", "w") as fileOut:
        fileOut.write("v2.0 raw\n")
        mempos = 0
        linepos = 0
        instructionCount = 0
        # We're going to loop through the list of assembly commands and write those commands to the ROM chip as the hex values Logisim wants.
        # We're also going to record the memory position where the commands are being written so that we can make a valid mapping later.
        for k in assemblyList:
            entryList.append([instructionCount, 0, mempos])
            instructionCount += 1
            for i in k:
                mempos += 1
                fileOut.write(hex(sum([2 ** int(j) for j in i[2]]))[2:])
                if linepos == 15:
                    fileOut.write('\n')
                    linepos = 0
                else:
                    fileOut.write(' ')
                    linepos += 1
                    # Now we can loop through the flags, checking for any instructions that care about flags
        for f in range(1, 2 ** (len(flagsDict) - 1)):
            for k in range(len(assemblyList)):
                print(assemblyList)
                if assemblyList[k][0][0] in [q[0][0] for q in flagAssemblyList if f in [r[1] for r in q]]:
                    entryList.append([k, f, mempos])
                    curcode = assemblyList[k][0][0]
                    for i in [t[u] for t in flagAssemblyList for u in range(len(t)) if
                              t[u][1] == f and t[u][0] == curcode]:
                        mempos += 1
                        fileOut.write(hex(sum([2 ** int(j) for j in i[2]]))[2:])
                        if linepos == 15:
                            fileOut.write('\n')
                            linepos = 0
                        else:
                            fileOut.write(' ')
                            linepos += 1
                else:
                    origmempos = [m[2] for m in entryList if m[0] == k and m[1] == 0][0]
                    entryList.append([k, f, origmempos])
                    for i in range(len(assemblyList[k])):
                        mempos += 1
                        fileOut.write(hex(sum([2 ** int(j) for j in assemblyList[k][i][2]]))[2:])
                        if linepos == 15:
                            fileOut.write('\n')
                            linepos = 0
                        else:
                            fileOut.write(' ')
                            linepos += 1

                            # Now we can go in and write the mapping ROM
    linepos = 0
    mempos = 0
    with open("CPUMappingROM", "w") as fileOut:
        fileOut.write("v2.0 raw\n")
        for f in range(2 ** (len(flagsDict) - 1)):
            for entry in entryList:
                if entry[1] == f:
                    mempos += 1
                    fileOut.write(hex(entry[2])[2:])
                    if linepos == 15:
                        fileOut.write('\n')
                        linepos = 0
                    else:
                        fileOut.write(' ')
                        linepos += 1
            while mempos < 2 ** 8 * (f + 1):
                fileOut.write("0")
                mempos += 1
                if linepos == 15:
                    fileOut.write('\n')
                    linepos = 0
                else:
                    fileOut.write(' ')
                    linepos += 1

    with open("AssemblyManifest.txt", "w") as fileOut:
        fileOut.write("Assembly Code Manifest")
        fileOut.write("\n")
        fileOut.write("CODE : BINARY - DECIMAL - HEX")
        fileOut.write("\n")
        for k in assemblyEncoding:
            out = str(k) + " : " + str(bin(int(assemblyEncoding[k], base=16)))[2:] + " - " + str(
                int(assemblyEncoding[k], base=16)) + " - " + str(assemblyEncoding[k])
            fileOut.write(out)
            fileOut.write("\n")
    os.chdir(curPath)


def compilePrograms(assemblyEncoding):
    # Remember where we are and hop over to programs
    curPath = os.getcwd()
    os.chdir(curPath + "/programs")
    # First we'll translate each program to appropriate codes before actually writing them to disk.
    for program in os.listdir(os.getcwd()):
        # Read the program
        with open(program, 'r') as curProgram:
            programList = [l.strip().split() for l in curProgram.readlines() if l != '']
        labels = {}
        variables = {}
        mempos = 0
        programList = [p for p in programList if len(p) > 0]
        programName = programList[0]
        del programList[0]
        # First we want to strip out and map all the labels we've left with #LABEL
        for p in programList:
            if p[0][0] == '#':
                labels[p[0]] = mempos
                del p[0]
                mempos += len(p)
            elif p[0][0] == '$':
                variables[p[0]] = mempos
                del p[0]
                mempos += len(p)
            else:
                mempos += len(p)
        flattenedProgram = []
        for p in programList:
            flattenedProgram = flattenedProgram + p
        # We want to flag all the register codes in a kind of janky way
        regFlags = []
        print(flattenedProgram)
        for i in range(len(flattenedProgram)):
            if flattenedProgram[i] == 'ADD' or flattenedProgram[i] == 'SUB' or flattenedProgram[i] == 'ADDC':
                regFlags.append(i + 1)
        for i in range(len(flattenedProgram)):
            if flattenedProgram[i][0] == '#':
                flattenedProgram[i] = hex(labels[flattenedProgram[i]])[2:]
            elif flattenedProgram[i][0] == '$':
                flattenedProgram[i] = hex(variables[flattenedProgram[i]])[2:]
            elif flattenedProgram[i] in assemblyEncoding.keys():
                flattenedProgram[i] = assemblyEncoding[flattenedProgram[i]]
            elif i not in regFlags:
                flattenedProgram[i] = hex(int(flattenedProgram[i]))[2:]
        # Now we can finally output the program!
        os.chdir(curPath + "/output")
        with open(programName[0], 'w') as fileOut:
            fileOut.write('v2.0 raw\n')
            linepos = 0
            for p in flattenedProgram:
                fileOut.write(p)
                if linepos == 15:
                    fileOut.write('\n')
                    linepos = 0
                else:
                    fileOut.write(' ')
                    linepos += 1
        os.chdir(curPath + "/programs")
        print(flattenedProgram)
    os.chdir(curPath)

# Read in flags, if any
flags = [i for i in sys.argv[1:]]

# Check if the output folder if exists, and if not, create it
if not os.path.isdir(os.getcwd() + "/output"):
    os.mkdir(os.getcwd() + "/output")

# Gather the compiled assembly dictionary
assemblyCompileResult = assemblyCompile()

# Handle the -a flag
if '-a' in flags:
    CPUROMWrite(assemblyCompileResult[0], assemblyCompileResult[1], assemblyCompileResult[2])

# Handle the -da flag
if '-da' in flags:
    ADisplayWrite()

# Compile the programs
compilePrograms(assemblyCompileResult[1])
