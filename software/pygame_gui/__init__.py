import subprocess
AUTHORS = ["Donatien Vachette"]
NAME = "pygame-gui"
required = [
    "pygame",
    "pygame-vkeyboard",
]
__installed_modules = subprocess.run("pip freeze", shell=True, capture_output=True).stdout.decode('utf-8').lower()
for mod in required:
    if mod not in __installed_modules:
        print(mod,"is not installed")
        subprocess.run("pip install {}".format(mod),shell = True)

del __installed_modules
from .main import *
import pygame_vkeyboard
import pygame


if not pygame.get_init():
    pygame.init()
print(f'Module {NAME} by {", ".join(AUTHORS)}.')