#!/usr/bin/python3

import exceptions

def singleton(typ):
    instances={}
    def get():
        if not typ in instances:
            instances[typ]=typ()
        return instances[typ]
    return get

@singleton
class Sounders(object):
    def __init__(self):
        self.sounders={}

    def register(self,plat,typ):
        """
        Register a type (derived from SounderInterface) against a platform
        string which matches a name returned from 'os.name', e.g. 'posix'
        """
        self.sounders[plat]=typ

    def get_sounder(self,plat):
        if plat in self.sounders:
            return self.sounders[plat]()
        else:
            #TODO Log, not print
            print("Sorry, sounds on platform '{0}' are not supported".format(plat))
            return QuietSounder()

def register(cls):
    """
    A decorator to let you register your class implementing SounderInterface
    against the Sounders database.
    """
    if not 'SounderInterface' in [t.__name__ for t in cls.mro()]:
        raise exceptions.ProtocolError("""\
Classes registering the Sounders database must implement SounderInterface
        """)
    elif hasattr(cls,'osname'):
        Sounders().register(cls.osname,cls)
    elif cls.__name__!='SounderInterface':
        raise exceptions.ProtocolError("""\
To register a class implementing SounderError you must define {0}.osname
        """.format(cls.__name__))
    return cls

@register
class SounderInterface(object):
    def play(self,soundfile):
        """Play a soundfile and return immediately"""
        raise exceptions.ProtcolError(
          "Sounder classes must redefine play(soundfile)"
        )

    def stop(self):
        """Clear any currently playing sound"""
        raise exceptions.ProtocolError("Sounder classes must redefine stop()")

@register
class QuietSounder(SounderInterface):
    osname=None

    def play(self,soundfile):
        pass

    def stop(self):
        pass
