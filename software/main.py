# Comments indications:
# * Important
# TODO
# ! alert
# ? queries
# // deleted code


# Importations
# * You need to run pip install pygame (windows) or python3 -m pip3 install pygame (unix)
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
    def __feed__(self, events: list) -> None:
        """
        Widget.__feed__(events)

        :events:list
        The list of events that the Widget have to handle,
        use Widget.__feed__(pygame.event.get()) for the best support

        Define how the Widget will react to any events
        """
        raise NotImplementedError

    def __draw__(self, surf: pygame.surface.Surface):
        """
        Widget.__draw__(dest_surf)

        Draw the Image onto the given surface

        :surf:pygame.Surface
        You should ALWAYS use the surface given by pygame.display.get_surface()
        """
        raise NotImplementedError


class Image(Widget):
    """
    This class is used to display images

    :position:tuple
    The position of the image

    :path:str
    The path to the image

    :transparency:int
    The transparency of the image, 0 means totaly transparent,
    and 255 totaly opaque

    :resize:tuple
    redim the image to fit the specified size, not recomended 


    """

    def __init__(
        self,
        *,
        position: tuple,
        path: str,
        transparency: int = 255,
        resize: tuple | None = None,
    ) -> None:
        self._image = pygame.image.load(path)
        self._position = position
        self._path = path
        self._resize = resize
        self._image.convert_alpha()
        if self._resize is not None:
            pygame.transform.scale(self._image, self._resize)
        self._surf = pygame.Surface(self._image.get_size())
        self._surf.blit(self._image, (0, 0))
        self._surf.convert_alpha()
        self._surf.set_alpha(transparency)

    def __repr__(self):
        return f"""Image object at {self._position}"""

    def __str__(self):
        return repr(self)

    def __feed__(self, events: list) -> None:
        pass

    def __draw__(self, surf: pygame.surface.Surface):
        surf.blit(self._surf, self._position)
        self._feed

class TextInput(Widget):
    """
    This class is used to create text inputs directly into the window, 
    with a virtual keyboard.


    :position: tuple
    A tuple to specify where the TextInput will be draw

    :size: tuple
    A tuple to specify the size of the TextInput

    :bg: str
    A string to define the background color of the TextInput
    Use html like color code : "#1234AB"

    :fg: str
    A string to define the foreground color of the TextInput
    Use html like color code : "#1234AB"

    :text_size: int
    The size of the text in the render

    :text_offset: tuple
    A tuple to define where the text will be positioned

    :transparency:int
    The transparency of the TextInput's Label, 0 means totaly transparent,
    and 255 totaly opaque

    """

    def __init__(
        self,
        *,
        position: tuple,
        size: tuple,
        bg: str,
        fg: str,
        text_size: int,
        text_offset: tuple = (0, 0),
        transparency: int = 255,
    ):
        self._size = size
        self._position = position
        self._layout = vkboard.VKeyboardLayout(vkboard.VKeyboardLayout.AZERTY)
        self._active = False
        self.text = ""
        self._bg = bg
        self._fg = fg
        self._text_size = text_size
        self._text_offset = text_offset
        self._transparency = transparency
        self._rect = pygame.rect.Rect(*self._position, *self._size)
        self._keyboard = vkboard.VKeyboard(
            SURFACE,
            self.__update_text__,
            self._layout,
            renderer=vkboard.VKeyboardRenderer.DARK,
            show_text=True,
            joystick_navigation=True,
        )

        self._text_area = Label(
            position=self._position,
            size=self._size,
            text=self.text,
            bg=self._bg,
            fg=self._fg,
            text_size=self._text_size,
            text_offset=self._text_offset,
            transparency=self._transparency,
        )

    def __draw__(self, surf):
        self._text_area.__draw__(surf=surf)

        rects = self._keyboard.draw(surface=surf, force=True)
        pygame.display.update(rects)

    def __feed__(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self._rect.collidepoint(*pygame.mouse.get_pos()):
                    self._active = True
                elif self._active and not self._keyboard.get_rect().collidepoint(
                    *pygame.mouse.get_pos()
                ):
                    self._active = False
            if event.type == pygame.FINGERUP:
                if self._rect.collidepoint(event.pos):
                    if self._rect.collidepoint(*event.pos):
                        self._active = True
                    elif self._active and not self._keyboard.get_rect().collidepoint(
                        *event.pos
                    ):
                        self._active = False
        self._text_area.__feed__(events)
        if self._active:
            self._keyboard.enable()
            self._keyboard.update(events)
        else:
            self._keyboard.disable()

    def __update_text__(self, text):
        self._text_area.configure(text_value=text)


class Button(Widget):
    """
    This class is used to display buttons, whose can run a function on a click
    
    """
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
            self._state = state
        else:
            raise ValueError("Unrecognized state value, see ALLOWED_STATES")
        self._text_size = text_size
        self._position = position
        self._size = size
        self._text = text
        self._bg = bg
        self._fg = fg
        self._transparency = transparency
        self._onclick = onclick
        self._rect = pygame.Rect(*self._position, *self._size)
        self._text_area = FONT(self._text_size).render(self._text, 0, fg)
        self._surf = pygame.Surface(self._size)
        self._surf.fill(bg)
        self._surf.blit(self._text_area, text_offset)
        self._mask = pygame.Surface(self._size)
        self._mask.fill("#202020")
        self._mask.set_alpha(150)
        self._surf.set_alpha(self._transparency)

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
            self._text = text_value
        if foreground is not None:
            self._fg = foreground
        if background is not None:
            self._bg = background
        if text_size is not None:
            self._text_size = text_size
        if text_offset is not None:
            self._bg = text_offset
        if transparency is not None:
            self._transparency = transparency

        self._text_area = FONT(self._text_size).render(self._text, 0, self._fg)
        self._surf.fill(self._bg)
        self._surf.blit(self._text_area, self._text_offset)
        self._surf.set_alpha(self._transparency)

    def __repr__(self):
        return f"""Button object at {self._position}"""

    def __str__(self):
        return repr(self)

    def __feed__(self, events):
        clicked = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and self._state == "enabled":
                if self._rect.collidepoint(*pygame.mouse.get_pos()):
                    clicked = True
        if self._rect.collidepoint(*pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(11)
        else:
            pygame.mouse.set_cursor(0)
        if clicked:
            self._onclick.__call__()

    def __draw__(self, surf):
        surf.blit(self._surf, self._position)
        if self._state == "disabled":
            surf.blit(self._mask, self._position)


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
        self._size = size
        self._position = position
        self._text = text
        self._bg = bg
        self._fg = fg
        self._text_size = text_size
        self._text_area = FONT(self._text_size).render(self._text, 0, fg)
        self._surf = pygame.Surface(self._size)
        self._surf.fill(bg)
        self._surf.blit(self._text_area, text_offset)
        self._surf.convert_alpha()
        self._surf.set_alpha(transparency)
        self._text_offset = text_offset
        self._transparency = transparency

    def configure(
        self,
        *,
        text_value: str | None = None,
        foreground: str | None = None,
        background: str | None = None,
        text_size: int | None = None,
        text_offset: tuple | None = None,
        transparency: int | None = None,
    ):
        if text_value is not None:
            self._text = text_value
        if foreground is not None:
            self._fg = foreground
        if background is not None:
            self._bg = background
        if text_size is not None:
            self._text_size = text_size
        if text_offset is not None:
            self._bg = text_offset
        if transparency is not None:
            self._transparency = transparency

        self._text_area = FONT(self._text_size).render(self._text, 0, self._fg)
        self._surf.fill(self._bg)
        self._surf.blit(self._text_area, self._text_offset)
        self._surf.set_alpha(self._transparency)

    def __repr__(self):
        return f"""Label object at {self._position}"""

    def __str__(self):
        return repr(self)

    def __feed__(self, events):
        pass

    def __draw__(self, surf):
        self._text_area = FONT(self._text_size).render(self._text, 0, self._fg)
        self._surf.fill(self._bg)
        self._surf.blit(self._text_area, self._text_offset)
        self._surf.convert_alpha()
        self._surf.set_alpha(self._transparency)
        surf.blit(self._surf, self._position)


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
        self._position = position
        self._text = text
        self._fg = fg
        self._onclick = onclick
        self._text_size = text_size
        self._image = pygame.image.load(path)
        self._size = self._image.get_size()
        self._transparency = transparency
        self._rect = pygame.Rect(*self._position, *self._size)
        self._text_area = FONT(self._text_size).render(self._text, 0, fg)
        self._state = state
        self._mask = pygame.Surface(self._size)
        self._mask.fill("#202020")
        self._mask.set_alpha(150)
        self._text_offset = text_offset
        self._image.set_alpha(self._transparency)
        self._text_area.set_alpha(self._transparency)
        self._collide = pygame.mask.from_surface(self._image)

    def __repr__(self):
        return f"""ButtonImage object at {self._position}"""

    def __str__(self):
        return repr(self)

    def __draw__(self, surf):
        surf.blit(self._image, self._position)
        surf.blit(
            self._text_area,
            tuple(p + o for p, o in zip(self._position, self._text_offset)),
        )

        if self._state == "disabled":
            surf.blit(self._mask, self._position)

    def __feed__(self, events):
        clicked = False
        if self._rect.collidepoint(*pygame.mouse.get_pos()):
            local_x, local_y = pygame.mouse.get_pos()
            local_x -= self._position[0]
            local_y -= self._position[1]
            for event in events:
                if (
                    event.type == pygame.MOUSEBUTTONUP
                    and self._state == "enabled"
                    and self._collide.get_at((local_x, local_y))
                ):
                    clicked = True
            if self._collide.get_at((local_x, local_y)):
                pygame.mouse.set_cursor(11)
            else:
                pygame.mouse.set_cursor(0)
        if clicked:
            self._onclick.__call__()


class Line(Widget):
    def __init__(
        self,
        *,
        start: tuple,
        end: tuple,
        color: str,
        width: int = 1,
    ):
        self._start = start
        self._end = end
        self._color = color
        self._width = width
        self._topleft = (min(start[0], end[0]), min(start[1], end[1]))
        self._bottomright = (max(start[0], end[0]), max(start[1], end[1]))

    def __repr__(self):
        return f"""Line object at {self._topleft}"""

    def __str__(self):
        return repr(self)

    def __feed__(self, events):
        pass

    def __draw__(self, surf):
        pygame.__draw__.line(surf, self._color, self._start, self._end, self._width)


class Polygon(Widget):
    def __init__(
        self, *, points: list[tuple], color: str, width: int = 1, fill: bool = False
    ):
        if fill:
            width = 0
        self._points: list = points
        self._color: str = color
        self._width: int = width

    def __feed__(self, events):
        pass

    def __draw__(self, surf):
        pygame.__draw__.polygon(surf, self._color, self._points, self._width)


class Window:
    def __init__(
        self: "Window",
        surf: pygame.Surface,
        bg: str,
        fps: int = 60,
    ):
        self._bg = bg
        self._FPS = fps
        self._surf = surf
        self._elements = dict()
        self._runing = False
        self._size = self._surf.get_size()
        self.tick = set()
        self._begin = time.time()
        self._after = list()

    @property
    def duration(self):
        return time.time() - self._begin

    @duration.setter
    def duration(self, value):
        raise NotAllowedError()

    def __getitem__(self, key):
        return self._elements[key]

    def __setitem__(self, key, value):
        if issubclass(type(value), Widget):
            self._elements[key] = value
        else:
            raise TypeError("Not a Widget")

    def __delitem__(self, key):
        del self._elements[key]

    def draw_elements(self):
        for element in self._elements.values():
            element.__draw__(self._surf)

    def update_elements(self, events):
        for element in self._elements.values():
            element.__feed__(events)

    def run(self):
        self._runing = True
        self._clock = pygame.time.Clock()
        while self._runing:
            self._surf.fill(self._bg)
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
            self._clock.tick(self._FPS)

    def stop(self):
        self._runing = False


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
    position=(300, 300),
    size=(300, 100),
    bg="#673829",
    fg="#000000",
    text_size=50,
)
main.tick.add(second)
main.run()
