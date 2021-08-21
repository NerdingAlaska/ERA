# ERA
The home of the Eater-inspired Research Architecture, a simulated 8-bit computer

Largely building on previous work ERA will support EROS, the Eater-inspired Research Operating System.
At present time ERA is being constructed with Logisim Evolution

https://github.com/logisim-evolution/logisim-evolution

ERA will have 64KB of RAM, 4GB of HDD, and eventually a 256B CPU cache.
At present time there are no plans to make multiple cores.
Eventually there will be efforts to write a very simple native compiler, but until then the plan is to learn how to aim LLVM at the architecture so that EROS can be written in a higher level programming language.
The goals of the project are presently:
-build ERA in Logisim Evolution and verify the assembler from previous work that is written in Python.
-make the assembler better and writing some tests for ERA to make sure everything works as intended.
-figure out how to use tools to make an LLVM backend aimed at ERA
-make videos about all of this
-expand ERA assembly instructions to permit subroutines
