import moviepy.video
import moviepy.video.VideoClip
import pygame
import sys
import os
import moviepy
import time


# import pin

# Initialisation
if not pygame.get_init():
    pygame.init()

# Constantes

SURFACE = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SOUNDS_FOLDER = os.path.join(os.getcwd(), "sounds")
IMAGES_FOLDER = os.path.join(os.getcwd(), "images")
ALLOWED_STATES = [
    "enabled",
    "disabled",
]


def FONT(size):
    font = pygame.font.SysFont("Aptos", size)
    return font


# Classes d'elements
class NotAllowedError(Exception):
    pass


class Widget:
    def draw(self, surf):
        raise NotImplementedError

    def feed(self, events):
        raise NotImplementedError


class Image(Widget):
    def __init__(self, *, position, path, transparency=255, resize=None):
        self.image = pygame.image.load(path)
        self.position = position
        self.path = path
        self.resize = resize
        self.image.convert_alpha()
        if self.resize is not None:
            pygame.transform.scale(self.image, self.resize)
        self.surf = pygame.Surface(self.image.get_size())
        self.surf.blit(self.image, (0, 0))
        self.surf.convert_alpha()
        self.surf.set_alpha(transparency)

    def __repr__(self):
        return f"""Image object at {self.position}"""

    def __str__(self):
        return repr(self)

    def feed(self, events):
        pass

    def draw(self, surf):
        surf.blit(self.surf, self.position)


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
            self.state = state
        else:
            raise ValueError("Unrecognized state value, see ALLOWED_STATES")
        self.text_size = text_size
        self.position = position
        self.size = size
        self.text = text
        self.bg = bg
        self.fg = fg
        self.transparency = transparency
        self.onclick = onclick
        self.rect = pygame.Rect(*self.position, *self.size)
        self.text_area = FONT(self.text_size).render(self.text, 0, fg)
        self.surf = pygame.Surface(self.size)
        self.surf.fill(bg)
        self.surf.blit(self.text_area, text_offset)
        self.mask = pygame.Surface(self.size)
        self.mask.fill("#202020")
        self.mask.set_alpha(150)
        self.surf.set_alpha(self.transparency)

    def configure(
            self,
            text_value = None,
            foreground = None,
            background = None,
            text_size = None,
            text_offset = None,
            transparency = None,
        ):
        if text_value is not None:
            self.text = text_value
        if foreground is not None:
            self.fg = foreground
        if background is not None:
            self.bg = background
        if text_size is not None:
            self.text_size = text_size
        if text_offset is not None:
            self.bg = text_offset
        if transparency is not None:
            self.transparency = transparency
            
        self.text_area = FONT(self.text_size).render(self.text, 0, self.fg)
        self.surf.fill(self.bg)
        self.surf.blit(self.text_area, self.text_offset)
        self.surf.set_alpha(self.transparency)

        

    def __repr__(self):
        return f"""Button object at {self.position}"""

    def __str__(self):
        return repr(self)

    def feed(self, events):
        clicked = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and self.state == "enabled":
                if self.rect.collidepoint(*pygame.mouse.get_pos()):
                    clicked = True
        if self.rect.collidepoint(*pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(11)
        else:
            pygame.mouse.set_cursor(0)
        if clicked:
            self.onclick.__call__()

    def draw(self, surf):
        surf.blit(self.surf, self.position)
        if self.state == "disabled":
            surf.blit(self.mask, self.position)


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
        self.size = size
        self.position = position
        self.text = text
        self.bg = bg
        self.fg = fg
        self.text_size = text_size
        self.text_area = FONT(self.text_size).render(self.text, 0, fg)
        self.surf = pygame.Surface(self.size)
        self.surf.fill(bg)
        self.surf.blit(self.text_area, text_offset)
        self.surf.convert_alpha()
        self.surf.set_alpha(transparency)
        self.text_offset = text_offset
        self.transparency = transparency

    def configure(
            self,
            text_value = None,
            foreground = None,
            background = None,
            text_size = None,
            text_offset = None,
            transparency = None,
        ):
        if text_value is not None:
            self.text = text_value
        if foreground is not None:
            self.fg = foreground
        if background is not None:
            self.bg = background
        if text_size is not None:
            self.text_size = text_size
        if text_offset is not None:
            self.bg = text_offset
        if transparency is not None:
            self.transparency = transparency
            
        self.text_area = FONT(self.text_size).render(self.text, 0, self.fg)
        self.surf.fill(self.bg)
        self.surf.blit(self.text_area, self.text_offset)
        self.surf.set_alpha(self.transparency)

    def __repr__(self):
        return f"""Label object at {self.position}"""

    def __str__(self):
        return repr(self)

    def feed(self, events):
        pass

    def draw(self, surf):
        self.text_area = FONT(self.text_size).render(self.text, 0, self.fg)
        self.surf.fill(self.bg)
        self.surf.blit(self.text_area, self.text_offset)
        self.surf.convert_alpha()
        self.surf.set_alpha(self.transparency)
        surf.blit(self.surf, self.position)

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
        self.position = position
        self.text = text
        self.fg = fg
        self.onclick = onclick
        self.text_size = text_size
        self.image = pygame.image.load(path)
        self.size = self.image.get_size()
        self.transparency = transparency
        self.rect = pygame.Rect(*self.position, *self.size)
        self.text_area = FONT(self.text_size).render(self.text, 0, fg)
        self.state = state
        self.mask = pygame.Surface(self.size)
        self.mask.fill("#202020")
        self.mask.set_alpha(150)
        self.text_offset = text_offset
        self.image.set_alpha(self.transparency)
        self.text_area.set_alpha(self.transparency)
        self.collide = pygame.mask.from_surface(self.image)

    def __repr__(self):
        return f"""ButtonImage object at {self.position}"""

    def __str__(self):
        return repr(self)

    def draw(self, surf):
        surf.blit(self.image, self.position)
        surf.blit(
            self.text_area,
            tuple(p + o for p, o in zip(self.position, self.text_offset)),
        )

        if self.state == "disabled":
            surf.blit(self.mask, self.position)

    def feed(self, events):
        clicked = False
        if self.rect.collidepoint(*pygame.mouse.get_pos()):
            local_x, local_y = pygame.mouse.get_pos()
            local_x -= self.position[0]
            local_y += self.position[1]
            for event in events:
                if (
                    event.type == pygame.MOUSEBUTTONUP
                    and self.state == "enabled"
                    and self.collide.get_at((local_x, local_y))
                ):
                    clicked = True
            if self.collide.get_at((local_x, local_y)):
                pygame.mouse.set_cursor(11)
            else:
                pygame.mouse.set_cursor(0)
        if clicked:
            self.onclick.__call__()


class Line(Widget):
    def __init__(
        self,
        *,
        start: tuple,
        end: tuple,
        color: str,
        width: int = 1,
    ):
        self.start = start
        self.end = end
        self.color = color
        self.width = width
        self.topleft = (min(start[0], end[0]), min(start[1], end[1]))
        self.bottomright = (max(start[0], end[0]), max(start[1], end[1]))

    def __repr__(self):
        return f"""Line object at {self.topleft}"""

    def __str__(self):
        return repr(self)

    def feed(self, events):
        pass

    def draw(self, surf):
        pygame.draw.line(surf, self.color, self.start, self.end, self.width)


class Polygon(Widget):
    def __init__(
        self, *, points: list[tuple], color: str, width: int = 1, fill: bool = False
    ):
        if fill:
            width = 0
        self.points: list = points
        self.color: str = color
        self.width: int = width

    def feed(self, events):
        pass

    def draw(self, surf):
        pygame.draw.polygon(surf, self.color, self.points, self.width)


class Video(Widget):
    def __init__(
        self,
        *,
        position: tuple,
        path: str,
    ):
        raise NotImplementedError("PAS FINI")
        self.position = position
        self.patgh = path
        self.video = moviepy.video.VideoClip.Clip()


class Window:
    def __init__(
        self: "Window",
        surf: pygame.Surface,
        bg: str,
        fps: int = 60,
    ):
        self.bg = bg
        self.FPS = fps
        self.surf = surf
        self.elements = dict()
        self.runing = False
        self.size = self.surf.get_size()
        self.tick = set()
        self.begin = time.time()

    @property
    def duration(self):
        return time.time() - self.begin

    @duration.setter
    def duration(self, value):
        raise NotAllowedError()


    def __getitem__(self, key):
        return self.elements[key]

    def __setitem__(self, key, value):
        if issubclass(type(value), Widget):
            self.elements[key] = value
        else:
            raise TypeError("Not a Widget")

    def __delitem__(self, key):
        del self.elements[key]

    def draw_elements(self):
        for element in self.elements.values():
            element.draw(self.surf)

    def update_elements(self, events):
        for element in self.elements.values():
            element.feed(events)

    def run(self):
        self.runing = True
        self.clock = pygame.time.Clock()
        while self.runing:
            self.surf.fill(self.bg)
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
            self.clock.tick(self.FPS)

    def stop(self):
        self.runing = False


# Fonctions d'appel de boutons


def second():
    main["label_hour"].text = str(main.duration)


main = Window(SURFACE, "#000000")
settings = Window(SURFACE, "#000000")

main["car image"] = ButtonImage(
    position=(0, 0),
    path=IMAGES_FOLDER + "/bg_main.png",
    text=" ",
    fg="#000000",
    text_size=10,
    onclick=lambda _=None: print("fenetre à ouvrir"),
)
main["stop_button"] = ButtonImage(
    position=(0, 0),
    text=" ",
    fg="#FF0000",
    onclick=main.stop,
    text_size=10,
    path=IMAGES_FOLDER + "/close.png",
)
main["window_button"] = Button(
    size=(300, 100),
    position=(200, 0),
    text="new_win",
    bg="#039283",
    fg="#111111",
    onclick=settings.run,
    text_size=30,
)
settings["stop_button"] = ButtonImage(
    position=(0, 0),
    text=" ",
    fg="#FF0000",
    onclick=settings.stop,
    text_size=10,
    path=IMAGES_FOLDER + "/close.png",
)
main["label_hour"] = Label(
    position=(400,0),
    size=(200,100),
    text='',
    bg="#00FF00",
    fg="#0000FF",
    text_size=50,
)
main.tick.add(second)
main.run()

