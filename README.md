# S1AsmVM
```
usage: VM.py [-h] -f PATH [-n] [-t] [-c] [-l LOG] [-u TEST] [-i] [-o] [-s]
             [-e] [-U]

S1VM

options:
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
  -e, --ExceptOnTestFail
                        after all unittests finish, raises exception if any
                        failed (mainly used for integration)
  -U, --UnittestDebug   turn off unittest feedback to speed up debugging
```
