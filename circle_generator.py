import pygame, pygame.freetype
import math
import time
import numpy

pygame.init()
canvas = pygame.display.set_mode((400, 400), pygame.RESIZABLE)
pygame.display.set_caption('Big Chungus')

def sin(angle):
    return math.sin(math.radians(angle))

def cos(angle):
    return math.cos(math.radians(angle))

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pygame_format = (x, y)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def __repr__(self):
        return 'x : {}, y : {}'.format(self.x, self.y)

class Line:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def __repr__(self):
        return 'point1 : {}\npoint2 : {}'.format(self.point1, self.point2)

#dis function will be unreadable
def convert_to_canvas(data):
    if isinstance(data, Point):
        xThing = canvas.get_width() / (screen2.x - screen1.x)
        yThing = canvas.get_height() / (screen2.y - screen1.y)
        return Point((data.x - screen1.x) * xThing, (data.y - screen1.y) * yThing)
    elif isinstance(data, pygame.rect.Rect):
        point1 = convert_to_canvas(Point(data.topleft[0], data.topleft[1]))
        point2 = convert_to_canvas(Point(data.bottomright[0], data.bottomright[1]))
        Thing = canvas.get_height() / (screen2.y - screen1.y)
        return pygame.rect.Rect(point1.pygame_format, (square_size * Thing + 1, square_size * Thing + 1)) # pygame doesent fully draw a rect

def convert_from_canvas(data):
    if isinstance(data, Point):
        xProportion = (screen2.x - screen1.x) / old_display_width
        yProportion = (screen2.y - screen1.y) / old_display_height
        # print('xp : {}, yp : {}'.format(xProportion, yProportion))
        # print((screen2.x - screen1.x), old_display_width)
        return Point(data.x * xProportion + screen1.x, data.y * yProportion + screen1.y)
    elif isinstance(data, tuple):
        a = convert_to_canvas(Point(data[0], data[1]))
        return (a.x, a.y)

def scale_mouse_movement(data):
    xProportion = (screen2.x - screen1.x) / canvas.get_width()
    yProportion = (screen2.y - screen1.y) / canvas.get_height()
    return (data[0] * xProportion, data[1] * yProportion)

def zoom_screen(zoom):
    a = screen1.x - screen2.x
    b = screen1.y - screen2.y
    sqrt = math.sqrt(a * a + b * b)
    x_zoom = abs(screen1.x - screen2.x) / sqrt * zoom
    y_zoom = abs(screen1.y - screen2.y) / sqrt * zoom

    screen1.x += x_zoom
    screen2.x -= x_zoom

    screen1.y += y_zoom
    screen2.y -= y_zoom

def get_pygame_square_from_coords(coords):
    l = square_size
    return pygame.rect.Rect(((coords.x - 1) * l, (coords.y - 1) * l), (l, l))

def get_square_coords(coords):
    return Point(coords.x // square_size + 1, coords.y // square_size + 1)

def get_distance(square1, square2):
    x = square1.x - square2.x
    y = square1.y - square2.y
    return math.sqrt(x * x +y * y)

def get_square_center(coords):
    c = get_pygame_square_from_coords(coords)
    c = c.topleft
    return Point(c[0] + square_size /  2, c[1] + square_size / 2)

def draw(data, color):
    if isinstance(data, Line):
        pygame.draw.line(canvas, color, data.point1.pygame_format, data.point2.pygame_format, 1)
    elif isinstance(data, pygame.rect.Rect):
        pygame.draw.rect(canvas, color, data)

#points are not in square coords
def get_circle(center, side):
    radius = get_distance(center, side)
    circle = []
    for angle in numpy.arange(0, 360, .5):
        point = Point(cos(angle) * radius + center.x, sin(angle) * radius + center.y)
        circle.append(get_square_coords(point))
    return circle

# def get_circle(radius, offset = Point(0, 0)):
#     radius *= square_size # convert to pixels
#     circle = []
#     for angle in numpy.arange(0, 360, .2):
#         point = Point(cos(angle) * radius + offset.x, sin(angle) * radius + offset.y)
#         circle.append(get_square_coords(point))
#     return circle

# will start woth center of screen showing (0, 0)(coordnates), screen1 = top left, screen 2 = bottom left, etc
# for zooming in, will just change screen1, screen2, etc
# alse, screen are gonna be global variables(i dont wanna pass it as an argument for every single function)
screen1 = Point(-200, -200)
screen2 = Point(200, 200)

square_size = 40
display_x_shift = 0
display_y_shift = 0
display_zoom = 0

old_display_width = canvas.get_width()
old_display_height = canvas.get_height()

mouse_pressed = False
must_draw = True
mouse_moved = False
selecting_circle = False
circle_center_is_0 = True
pos = Point(0, 0) # used for showing radius onscreen

circle = get_circle(Point(0, 0), Point(5 * square_size, 5 * square_size))
while True:
    for event in [pygame.event.wait()] + pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                selecting_circle = not selecting_circle
                must_draw = True
            elif event.button == 2 and selecting_circle:
                circle_center_is_0 = not circle_center_is_0
        elif event.type == pygame.MOUSEMOTION and selecting_circle:
            mouse_moved = True
        elif event.type == pygame.MOUSEWHEEL:
            display_zoom = event.y * 40
        elif event.type == pygame.WINDOWRESIZED or event.type == pygame.WINDOWSIZECHANGED:
            screen2 = convert_from_canvas(Point(event.x, event.y))
            old_display_height = canvas.get_height() # set these after using them in convert_from_canvas
            old_display_width = canvas.get_width()
            must_draw = True

    # check dragging
    pressed = pygame.mouse.get_pressed(3)
    if pressed[0]:
        if not mouse_pressed:
            pygame.mouse.get_rel() # set rel to current position
        mouse_pressed = True
        mouse_movement = scale_mouse_movement(pygame.mouse.get_rel())
        display_x_shift = -mouse_movement[0]
        display_y_shift = -mouse_movement[1]
    else:
        mouse_pressed = False

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_RIGHT]:
        display_x_shift = 1
    elif pressed[pygame.K_LEFT]:
        display_x_shift = -1
    if pressed[pygame.K_UP]:
        display_y_shift = -1
    elif pressed[pygame.K_DOWN]:
        display_y_shift = 1

    if must_draw or display_x_shift != 0 or display_y_shift != 0 or display_zoom != 0 or mouse_moved or selecting_circle:
        # move screen
        screen1.x += display_x_shift
        screen2.x += display_x_shift

        screen1.y += display_y_shift
        screen2.y += display_y_shift
        
        # zoom screen
        zoom_screen(display_zoom)

        canvas.fill('white') # IMPORTANT (you just get a big mess, dont try it)
        
        # tis is not needed
        # tis has now been removed

        if selecting_circle: 
            pos = pygame.mouse.get_pos()
            pos = convert_from_canvas(Point(pos[0], pos[1]))
            print('square : {}'.format(get_square_coords(pos)))
            pos = get_square_center(get_square_coords(pos))
            if circle_center_is_0:
                circle = get_circle(Point(0, 0), pos)
            else:
                circle = get_circle(Point(square_size / 2, square_size / 2), pos)
            #circle = get_circle(math.sqrt(pos.x * pos.x + pos.y * pos.y) / square_size, offset)
            # draw(convert_to_canvas(get_pygame_square_from_coords(get_square_coords(convert_from_canvas(pos)))), 'black')

        if selecting_circle:
            for squarex in numpy.arange(screen1.x // square_size - 1, screen2.x // square_size + 1):
                draw(convert_to_canvas(get_pygame_square_from_coords(Point(squarex, 1))), 'yellow')
            for squarey in numpy.arange(screen1.y // square_size - 1, screen2.y // square_size + 1):
                draw(convert_to_canvas(get_pygame_square_from_coords(Point(1, squarey))), 'yellow')
            if circle_center_is_0:
                for squarex in numpy.arange(screen1.x // square_size - 1, screen2.x // square_size + 1):
                    draw(convert_to_canvas(get_pygame_square_from_coords(Point(squarex, 0))), 'yellow')
                for squarey in numpy.arange(screen1.y // square_size - 1, screen2.y // square_size + 1):
                    draw(convert_to_canvas(get_pygame_square_from_coords(Point(0, squarey))), 'yellow')

        # make orange center
        if circle_center_is_0:
            draw(convert_to_canvas(get_pygame_square_from_coords(Point(0, 0))), 'orange')
            draw(convert_to_canvas(get_pygame_square_from_coords(Point(0, 1))), 'orange')
            draw(convert_to_canvas(get_pygame_square_from_coords(Point(1, 0))), 'orange')
        draw(convert_to_canvas(get_pygame_square_from_coords(Point(1, 1))), 'orange')

        for square in circle:
            draw(convert_to_canvas(get_pygame_square_from_coords(square)), 'green')

        # also, i add an extra square_size to the end(otherwize it wont draw the rightmost line)
        for linex in numpy.arange(screen1.x // square_size * square_size, screen2.x // square_size * square_size + square_size, square_size):
            draw(Line(convert_to_canvas(Point(linex, screen1.y)), convert_to_canvas(Point(linex, screen2.y))), 'blue')
        for liney in numpy.arange(screen1.y // square_size * square_size, screen2.y // square_size * square_size + square_size, square_size):
            draw(Line(convert_to_canvas(Point(screen1.x, liney)), convert_to_canvas(Point(screen2.x, liney))), 'blue')

        # circle radius
        if selecting_circle:
            pos = pygame.mouse.get_pos()
            pos = get_square_coords(convert_from_canvas(Point(pos[0], pos[1])))
        text = pygame.freetype.SysFont("hahaha", 30)
        if circle_center_is_0:
            text.render_to(canvas, (0, 0), str(round(get_distance(Point(0, 0), get_square_center(pos)) / square_size, 2)), 'black')
        else:
            text.render_to(canvas, (0, 0), str(round(get_distance(Point(1, 1), pos), 2)), 'black')

        #draw(convert_to_canvas(get_pygame_square_from_coords(Point(1, 1))), 'yellow')

        display_x_shift = 0
        display_y_shift = 0
        display_zoom = 0
        must_draw = False
        mouse_moved = False

        pygame.display.flip()
        draw(convert_to_canvas(get_pygame_square_from_coords(Point(1, 1))), 'blue')
        draw(convert_to_canvas(get_pygame_square_from_coords(Point(-3, 2))), 'blue')