#!/usr/bin/python3

import sys,logging

sys.path.append('./lib')
import exercise

standard_length=60
standard_rest=10
loglevel=logging.INFO

description="Kettle bell upper body exercises, level 1"

exercises=(("Clean to right shoulder", None, None),
	("Clean to left shoulder", None, None),
	("Right arm overhead press (no crouch)", None, None),
	("Left arm overhead press (no crouch)", None, None),
	("Right arm overhead extension with opposite lunge", None, None),
	("Left arm overhead extension with opposite lunge", None, None),
	("Kettle bell swing", None, 0))

# Exercise 1: Clean to right shoulder
# Start in a standing crouch with the kettle bell suspended between the legs
# Lift the kettlebell to the shoulder as you breathe in, and return it to
# the clean position as you breathe out

# Exercise 2: Clean to left shoulder
# As exercise 1, but to your left shoulder

# Exercise 3: Right arm overhead press (no crouch)
# Start with the kettle bell on the right shoulder, and raise it up as you
# breath in to full extension.  As you breathe out let the kettle bell slowly
# descend, to rest on your right shoulder as you repeat the exercise

# Exercise 4: Left arm overhead press (no crouch)
# As exercise 3, but using your left hand.

# Exercise 5: Right arm overhead extension with opposite lunge
# Hold the kettle bell in your right hand, suspended over your head.
# Stepping forward with the left leg, lunge forward while keeping the kettle
# bell suspended, then step back to repeat.

# Exercise 6: Left arm overhead extension with opposite lunge
# As exercise 5, but holding the kettle bell overhead in your left hand and
# lunging with your right leg.

# Exercise 7: Kettlebell swing
# Start with the kettle bell on the ground around a foot ahead of you.  Crouch
# down and grab the kettle bell with both hands.  Still crouched, let the
# kettle bell swing back and let your arms hit your inner thighs.  Once it is
# at its apex, push forward with your back side, launching the kettle bell
# forward and up as you continue to hold it.  As the kettle bell reaches its
# upper apex, go into another standing crouch to allow you to repeat the swing.
# Tune the swing so that the kettle bell rises to shoulder height at its top
# apex

logging.basicConfig(format='%(message)s')

exercise_objects=[]
duration=0

for e in exercises:
	length=e[1]
	rest=e[2]
	if length == None:
		length=standard_length
	if rest == None:
		rest=standard_rest
	ex=exercise.Exercise(e[0], length, rest, loglevel=loglevel)
	exercise_objects.append(ex)
	duration+=length+rest+ex.read_delay

duration_string=str(int(duration/60))+"'{0:02d}\"".format(duration%60)

print("*"*70)
print("*",description,"("+duration_string+")")
print("*"*70)

for e in exercise_objects:
	e.start()
