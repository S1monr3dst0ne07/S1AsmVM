# S1AsmVM
```
usage: VM.py [-h] -f PATH [-n] [-t] [-c] [-l LOG] [-u TEST] [-i] [-o] [-s]

S1VM

optional arguments:
  -h, --help            show this help message and exit
  -f PATH, --file PATH  source file
  -n, --NoNL            'out' instruction will not put newline
  -t, --Time            display execution time
  -c, --PrintCommand    print the command being currently executed
  -l LOG, --Log LOG     log vm state in file
  -u TEST, --Unittest TEST
                        search for and run unittest given a namespace
  -i, --Interact        run semi-python interactive environment
  -o, --Optimize        optimize execution
  -s, --PrintSub        print sub calls
```