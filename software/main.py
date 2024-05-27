# Importations
# You need to run pip install pygame (windows) or python3 -m pip3 install pygame (unix)
import pygame_vkeyboard as vkboard
import pygame
import sys
import os
import time

# Initialisation
if not pygame.get_init():
    pygame.init()

# Constants

# The main surface, which will be used for the program
SURFACE = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# The folder where all the sounds are located
SOUNDS_FOLDER = os.path.join(os.getcwd(), "software", "sounds")
# The folder with all the images assets
IMAGES_FOLDER = os.path.join(os.getcwd(), "software", "images")
# The two states allowed for "Button" and "ButtonImage"
ALLOWED_STATES = [
    "enabled",
    "disabled",
]

# All the texts are using the same font
def FONT(size: int) -> pygame.font.SysFont:
    """
    FONT(size:int)->pygame.font.Sysfont
    This function is used to get the font used by all the texts in the GUI
    """
    font = pygame.font.SysFont("Aptos", size)
    return font


# Error classes
class NotAllowedError(Exception):
    """
    Base Exception raised when you are not allowed to do a thing,
    such as set a property attribute which is not meant to
    """

    pass


# Widget classes
class Widget:
    """
    Base exception for widgets
    All widgets needs to have a __draw__(self,surf_dest)
    and a __feed__(self,events) method defined
    """

    def __draw__(self, surf):
        raise NotImplementedError

    def __feed__(self, events):
        raise NotImplementedError


class Image(Widget):
    """
    Image(
        *,
        position:
        tuple,
        path:str,
        transparency:int=255,
        resize:tuple|None=None
    )
    This class is used to display images
    """

    def __init__(
        self,
        *,
        position: tuple,
        path: str,
        transparency: int = 255,
        resize: tuple | None = None,
    ) -> None:
        self.__image = pygame.image.load(path)
        self.__position = position
        self.__path = path
        self.__resize = resize
        self.__image.convert_alpha()
        if self.__resize is not None:
            pygame.transform.scale(self.__image, self.__resize)
        self.__surf = pygame.Surface(self.__image.get_size())
        self.__surf.blit(self.__image, (0, 0))
        self.__surf.convert_alpha()
        self.__surf.set_alpha(transparency)

    def __repr__(self):
        return f"""Image object at {self.__position}"""

    def __str__(self):
        return repr(self)

    def __feed__(self, events:list)->None:
        """
        Image.__feed__(events)
        Define how the Image will react to any events
        """
        pass

    def __draw__(self, surf:pygame.surface.Surface):
        """
        Image.__draw__(dest_surf)
        Draw the Image onto the given surface
        """
        surf.blit(self.__surf, self.__position)

class TextInput(Widget):
    def __init__(
        self,
        *,
        position:tuple,
        size:tuple,
        bg:str,
        fg:str,
        text_size:int,
        text_offset:tuple=(0,0),
        transparency:int=255,
    ):
        self.__size = size
        self.__position = position
        self.__layout = vkboard.VKeyboardLayout(vkboard.VKeyboardLayout.AZERTY)
        self.__active = False
        self.text = ""
        self.__bg = bg
        self.__fg = fg
        self.__text_size = text_size
        self.__text_offset = text_offset
        self.__transparency = transparency
        self.__rect = pygame.rect.Rect(*self.__position, *self.__size)
        self.__keyboard = vkboard.VKeyboard(
            SURFACE,
            self.__update_text__,
            self.__layout,
            renderer=vkboard.VKeyboardRenderer.DARK,
            show_text=True,
            joystick_navigation=True,
        )
        
        self.__text_area = Label(
            position=self.__position,
            size=self.__size,
            text=self.text,
            bg=self.__bg,
            fg=self.__fg,
            text_size=self.__text_size,
            text_offset=self.__text_offset,
            transparency=self.__transparency,
        )
        
    def __draw__(self, surf):
        self.__text_area.__draw__(surf=surf)

        rects = self.__keyboard.draw(surface=surf,force=True)
        pygame.display.update(rects)
    def __feed__(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.__rect.collidepoint(*pygame.mouse.get_pos()):
                    self.__active = True
                elif self.__active and not self.__keyboard.get_rect().collidepoint(*pygame.mouse.get_pos()):
                    self.__active = False
            if event.type == pygame.FINGERUP:
                if self.__rect.collidepoint(event.pos):
                    if self.__rect.collidepoint(*event.pos):
                        self.__active = True
                    elif self.__active and not self.__keyboard.get_rect().collidepoint(*event.pos):
                        self.__active = False
        self.__text_area.__feed__(events)
        if self.__active:
            self.__keyboard.enable()
            self.__keyboard.update(events)
        else:
            self.__keyboard.disable()

    def __update_text__(self,text):
        self.__text_area.configure(text_value=text)
class Button(Widget):
    def __init__(
        self: "Button",
        *,
        size: tuple,
        position: tuple,
        text: str,
        bg: str,
        fg: str,
        onclick,
        text_size: int,
        text_offset: tuple = (0, 0),
        transparency: int = 255,
        state: str = "enabled",
    ):
        if state in ALLOWED_STATES:
            self.__state = state
        else:
            raise ValueError("Unrecognized state value, see ALLOWED_STATES")
        self.__text_size = text_size
        self.__position = position
        self.__size = size
        self.__text = text
        self.__bg = bg
        self.__fg = fg
        self.__transparency = transparency
        self.__onclick = onclick
        self.__rect = pygame.Rect(*self.__position, *self.__size)
        self.__text_area = FONT(self.__text_size).render(self.__text, 0, fg)
        self.__surf = pygame.Surface(self.__size)
        self.__surf.fill(bg)
        self.__surf.blit(self.__text_area, text_offset)
        self.__mask = pygame.Surface(self.__size)
        self.__mask.fill("#202020")
        self.__mask.set_alpha(150)
        self.__surf.set_alpha(self.__transparency)

    def configure(
        self,
        text_value=None,
        foreground=None,
        background=None,
        text_size=None,
        text_offset=None,
        transparency=None,
    ):
        if text_value is not None:
            self.__text = text_value
        if foreground is not None:
            self.__fg = foreground
        if background is not None:
            self.__bg = background
        if text_size is not None:
            self.__text_size = text_size
        if text_offset is not None:
            self.__bg = text_offset
        if transparency is not None:
            self.__transparency = transparency

        self.__text_area = FONT(self.__text_size).render(self.__text, 0, self.__fg)
        self.__surf.fill(self.__bg)
        self.__surf.blit(self.__text_area, self.__text_offset)
        self.__surf.set_alpha(self.__transparency)

    def __repr__(self):
        return f"""Button object at {self.__position}"""

    def __str__(self):
        return repr(self)

    def __feed__(self, events):
        clicked = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and self.__state == "enabled":
                if self.__rect.collidepoint(*pygame.mouse.get_pos()):
                    clicked = True
        if self.__rect.collidepoint(*pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(11)
        else:
            pygame.mouse.set_cursor(0)
        if clicked:
            self.__onclick.__call__()

    def __draw__(self, surf):
        surf.blit(self.__surf, self.__position)
        if self.__state == "disabled":
            surf.blit(self.__mask, self.__position)


class Label(Widget):
    def __init__(
        self: "Label",
        *,
        position: tuple,
        size: tuple,
        text: str,
        bg: str,
        fg: str,
        text_size: int,
        text_offset: tuple = (0, 0),
        transparency=255,
    ):
        self.__size = size
        self.__position = position
        self.__text = text
        self.__bg = bg
        self.__fg = fg
        self.__text_size = text_size
        self.__text_area = FONT(self.__text_size).render(self.__text, 0, fg)
        self.__surf = pygame.Surface(self.__size)
        self.__surf.fill(bg)
        self.__surf.blit(self.__text_area, text_offset)
        self.__surf.convert_alpha()
        self.__surf.set_alpha(transparency)
        self.__text_offset = text_offset
        self.__transparency = transparency

    def configure(
        self,
        *,
        text_value=None,
        foreground=None,
        background=None,
        text_size=None,
        text_offset=None,
        transparency=None,
    ):
        if text_value is not None:
            self.__text = text_value
        if foreground is not None:
            self.__fg = foreground
        if background is not None:
            self.__bg = background
        if text_size is not None:
            self.__text_size = text_size
        if text_offset is not None:
            self.__bg = text_offset
        if transparency is not None:
            self.__transparency = transparency

        self.__text_area = FONT(self.__text_size).render(self.__text, 0, self.__fg)
        self.__surf.fill(self.__bg)
        self.__surf.blit(self.__text_area, self.__text_offset)
        self.__surf.set_alpha(self.__transparency)

    def __repr__(self):
        return f"""Label object at {self.__position}"""

    def __str__(self):
        return repr(self)

    def __feed__(self, events):
        pass

    def __draw__(self, surf):
        self.__text_area = FONT(self.__text_size).render(self.__text, 0, self.__fg)
        self.__surf.fill(self.__bg)
        self.__surf.blit(self.__text_area, self.__text_offset)
        self.__surf.convert_alpha()
        self.__surf.set_alpha(self.__transparency)
        surf.blit(self.__surf, self.__position)


class ButtonImage(Widget):
    def __init__(
        self: "Button",
        *,
        position: tuple,
        text: str,
        fg: str,
        onclick,
        text_size: int,
        path,
        text_offset: tuple = (0, 0),
        transparency: int = 255,
        state: str = "enabled",
    ):
        self.__position = position
        self.__text = text
        self.__fg = fg
        self.__onclick = onclick
        self.__text_size = text_size
        self.__image = pygame.image.load(path)
        self.__size = self.__image.get_size()
        self.__transparency = transparency
        self.__rect = pygame.Rect(*self.__position, *self.__size)
        self.__text_area = FONT(self.__text_size).render(self.__text, 0, fg)
        self.__state = state
        self.__mask = pygame.Surface(self.__size)
        self.__mask.fill("#202020")
        self.__mask.set_alpha(150)
        self.__text_offset = text_offset
        self.__image.set_alpha(self.__transparency)
        self.__text_area.set_alpha(self.__transparency)
        self.__collide = pygame.mask.from_surface(self.__image)

    def __repr__(self):
        return f"""ButtonImage object at {self.__position}"""

    def __str__(self):
        return repr(self)

    def __draw__(self, surf):
        surf.blit(self.__image, self.__position)
        surf.blit(
            self.__text_area,
            tuple(p + o for p, o in zip(self.__position, self.__text_offset)),
        )

        if self.__state == "disabled":
            surf.blit(self.__mask, self.__position)

    def __feed__(self, events):
        clicked = False
        if self.__rect.collidepoint(*pygame.mouse.get_pos()):
            local_x, local_y = pygame.mouse.get_pos()
            local_x -= self.__position[0]
            local_y -= self.__position[1]
            for event in events:
                if (
                    event.type == pygame.MOUSEBUTTONUP
                    and self.__state == "enabled"
                    and self.__collide.get_at((local_x, local_y))
                ):
                    clicked = True
            if self.__collide.get_at((local_x, local_y)):
                pygame.mouse.set_cursor(11)
            else:
                pygame.mouse.set_cursor(0)
        if clicked:
            self.__onclick.__call__()


class Line(Widget):
    def __init__(
        self,
        *,
        start: tuple,
        end: tuple,
        color: str,
        width: int = 1,
    ):
        self.__start = start
        self.__end = end
        self.__color = color
        self.__width = width
        self.__topleft = (min(start[0], end[0]), min(start[1], end[1]))
        self.__bottomright = (max(start[0], end[0]), max(start[1], end[1]))

    def __repr__(self):
        return f"""Line object at {self.__topleft}"""

    def __str__(self):
        return repr(self)

    def __feed__(self, events):
        pass

    def __draw__(self, surf):
        pygame.__draw__.line(surf, self.__color, self.__start, self.__end, self.__width)


class Polygon(Widget):
    def __init__(
        self, *, points: list[tuple], color: str, width: int = 1, fill: bool = False
    ):
        if fill:
            width = 0
        self.__points: list = points
        self.__color: str = color
        self.__width: int = width

    def __feed__(self, events):
        pass

    def __draw__(self, surf):
        pygame.__draw__.polygon(surf, self.__color, self.__points, self.__width)


class Window:
    def __init__(
        self: "Window",
        surf: pygame.Surface,
        bg: str,
        fps: int = 60,
    ):
        self.__bg = bg
        self.__FPS = fps
        self.__surf = surf
        self.__elements = dict()
        self.__runing = False
        self.__size = self.__surf.get_size()
        self.tick = set()
        self.__begin = time.time()
        self.__after = list()

    @property
    def duration(self):
        return time.time() - self.__begin

    @duration.setter
    def duration(self, value):
        raise NotAllowedError()

    def __getitem__(self, key):
        return self.__elements[key]

    def __setitem__(self, key, value):
        if issubclass(type(value), Widget):
            self.__elements[key] = value
        else:
            raise TypeError("Not a Widget")

    def __delitem__(self, key):
        del self.__elements[key]

    def draw_elements(self):
        for element in self.__elements.values():
            element.__draw__(self.__surf)

    def update_elements(self, events):
        for element in self.__elements.values():
            element.__feed__(events)

    def run(self):
        self.__runing = True
        self.__clock = pygame.time.Clock()
        while self.__runing:
            self.__surf.fill(self.__bg)
            self.draw_elements()
            events = pygame.event.get()
            self.update_elements(events=events)
            for action in self.tick:
                action.__call__()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.runing = False
                    sys.exit()
            pygame.display.flip()
            self.__clock.tick(self.__FPS)

    def stop(self):
        self.__runing = False


# Fonctions d'appel de boutons


def second():
    main["label_hour"].configure(text_value=str(main.duration))


main = Window(SURFACE, "#000000")


main["stop_button"] = ButtonImage(
    position=(0, 0),
    text=" ",
    fg="#FF0000",
    onclick=main.stop,
    text_size=10,
    path=os.path.join(IMAGES_FOLDER, "close.png"),
)
main["label_hour"] = Label(
    position=(400, 0),
    size=(200, 100),
    text="",
    bg="#00FF00",
    fg="#0000FF",
    text_size=50,
)
main["input"] = TextInput(
    position=(300,300),
    size=(300,100),
    bg="#673829",
    fg="#000000",
    text_size=50,
)
main.tick.add(second)
main.run()
