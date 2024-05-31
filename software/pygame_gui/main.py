# Comments indications: (by using `better comments` VsCode Extension)
# * Important
# TODO
# ! alert
# ? queries
# // deleted code


# Imports
import pygame_vkeyboard as vkboard
import pygame
import sys
import os
import time

SURFACE = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# Constants


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
    All widgets needs to have a __draw__(self,surf_dest),
    a configure(self, *, **kwargs)
    and a __feed__(self,events) method defined
    """
    def __init__(self):
        self._position = (0,0)
    def __repr__(self):
        return f"{self.__class__} object at {self._position}"
    def __str__(self) -> str:
        return repr(self)
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

    def configure(self, *args, **kwargs):
        """
        Clean way to edit the Widget's attributes
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
        self._transparency = transparency
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

    def configure(
        self,
        position: tuple | None = None,
        path: str | None = None,
        transparency: int | None = None,
        resize: tuple | None = None,
    ):
        if position is None:
            position = self._position
        if path is None:
            path = self._path
        if transparency is None:
            transparency = self._transparency
        if resize is None:
            resize = self._resize
        self.__init__(
            position=position,
            path=path,
            transparency=transparency,
            resize=resize,
        )


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

    def configure(
        self,
        position: tuple | None = None,
        size: tuple | None = None,
        bg: str | None = None,
        fg: str | None = None,
        text_size: int | None = None,
        text_offset: tuple | None = None,
        transparency: int | None = None,
    ):
        if position is None:
            position = self._position
        if size is None:
            size = self._size
        if bg is None:
            bg = self._bg
        if fg is None:
            fg = self._fg
        if text_size is None:
            text_size = self._text_size
        if text_offset is None:
            text_offset = self._text_offset
        if transparency is None:
            transparency = self._transparency
        self.__init__(
            position=position,
            size=size,
            bg=bg,
            fg=fg,
            text_size=text_size,
            text_offset=text_offset,
            transparency=transparency,
        )


class Button(Widget):
    # TODO: add a method to determinate if the button is at the top layer
    """
    This class is used to display buttons, whose can run a function on a click

    :size: tuple
    The size of the widget

    :position: tuple
    The position of the widget

    :text: str
    The text displayed on the widget

    :bg: str
    The background of the widget

    :fg: str
    The foreground of the widget

    :onclick
    The function triggered by a click

    :text_size: int
    The text's size

    :text_offset: tuple
    The text's position on the widget

    :transparency: int
    The transparency of the widget

    :state: str
    The state of the button, `enabled` or `disabled`

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
        state=None,
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
        if state is not None:
            self._state = state

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
    """
    A Label is used to display text

    :size: tuple
    The size of the widget

    :position: tuple
    The position of the widget

    :text: str
    The text displayed on the widget

    :bg: str
    The background of the widget

    :fg: str
    The foreground of the widget

    :text_size: int
    The text's size

    :text_offset: tuple
    The text's position on the widget

    :transparency: int
    The transparency of the widget


    """

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
    """
    This Widget is used to create clickable images

        :size: tuple
    The size of the widget

    :position: tuple
    The position of the widget

    :text: str
    The text displayed on the widget

    :path: str
    The path of the image that will be display

    :bg: str
    The background of the widget

    :fg: str
    The foreground of the widget

    :onclick
    The function triggered by a click

    :text_size: int
    The text's size

    :text_offset: tuple
    The text's position on the widget

    :transparency: int
    The transparency of the widget

    :state: str
    The state of the button, `enabled` or `disabled`

    """

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
        self._path = path
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
        else:
            pygame.mouse.set_cursor(0)
        if clicked:
            self._onclick.__call__()

    def configure(
        self,
        position: tuple | None = None,
        fg: str | None = None,
        text_size: int | None = None,
        text_offset: tuple | None = None,
        transparency: int | None = None,
        state: str | None = None,
    ):
        if position is None:
            position = self._position
        if fg is None:
            fg = self._fg
        if text_size is None:
            text_size = self._text_size
        if text_offset is None:
            text_offset = self._text_offset
        if transparency is None:
            transparency = self._transparency
        if state is None:
            state = self._state
        self.__init__(
            position=position,
            onclick = self._onclick,
            text=self._text,
            path = self._path,
            fg=fg,
            text_size=text_size,
            text_offset=text_offset,
            transparency=transparency,
            state=state,
        )


class Line(Widget):
    """
    A class used to draw a line on the screen

    :start: tuple
    The starting point

    :end: tuple
    The end point

    :color: str
    The color of the line

    :width: int
    The width of the line

    """

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

    def configure(
        self,
        start: tuple | None = None,
        end: tuple | None = None,
        color: str | None = None,
        width: int | None = None,
    ):
        if start is None:
            start = self._start
        if end is None:
            end = self._end
        if color is None:
            color = self._color
        if width is None:
            width = self._width
        self.__init__(
            start=start,
            end=end,
            color=color,
            width=width,
        )


class Polygon(Widget):
    """
    This class is used to display polygon

    :points: list[tuple]
    A list of the polygon's points

    :color: str
    The color of the polygon

    :width: int
    The width of the Polygon's stroke

    :fill: bool
    Set it to True or set the width to 0 to fill the polygon with the specified color

    """

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

    def configure(
        self,
        points: list | None = None,
        color: str | None = None,
        width: int | None = None,
        fill: bool | None = None,
    ):
        if points is None:
            points = self._points
        if fill is None:
            fill = self._fill
        if color is None:
            color = self._color
        if width is None:
            width = self._width
        self.__init__(
            points=points,
            fill=fill,
            color=color,
            width=width,
        )


class Window:
    """
    :surf: pygame.Surface
    The surface where the Window will be created

    :bg: str
    The background color of the Window

    :fps: int
    The max fps of the Window, leav it to 60 if you don't want any problem

    """

    def __init__(
        self: "Window",
        bg: str,
        fps: int = 60,
    ):
        #//pygame.mouse.set_visible(False)
        self._bg = bg
        self._FPS = fps
        self._surf = SURFACE
        self._elements = dict()
        self._runing = False
        self._size = self._surf.get_size()
        self.tick = set()
        self._begin = time.time()
        self._after = list()
        self._sounds = dict()
        self._musics = dict()
    def after(self, function, delay):
        last = self.duration
        self._after.append([function,delay,last])
    def add_sound(self, name, path):
        self._sounds[name] = pygame.mixer.Sound(path)
    def play_sound(self, name):
        pygame.mixer.Sound.play(self._sounds[name])
    def add_music(self, name, path):
        self._musics[name] = pygame.mixer.music.load(path)
    def play_music(self, name):
        pygame.mixer.music.play(self._musics[name])
    def pause_music(self, name):
        pygame.mixer.music.pause(self._musics[name])
    def unpause_music(self, name):
        pygame.mixer.music.unpause(self._musics[name])
    def stop_music(self, name):
        pygame.mixer.music.stop(self._musics[name])
    def stop_sound(self, name):
        pygame.mixer.stop(self._sounds[name])
    def silence(self):
        pygame.mixer.stop()

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
            now = self.duration
            for element in self._after:
                if now - element[2] >= element[1]:
                    element[2] = now
                    element[0].__call__()
                    

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.runing = False
                    sys.exit()
            pygame.display.flip()
            self._clock.tick(self._FPS)

    def stop(self):
        self._runing = False

