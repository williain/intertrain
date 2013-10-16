#TODO: Can't get this working with python 3.1...
#import os, inspect,importlib
#package=os.path.dirname(
#  inspect.getfile(inspect.currentframe())
#).replace('/','.').replace('\\','.')
#for file in [file for file in os.listdir(
#  os.path.dirname(inspect.getfile(inspect.currentframe()))
#  ) if not file == '__init__.py' and
#    not file.endswith('.pyc') and
#    not file.startswith('.')
#]:
#    print("DEBUG:",importlib.__import__(__name__+"."+file))

#Until I can get it working, you'll need to add your sounder here:
import plat.windows_sounder, plat.posix_sounder
