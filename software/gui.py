import pygame_gui as pgui
import os
import pygame
import random
import time
import sys

# Constantes des dossier de l'application
MUSICS_FOLDER = os.path.join(os.getcwd(), "software", "musics")
SOUNDS_FOLDER = os.path.join(os.getcwd(), "software", "sounds")
# The folder with all the images assets
IMAGES_FOLDER = os.path.join(os.getcwd(), "software", "images")

# * code des fonctions
def second():
    main["label_hour"].configure(text_value=str(int(main.duration)))
def foo():
    main.play_sound("click.tick")
    print("foo")
    second()
# Initialiser la fenêtre
main = pgui.Window("#000000")
# charger les musiques
main.load_music_folder(MUSICS_FOLDER)
main.load_sound_folder(SOUNDS_FOLDER)

# * Bouton pour quitter (Ne pas enlever, ou alors mettre un autre moyen de quitter)
main["stop_button"] = pgui.ButtonImage(
    position=(0, 0),
    text=" ",
    fg="#FF0000",
    onclick=main.stop,
    text_size=10,
    path=os.path.join(IMAGES_FOLDER, "close.png"),
)
main["label_hour"] = pgui.Label(
    position=(400, 0),
    size=(200, 100),
    text="",
    bg="#00FF00",
    fg="#0000FF",
    text_size=50,
)
main["input"] = pgui.TextInput(
    position=(300, 300),
    size=(300, 100),
    bg="#673829",
    fg="#000000",
    text_size=50,
)
main["button"] = pgui.Button(
    position=(0, 100),
    text="foo",
    bg="#0000FF",
    fg="#FF0000",
    onclick=foo,
    text_size=50,
    size=(200, 100),

)
main.tick.add(second)
main.run()
pygame.quit()
sys.exit()