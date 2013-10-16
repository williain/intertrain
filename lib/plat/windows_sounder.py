import sounderinterface

@sounderinterface.register
class WindowsSounder(sounderinterface.SounderInterface):
    osname='nt'

    def __init__(self):
        print("Sorry, windows sound support is not yet implemented")

    def play(self,soundfile):
        pass

    def stop(self):
        pass
