"""
Acc - Accumolator
Reg - Register
mem - Memory

16-Bit Maschine

set attr - set attr into Reg

add none - Acc = Acc + Reg
sub none - Acc = Acc - Reg
shg none - Acc = Acc shifted greater
shs none - Acc = Acc shifted smaller

lor none - Acc = Acc (logical or) Reg
and none - Acc = Acc (logical and) Reg
xor none - Acc = Acc (logical xor) Reg
not none - Acc = Acc (logical not)

lDA attr - Load mem at attr into Acc
lDR attr - Load mem at attr into Reg
sAD attr - Save Acc into mem at attr
sRD attr - Save Reg into mem at attr

lPA atrr - Load mem pointed to by mem at attr into Acc
lPR atrr - Load mem pointed to by mem at attr into Reg
sAP atrr - Save Acc into mem pointed to by mem at attr
sRP atrr - Save Reg into mem pointed to by mem at attr

out attr - outputs mem at attr
inp attr - inputs  mem at attr

lab attr - define lable
got attr - goto attr
jm0 attr - goto attr if Acc = 0
jmA attr - goto attr if Acc = Reg

jmG attr - goto attr if Acc > Reg (jmG for jump great)
jmL attr - goto atrr if Acc < Reg (jmL for jump less)

jmS attr - goto attr as subroutine (pc gets push to stack)
ret none - return from subroutine (stack gets pop to pc)

pha none - push Acc to stack
pla none - pull from stack to Acc


brk none - stops programm
clr none - clears Reg and Acc

putstr none - print the Acc as ascii


ahm none - allocate a number of word given by the Reg and put a pointer to the base into the Acc
fhm none - free a number of word given by the Reg at the address given by the Acc


plugin attr - runs plugin with name of attr


"""

import time
import glob
import argparse
import traceback
import json
import sys
import os
from dataclasses import dataclass
import operator as oper
from copy import deepcopy

from pprint import pprint

cls         = lambda: print("\033[2J\033[H")
pprintDict  = lambda s: "\n".join([f"{x: <25}\t : {s[x]}".format() for x in s])


xBitSize = 16
xIntLimit = 1 << xBitSize     


class cUtils:
    @staticmethod
    def Error(xMsg):
        print(xMsg)
        sys.exit(0)

    @staticmethod
    def Lst(x):
        return list(map(lambda y: str(y), x))


class cInt:
    _fs = {
        "add"     : oper.add,
        "sub"     : oper.sub,
        "rshift"  : oper.rshift,
        "lshift"  : oper.lshift,
    }

    def __init__(self, xInt = 0, xIntLimit = xIntLimit):
        self.x : int = xInt
        self.l : int = xIntLimit

    @classmethod
    def _build(cls):
        for f in cls._fs:
            setattr(cls, f'__{f}__',   cls._makeAttr(f))
            setattr(cls, f'__i{f}__', cls._makeIAttr(f))        

    @staticmethod
    def _makeAttr(f):
        return lambda self, v: self.op(v, cInt._fs[f])

    @staticmethod
    def _makeIAttr(f):
        return lambda self, v: self.iop(v, cInt._fs[f])

    def op(self, v, f):
        return f(self.x, int(v)) % self.l
        
    def iop(self, v, f):
        self.x = self.op(v, f)
        return self
        
    #call used to set value
    def __call__(self, v):    self.x = self.op(v, lambda x,y:y)
    def __int__(self): return self.x
    def __str__(self): return str(self.x)
    
    #copy
    def c(self):
        return cInt(xInt = self.x, xIntLimit=self.l)

cInt._build()    
    
class cConfig:
    NoNL         = False
    DisplayTime  = False
    PrintCommand = False
    Log          = None
    Test         = None
    
    @classmethod
    def ReadArgs(self, xArgs):
        for x in ["NoNL", "DisplayTime", "PrintCommand", "Log", "Test"]:
            xSetng = getattr(xArgs, x)
            setattr(self, x, xSetng)
    
    
    
class cProg:
    @dataclass
    class cInst:
        xOp  : "" = None
        xArg : "" = 0
        
        def __call__(self):
            self.xOp(cEnv, int(self.xArg))
            
        def __str__(self):
            return f'{self.xOp.__name__[1:]} {self.xArg}'
        
        def LabRes(self, xLabels):
            if self.xArg.isdigit(): return #good
            elif self.xArg not in xLabels: 
                cUtils.Error(f"Invaild Label: {self.xArg}")
                
            self.xArg = xLabels[self.xArg]

    xInsts = []
    xLabels = {}
    xTests = {}
    
    def __init__(self, xRaw):
        spce = lambda x: x.replace("  ", " ").strip()
        xLines = [xs.split(" ") for x in xRaw.split("\n") if len(xs := spce(x)) > 0 and xs[0] != '"']

        while len(xLines) > 0:
            #parse line and discard
            (xOpRaw, *xArgsList) = xLines.pop(0) + ['0']
            xOp = xOpRaw.lower()
            xArgs = xArgsList[0]

            #check for label
            if xOp == "lab":
                #add to mapper and continue
                self.xLabels[xArgs] = len(self.xInsts)
                continue
            
            
            #check if op exists
            xOpMName = 'f' + xOp
            if not hasattr(cProg.cImpl, xOpMName):
                cUtils.Error(f"Invaild Instruction: '{xOp}'")
                continue
            
            self.xInsts.append(self.cInst(
                xOp  = getattr(cProg.cImpl, xOpMName),
                xArg = xArgs
            ))
                        
        #resolve labels
        for x in self.xInsts:
            x.LabRes(self.xLabels)
            
        #search unittests
        if cConfig.Test:
            self.xTests = {
                i: self.xLabels[i] 
                for i in self.xLabels 
                if i.startswith(cConfig.Test)
            }
    
    #command implementations
    class cImpl:        
        def fset(self, x): self.Reg(x)
        
        def fadd(self, x): self.Acc += self.Reg
        def fsub(self, x): self.Acc -= self.Reg
        def fshg(self, x): self.Acc(self.Acc << 1)
        def fshs(self, x): self.Acc(self.Acc >> 1)
        def flor(self, x): self.Acc(self.Acc.op(self.Reg, lambda x,y: x|y))
        def fand(self, x): self.Acc(self.Acc.op(self.Reg, lambda x,y: x&y))
        def fxor(self, x): self.Acc(self.Acc.op(self.Reg, lambda x,y: x^y))
        def fnot(self, x): self.Acc(xIntLimit - self.Acc)

        def flda(self, x): self.Acc(self.xMem[x])
        def fldr(self, x): self.Reg(self.xMem[x])
        def fsad(self, x): self.xMem[x](self.Acc)
        def fsrd(self, x): self.xMem[x](self.Reg)

        def flpa(self, x): self.Acc(self.xMem[int(self.xMem[x])])
        def flpr(self, x): self.Reg(self.xMem[int(self.xMem[x])])
        def fsap(self, x): self.xMem[int(self.xMem[x])](self.Acc)
        def fsrp(self, x): self.xMem[int(self.xMem[x])](self.Reg)

        def fout(self, x):
            xEnd = "" if cConfig.NoNL else "\n"
            print(int(self.xMem[x]), end = xEnd)

        def finp(self, x):
            print("inp too lazy")
        
        def fgot(self, x):                                      self._jmp(self, x)
        def fjm0(self, x): 
                            if int(self.Acc) == 0:              self._jmp(self, x)
        def fjma(self, x): 
                            if int(self.Acc) == int(self.Reg):  self._jmp(self, x)
        def fjmg(self, x): 
                            if int(self.Acc) > int(self.Reg):   self._jmp(self, x)
        def fjml(self, x): 
                            if int(self.Acc) < int(self.Reg):   self._jmp(self, x)
        
        def fbrk(self, x): self.xRun = False
        def fclr(self, x):
            self.Acc(0)
            self.Reg(0)
        
        def fjms(self, x):
            xNextInst = (self.xProgIndex + 1) << 1
            self.xStack.append(xNextInst)
            self._jmp(self, x)
        
        def fret(self, x):
            self._slen(self, "Stack Underflow")
            self._jmp(self, self.xStack.pop() >> 1)

        def fpha(self, x): 
            self.xStack.append(self.Acc.c())

        def fpla(self, x):
            self._slen(self, "Stack Underflow")
            self.Acc(self.xStack.pop())
    
        def fputstr(self, x):
            print(chr(int(self.Acc)), end = "", flush = True)
            
        def fahm(self, x):
            xAllocSize = int(self.Reg)
            
            #find the correct number of word in a row that are free
            xBasePointer = None
            for xHeapIndex in range(self.xHeapStartAddress, self.xHeapStartAddress + self.xHeapSize):
                #terminate the loop if the xHeapIndex plus the size that the memory row need to by is greater than the heap itself
                #because any check would be out of range and thus useless anyway
                if xHeapIndex + xAllocSize > self.xHeapStartAddress + self.xHeapSize:
                    break

                #otherwise check for a matching row
                if all([xHeapIndex + xCheckIndex not in self.xHeapAlloc for xCheckIndex in range(xAllocSize)]):
                    xBasePointer = xHeapIndex
                    break
            
            if xBasePointer is None:
                cUtils.Error("Heap out of memory")
                
            for xAddrIndex in range(xBasePointer, xBasePointer + xAllocSize):
                #append all the memory addresses to the alloc list, in order for them to properly freed 
                self.xHeapAlloc.append(xAddrIndex)
                
                #and reset the address, just for safety
                self.xMem[xAddrIndex](0)
            
            #override the Acc to return the memory address to the user
            self.Acc(xBasePointer)
            
        def ffhm(self, x):
            xFreeSize = int(self.Reg)
            xFreeBase = int(self.Acc)
            
            for xFreeAddrIndex in range(xFreeBase, xFreeBase + xFreeSize):
                if xFreeAddrIndex in self.xHeapAlloc: 
                    self.xHeapAlloc.remove(xFreeAddrIndex)
                
                self.xMem[xFreeAddrIndex](0)

    def Time(self):
        return time.time() - self.xStartTime

    def Test(self):
    
        xFailTotal = 0
        for (xName, xTest) in self.xTests.items():
            #init env
            xOoB = (len(self.xInsts) + 1) * 2 #out of bounds
            
            cEnv.xProgIndex = xTest
            cEnv.Acc(0)
            cEnv.Reg(0)
            cEnv.xHeapAlloc = []
            cEnv.xStack = [cInt(xInt = xOoB)] #out of bounds return value to make run() exit
            for i in range(xIntLimit): cEnv.xMem[i](0)
            cEnv.Run = True
            
            #run test
            self.Run()
                        
            #check test evaluation
            xTestEval = int(cEnv.xStack[0])
            if xTestEval == 0:
                print(f"'{xName}' failed")
                xFailTotal += 1
        
        print(f'Total fails: {xFailTotal}')
        if xFailTotal == 0: print("All tests passed")


    def Run(self):
        xLogFile = []
        xMemOld = []
        self.xStartTime = time.time()
        
        try:
            xCycleCount = 0
            while cEnv.xRun and cEnv.xProgIndex < len(self.xInsts):

                #save mem for mem diff
                if cConfig.Log: xMemOld = [i.x for i in cEnv.xMem]

                #actual vm call                                
                (xInst := self.xInsts[cEnv.xProgIndex])()            
                if cConfig.PrintCommand: print(xInst)

                #render log
                if cConfig.Log:
                    #mem delta
                    xMemDiff = { i : (cEnv.xMem[i].x, xMemOld[i]) 
                                for i in range(xIntLimit) 
                                if xMemOld[i] != cEnv.xMem[i].x
                            }
                    
                    xLogFile += [
                        f'[{str(self.Time())[:10]}] {cEnv.xProgIndex}: {xInst}',
                        f'\tAcc: {int(cEnv.Acc)}',
                        f'\tReg: {int(cEnv.Reg)}',
                        f'\tHAl: {cUtils.Lst(cEnv.xHeapAlloc)}',
                        f'\tStk: {cUtils.Lst(cEnv.xStack)}',
                        f'\tMem: {str(xMemDiff)}'
                                ]

                cEnv.xProgIndex += 1
                xCycleCount += 1

        except KeyboardInterrupt:
            pass
        
        if cConfig.DisplayTime:
            print(f"Execution took {str(xCycleCount)} cycles and {self.Time()} seconds")

        if cConfig.Log:
            with open(cConfig.Log, "w") as xFile:
                xFile.write('\n'.join(xLogFile))

    
class cEnv:
        
    Acc = cInt()
    Reg = cInt()

    xHeapStartAddress = xIntLimit // 2
    xHeapSize = xIntLimit - xHeapStartAddress
    
    #memory addresses allocated on the heap
    xHeapAlloc = [] 
    xMem = [cInt() for _ in range(xIntLimit)]
    xStack = []
            
    xProgIndex = 0
    xRun = True

    def _jmp(self, x): self.xProgIndex = x - 1
    def _slen(self, xMsg): #error on empty string
        if len(self.xStack) == 0:
            cUtils.Error(xMsg)



class cMain:    
    @classmethod
    def ParseArgs(self):
        xArgParser = argparse.ArgumentParser(description = "S1AsmVM")
    
        xArgParser.add_argument("-f", "--file", type=str, dest="path", action="store", nargs=1, required=True, help = "source file")
        xArgParser.add_argument("-n", "--NoNL", dest="NoNL", action="store_true", help = "'out' instruction will not put newline")
        xArgParser.add_argument("-t", "--Time", dest="DisplayTime", action="store_true", help = "display execution time")
        xArgParser.add_argument("-c", "--PrintCommand", dest="PrintCommand", action="store_true", help = "print the command being currently executed")
        xArgParser.add_argument("-l", "--Log", dest="Log", action="store", help = "log vm state in file")        
        xArgParser.add_argument("-u", "--Unittest", dest="Test", action="store", help = "search for and run unittest given a namespace")
        return xArgParser.parse_args()
    
    @classmethod
    def Main(self):
        xArgs = self.ParseArgs()
        cConfig.ReadArgs(xArgs)
    
        xPath = next(iter(xArgs.path))
        if not os.path.isfile(xPath):
            cUtils.Error(f"Invaild Path: {xPath}")
    
        with open(xPath, "r") as xFD:
            xFile = xFD.read()

        
        xProg = cProg(xFile)
        xProg.Test() if cConfig.Test else xProg.Run()
        
            
if __name__ == '__main__':
    cMain.Main()