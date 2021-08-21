import sys, os

'''
This program is for the purpose of compiling all the necessary files to load into bb0.3 in order to have it run.
The program has strict expectations on what the files it relies on will contain, and this specification will be
laid out here, to be documented further in a centralized documentation. 

The program will seek out three different folders in the directory where it is running: sys, display, and programs.

The sys folder will contain three files: microcode.txt, assembly.txt, and flags.txt

microcode.txt will be expected to be formatted as such:
IO,0 Instruction register out
II,2 Instruction register in
RO,3 RAM out
.
.
.
the first integer is the control line that the microcode instruction will light up, and the second is the symbol that represents 
that microcode instruction. The two are separated by only a comma. This allows one to define microcode instructions as whatever
symbols one would like. Comments may be added simply by providing a space after the instruction definition, and the program will
ignore it.

assembly.txt will be expected to be formatted as such:
LDA 00 RO,AI RAM out, A register in
ADD 00 RO,BI RAM out, B register in
ADD 00 EO,AI Sum out, A register in
LDB 00 RO,BI RAM out, B register in
.
.
.
the first word is the symbol that represents this assembly code instruction. This will define what assembly code the compiler will
recognize in the programs folder. The second entry is the flag indicators, which can be used to specify other operations for each 
command depending on the values in the status register. At the moment there are two flags which are available, Carry and Zero, respectively
therefore only two entries that need to be accounted for. If a command will be executed the same no matter what the flags say, an entry
of 'NOFLAG' while if a command will be executed when the Carry and Zero flags are set the entry would read 'C,Z'
The order of the flag codes is irrelevant, as the definition of their value comes from the flags.txt file in the sys folder, which
the compiler will parse.
The third entry is the group of microcode instructions for that step of the assembly instruction.
Each instruction is separated by a comma, and there can be any number of valid microcode instructions per assembly instruction step.
At the moment the compiler will not provide any cursory code for manipulating the step counter and program counter, leaving all of the
details to the programmer.

flags.txt will be expected to be formatted as such:
C 1 Carry flag
Z 2 Zero flag
.
.
.
the first word is the symbol that represents the flag code that will be matched in the assembly.txt file. The integer value is the place
in the status register that the flag occupies. Comments can be added after a space and will be ignored by the compiler. 

When the -a flag is set the compiler will first parse microcode.txt into a dictionary which it will use to generate the hex codes for each 
assembly instruction step, outputting a new CPUROM to be uploaded into bb's CPU ROM. It will also generate a file that maps the assembly instructions
to the binary codes that the compiler assigns. It assigns these simply by the order in which they are listed in assembly.txt. flags.txt will 
be parsed to ensure that the CPUROM will be created with the appropriate microcode for the appropriate flags.
Whether or not the -a flag is set the program will now parse the assembly.txt file into a dictionary that will be used to translate the programs
in the programs folder.

The display folder will be expected to have two files: Fpre.txt and Apre.txt 

Fpre.txt will not be defined at the moment, but will be addressed in the future with a much more efficient and human-friendly method of loading
all the possible 256 pre-set freeform LED matrix frames.

Apre.txt will be expected to be formatted as such:
0,bb0.3 :]
1,Error X3
2,Overflow
.
.
These define the preset ASCII messages that can be accessed from the A preset mode of the display chip. Because the LED matrix display only supports
8 characters we can define the the first integer as the number used to call that message, and then a comma followed by the 8 characters to store.

If the -da flag is set the compiler will process the Apre.text file and generate the 8 ROM chips needed to store all the preset ASCII messages.
This operation also requires ASCIIencoding.txt to be present in the display folder. 

ASCIIencoding.txt will be expected to be formatted as such:
33,000000000000011101000000
34,000000011000000000011000
35,000000011111001010011111
.
.

The exact formatting of the binary string is given in the documentation. 

The programs folder is expected to hold all of the user-defined programs that one wishes to include in bb's RAM. bb assembly code is defined in the 
documentation, and each program file should be named in the convention programname.txt. 
Each program file will be evaluated to ensure that it can be compiled, and assuming that it is free of syntax errors the compiler will compile the
program and generate the program manifest so that there is a map of available programs and what memory address they can be accessed at. 
Additionally, the compiler will recognize comments and labels to make the process of defining jumping much simpler for the user. 

Each program file will be expected to be formatted as such:
#Label1 Defining a label
LDA P10000000 Loading register A from program RAM
ADD P10000001 Adding to register A a value from program RAM
WRI P10000000 Writing back to program RAM the new sum
JMP #Label1 Jump back to the label we defined earlier

The compiler will take care of any necessary address substitutions for the labels, as well as any other translation that needs to occur. 
For the moment the compiler will not attempt to optimize any code, but simply translate the assembly instructions into the correct codes for the RAM.

The compiler will generate the compiledRAM file as well as the programManifest.txt so that the user can see how the compiler has mapped the programs
into memory.
'''


class bbSyntaxError(Exception):
    pass


def assemblyCompile():
    # Seek out the sys folder
    curPath = os.getcwd()
    nextPath = curPath + '/sys'
    os.chdir(nextPath)

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


def ASCIIdecode(character, encoding):
    try:
        return (encoding[character])
    except KeyError:
        print("Encoding error: invalid ASCII")


def ADisplayWrite():
    # Remember where we are and hop over to display folder
    curPath = os.getcwd()
    os.chdir(curPath + "/display")
    # Grab the raw preset messages
    with open('Apre.txt', 'r') as fileIn:
        contents = [l for l in fileIn.readlines()]
    # Grab the encoding and make it into a dictionary to pass to the encoding function
    with open('ASCIIencoding.txt', 'r') as fileIn:
        encoding = {int(e[0]): hex(int(e[1], base=2))[2:] for e in [l.strip().split(',') for l in fileIn.readlines()]}
    os.chdir(curPath)
    # Process the contents into the correct list
    contents = [l for l in zip([a.split(',')[0] for a in contents], [b.strip()[-8:] for b in contents])]
    os.chdir(curPath + "/output")
    # Nested files open to get the 8 ROM chips
    with open('APreROM0', 'w') as R0:
        with open('APreROM1', 'w') as R1:
            with open('APreROM2', 'w') as R2:
                with open('APreROM3', 'w') as R3:
                    with open('APreROM4', 'w') as R4:
                        with open('APreROM5', 'w') as R5:
                            with open('APreROM6', 'w') as R6:
                                with open('APreROM7', 'w') as R7:
                                    # Set the initial file needs
                                    R0.write("v2.0 raw\n")
                                    R1.write("v2.0 raw\n")
                                    R2.write("v2.0 raw\n")
                                    R3.write("v2.0 raw\n")
                                    R4.write("v2.0 raw\n")
                                    R5.write("v2.0 raw\n")
                                    R6.write("v2.0 raw\n")
                                    R7.write("v2.0 raw\n")
                                    mempos = 0
                                    for l in contents:
                                        R0.write(ASCIIdecode(ord(l[1][7]), encoding))
                                        R1.write(ASCIIdecode(ord(l[1][6]), encoding))
                                        R2.write(ASCIIdecode(ord(l[1][5]), encoding))
                                        R3.write(ASCIIdecode(ord(l[1][4]), encoding))
                                        R4.write(ASCIIdecode(ord(l[1][3]), encoding))
                                        R5.write(ASCIIdecode(ord(l[1][2]), encoding))
                                        R6.write(ASCIIdecode(ord(l[1][1]), encoding))
                                        R7.write(ASCIIdecode(ord(l[1][0]), encoding))
                                        mempos += 1
                                        if mempos == 15:
                                            R0.write('\n')
                                            R1.write('\n')
                                            R2.write('\n')
                                            R3.write('\n')
                                            R4.write('\n')
                                            R5.write('\n')
                                            R6.write('\n')
                                            R7.write('\n')
                                            mempos = 0
                                        else:
                                            R0.write(' ')
                                            R1.write(' ')
                                            R2.write(' ')
                                            R3.write(' ')
                                            R4.write(' ')
                                            R5.write(' ')
                                            R6.write(' ')
                                            R7.write(' ')
                                            mempos += 1
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