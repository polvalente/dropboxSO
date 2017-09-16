#!/usr/bin/env python
import os, sys

for i in xrange(1,len(sys.argv)):
    n = sys.argv[i]
    print n, ': ', os.path.getmtime(n)
