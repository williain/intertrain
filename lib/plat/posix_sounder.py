import sounderinterface
import subprocess

@sounderinterface.register
class LinuxSounder(sounderinterface.SounderInterface):
    osname='posix'

    def __init__(self):
        self.lastsound = None
 
    def play(self,soundfile):
        """play a soundfile and return immediately"""
        self.stop()
        self.lastsound=subprocess.Popen(
          ['mplayer', soundfile],
          stdout=open('/dev/null','w'),
          stderr=open('/dev/null','w')
        )

    def stop(self):
        """clear any currently playing sound"""
        if self.lastsound!=None:
            self.lastsound.terminate()
            self.lastsound=None
