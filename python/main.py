import sys
from pygame.constants import *
from OpenGL.GLU import *
from OBJ import *
from Camera import *

rotate = False
move = False


def init_camera():
    # Define initial camera parameters
    initial_camera_params = {
        'position': [0, 10, 150],  # Adjust the Y-coordinate to move the camera higher and Z-coordinate to move it closer
        'direction': [0, 0, -1],
        'up_vector': [0, 1, 0],
        'field_of_view': 90.0,
        'transition_frames': 60
    }

    # Create initial camera
    return Camera(**initial_camera_params)


def render_object(obj, camera):
    glLoadIdentity()

    # Apply the view matrix from the current camera
    glMultMatrixf(camera.view_matrix)

    obj.render()


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


def setup_projection(camera, width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(camera.field_of_view, width / float(height), 1, 100.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)


def handle_input(camera):
    global rotate, move
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            handle_mouse_down(event, camera)
        elif event.type == MOUSEBUTTONUP:
            handle_mouse_up(event)
        elif event.type == MOUSEMOTION:
            handle_mouse_motion(event, camera)


def handle_mouse_down(event, camera):
    global rotate, move
    if event.button == 1:
        rotate = True
    elif event.button == 3:
        move = True


def handle_mouse_up(event):
    global rotate, move
    if event.button == 1:
        rotate = False
    elif event.button == 3:
        move = False


def handle_mouse_motion(event, camera):
    global rotate, move
    i, j = event.rel
    scaling_factor = 0.2  # Adjust the scaling factor as needed

    if rotate:
        camera.position[0] += i * scaling_factor
        camera.position[1] -= j * scaling_factor
    if move:
        camera.position[0] += i * scaling_factor
        camera.position[1] -= j * scaling_factor


# def render_object(obj, tx, ty, zpos, rx, ry):
#     glLoadIdentity()
#     glTranslate(tx[0] / 20., ty[0] / 20., -zpos[0])
#     glRotate(ry[0], 1, 0, 0)
#     glRotate(rx[0], 0, 1, 0)
#     obj.render()


def main():
    init()
    obj = OBJ("models/Football.obj", swapyz=True)
    obj.generate()

    clock = pygame.time.Clock()
    width, height = 1000, 1000
    setup_projection(init_camera(), width, height)

    current_camera = init_camera()
    target_camera = Camera([5, 5, 5], [0, 0, 0], [0, 1, 0], 60.0, 60)

    frame_count = 0

    while True:
        clock.tick(30)
        handle_input(current_camera)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        render_object(obj, current_camera)

        pygame.display.flip()

        frame_count += 1

        if frame_count <= current_camera.transition_frames:
            # Interpolate between current and target camera
            current_camera.interpolate(target_camera, frame_count, current_camera.transition_frames)
        else:
            frame_count = 0
            # Switch to the next camera or reset to the initial camera
            current_camera = target_camera
            target_camera = init_camera() if current_camera == target_camera else Camera([5, 5, 5], [0, 0, 0],
                                                                                         [0, 1, 0], 60.0, 60)


if __name__ == "__main__":
    main()
