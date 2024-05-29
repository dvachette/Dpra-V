import pygame_gui as pgui
import os
import pygame
import random
import time



# The folder where all the sounds are located
SOUNDS_FOLDER = os.path.join(os.getcwd(), "software", "sounds")
# The folder with all the images assets
IMAGES_FOLDER = os.path.join(os.getcwd(), "software", "images")

pre = time.time()
def move():
    global pre
    
    if time.time() - pre >0.5:
        main["stop_button"].configure(position=(random.randint(0,500),random.randint(0,500)))
        pre = time.time()
def second():
    main["label_hour"].configure(text_value=str(main.duration))


main = pgui.Window("#000000")


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
main.tick.add(second)
main.tick.add(move)
main.run()
