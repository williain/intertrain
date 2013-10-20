#!/usr/bin/python3

import sys,logging

sys.path.append('./lib')
import exercise,routine,guide

max_line=79

guide=guide.Guide()
guide.load_file("data/exercises/kettlebell.yaml")
routinefile=routine.RoutineFile()
routinefile.add_guide(guide)
routine=routinefile.load_file("data/routines/upperbody2")

logging.basicConfig(format='%(message)s')
logging.getLogger('exercise').setLevel(logging.INFO)

duration_string=str(int(routine.get_total_time()/60))+"'{0:02d}\"".format(routine.get_total_time()%60)

print("*"*70)
print("*",routine.get_name(),"("+duration_string+")")
desc=routine.get_description()
i=0
while i<len(desc):
    full_line=desc[i:i+max_line+1]
    if len(full_line)==max_line+1:
        last_word=full_line.rindex(' ')
        if last_word==0: last_word=len(full_line)
        line=full_line[:full_line.rindex(" ")]
    else:
        line=full_line
    print("*",line)
    i=i+len(line)+1
print("*"*70)

routine.start()
