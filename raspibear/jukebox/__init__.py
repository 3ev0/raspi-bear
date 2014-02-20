from . import audioplay_pygame

_audioplayer = None

version = "0.1"

def getPlayer():
    global _audioplayer
    if not _audioplayer:
        _audioplayer = audioplay_pygame.AudioPlayer()
    return _audioplayer




