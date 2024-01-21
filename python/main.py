from pygame.constants import *
from OpenGL.GLU import *
from OBJ import *
import json
import sys

rotate = False
move = False


def init():
    pygame.init()
    viewport = (800, 600)
    hx, hy = viewport[0] / 2, viewport[1] / 2
    srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))

    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)


def load_objects_from_json(json_filename):
    with open(json_filename, 'r') as file:
        objects_data = json.load(file)

    objects = []
    for obj_data in objects_data:
        obj = OBJ(obj_data["filename"], obj_data.get("swapyz", False), obj_data.get("position"),
                  obj_data.get("rotation"))
        objects.append(obj)

    return objects


def setup_projection(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90.0, width / float(height), 1, 100.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)


def handle_input(rx, ry, tx, ty, zpos):
    global rotate, move
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            handle_mouse_down(event, zpos)
        elif event.type == MOUSEBUTTONUP:
            handle_mouse_up(event)
        elif event.type == MOUSEMOTION:
            handle_mouse_motion(event, rx, ry, tx, ty)


def handle_mouse_down(event, zpos):
    global rotate, move
    if event.button == 4:
        zpos[0] = max(1, zpos[0] - 1)
    elif event.button == 5:
        zpos[0] += 1
    elif event.button == 1:
        rotate = True
    elif event.button == 3:
        move = True


def handle_mouse_up(event):
    global rotate, move
    if event.button == 1:
        rotate = False
    elif event.button == 3:
        move = False


def handle_mouse_motion(event, rx, ry, tx, ty):
    global rotate, move
    i, j = event.rel
    if rotate:
        rx[0] += i
        ry[0] += j
    if move:
        tx[0] += i
        ty[0] -= j


def render_object(obj, tx, ty, zpos, rx, ry):
    glLoadIdentity()
    glTranslate(tx[0] / 20., ty[0] / 20., -zpos[0])
    glRotate(ry[0], 1, 0, 0)
    glRotate(rx[0], 0, 1, 0)
    obj.render()


def main():
    init()
    if sys.argv[1] == "obj":
        obj = OBJ("models/Football.obj", swapyz=True)
        obj.generate()

        clock = pygame.time.Clock()
        width, height = 800, 600
        setup_projection(width, height)

        rx, ry, tx, ty = [0], [0], [0], [0]
        zpos = [5]

        while True:
            clock.tick(30)
            handle_input(rx, ry, tx, ty, zpos)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            render_object(obj, tx, ty, zpos, rx, ry)

            pygame.display.flip()
    elif sys.argv[1] == "json":
        objects = load_objects_from_json("objects.json")

        clock = pygame.time.Clock()
        width, height = 800, 600
        setup_projection(width, height)

        rx, ry, tx, ty = [0], [0], [0], [0]
        zpos = [5]

        while True:
            clock.tick(30)
            handle_input(rx, ry, tx, ty, zpos)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Render all objects on the scene
            for obj in objects:
                render_object(obj, tx, ty, zpos, rx, ry)

            pygame.display.flip()


if __name__ == "__main__":
    main()
