#!/usr/bin/python3

helptext="""\
Usage: test_exercise.py [-h] [-v] filename

Check that an exercise file is a valid set of exercises

Positional arguments:
 filename   The name of the exercise file to test

Optional arguments:
 -v         Print more verbose output.  By default this tool only
            prints out whether it could parse the file or not.
            With -v it prints out a short summary of each exercise.
            With -vv it prints out full details of each exercise.
"""

import sys,yaml,getopt
sys.path.append('../../lib')
import guide,exceptions

def test_file(filename,verbose):
    testguide=guide.Guide()
    try:
        testguide.load_file(filename)
        if verbose>0:
            for ex in sorted(testguide.get_exercise_ids()):
                print("="*78)
                exercise=testguide.get_exercise(ex)
                __display_string("{0}: {1}".format(ex,exercise.name))
                __display_string(exercise.desc)
                if verbose==1:
                    __display_string("Tips: {0}".format(len(exercise.tips)))
                else:
                    for tip in exercise.tips:
                        __display_string("Tip: "+tip)

            print("="*78)
        print("File {1}: Parsed {0} exercises OK".format(
          len(testguide.get_exercise_ids()),filename
        )) 
    except (exceptions.ParseError)  as e:
        print("Parse failure:",str(e))
    except IOError as e:
        print("File error:",str(e))

def parse_opts(raw_args):
    opts,args=getopt.gnu_getopt(raw_args,'hv+',['help','verbose+'])
    verbose=0
    for opt,a in opts:
        if opt=='-v' or opt=='-verbose':
            verbose+=1
        elif opt=='-h' or opt=='-help':
            print(helptext)
            return(0)

    if len(args)>1:
        print("Error: Too many arguments; expected only one (filename)")
        return(1)
    elif len(args)<1:
        print("Error: Too few arguments; expected the test filename\n")
        print(helptext)
        return(1)
    else:
        filename=args[0]

    return(filename,verbose)

def __display_string(string):
    words=string.split(" ")
    pos=0
    for word in words:
        pos+=len(word)
        if pos<78:
            print(word,end=' ')
            pos+=1
        else:
            pos=len(word)+1
            print('')
            print(word,end=' ')
    print('')

if __name__=="__main__":
    opts=parse_opts(sys.argv[1:])
    if opts==0:
        exit(0)
    elif opts==1:
        exit(1)
    else:
        (filename, verbose)=opts
    test_file(filename, verbose)
