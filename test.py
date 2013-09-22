#!/usr/bin/python3

import sys
import logging

sys.path.append('./lib')

import countdown
import exercise

print("+++ Test countdown")
countdown.Test()
logging.getLogger('countdown').setLevel(logging.ERROR)
print("+++ Test exercise")
exercise.Test()
