import sys, os

def parse_microcode():
    pass

def parse_flags():
    pass

def parse_assembly():
    pass

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
