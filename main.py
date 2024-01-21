from pygame.constants import *
from OpenGL.GLU import *
from OBJ import *
import json
import sys
from Camera import *

rotate = False
move = False


def init_camera():
    # Define initial camera parameters
    initial_camera_params = {
        'id': 1,
        'position': [0, 2, 10],  # Adjust the Y-coordinate to move the camera lower and Z-coordinate to move it closer
        'direction': [0, 0, -1],
        'up_vector': [0, 1, 0],
        'field_of_view': 90.0,
        'transition_frames': 60
    }

    # Create initial camera
    return Camera(**initial_camera_params)


def load_cameras_from_json(json_filename):
    with open(json_filename, 'r') as file:
        cameras_data = json.load(file)

    cameras = []
    for camera_data in cameras_data:
        camera = Camera(id=camera_data["id"],
                        position=camera_data["position"],
                        direction=camera_data["direction"],
                        up_vector=camera_data["up_vector"],
                        field_of_view=camera_data["field_of_view"],
                        transition_frames=camera_data["transition_frames"])
        cameras.append(camera)

    return cameras


def camera_render_object(obj, camera):
    glLoadIdentity()

    # Apply the view matrix from the current camera
    glMultMatrixf(camera.view_matrix)

    obj.render()


def camera_handle_mouse_down(event, camera):
    global rotate, move
    if event.button == 1:
        rotate = True
    elif event.button == 3:
        move = True


def camera_handle_mouse_motion(event, camera):
    global rotate, move
    i, j = event.rel
    scaling_factor = 0.2  # Adjust the scaling factor as needed

    if rotate:
        camera.position[0] += i * scaling_factor
        camera.position[1] -= j * scaling_factor
    if move:
        camera.position[0] += i * scaling_factor
        camera.position[1] -= j * scaling_factor


def camera_handle_input(camera):
    global rotate, move
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            handle_mouse_down(event, camera)
        elif event.type == MOUSEBUTTONUP:
            handle_mouse_up(event)
        elif event.type == MOUSEMOTION:
            camera_handle_mouse_motion(event, camera)


def camera_setup_projection(camera, width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(camera.field_of_view, width / float(height), 1, 100.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)


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
        width, height = 1000, 1000
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

    elif sys.argv[1] == "cam":
        if sys.argv[2] == "obj":
            obj = OBJ("models/Football.obj", swapyz=True)
            obj.generate()
            clock = pygame.time.Clock()
            width, height = 1000, 1000
            camera_setup_projection(init_camera(), width, height)
            current_camera = init_camera()
            target_camera = Camera(id=2, position=[0, 0, -5], direction=[0, 0, -1], up_vector=[0, 1, 0], field_of_view=60.0,
                                   transition_frames=60)
            frame_count = 0
            while True:
                clock.tick(30)
                camera_handle_input(current_camera)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                camera_render_object(obj, current_camera)
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
        elif sys.argv[2] == "json":
            objects = load_objects_from_json("objects.json")
            cameras = load_cameras_from_json("cameras.json")

            clock = pygame.time.Clock()
            width, height = 1000, 1000
            camera_setup_projection(cameras[0], width, height)
            current_camera_index = 0
            current_camera = cameras[current_camera_index]
            target_camera_index = (current_camera_index + 1) % len(cameras)
            target_camera = cameras[target_camera_index]
            frame_count = 0

            while True:
                clock.tick(30)
                camera_handle_input(current_camera)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                # Render all objects on the scene
                for obj in objects:
                    camera_render_object(obj, current_camera)

                pygame.display.flip()

                # Check for camera switch
                if frame_count <= current_camera.transition_frames:
                    # Interpolate between current and target camera
                    current_camera.interpolate(target_camera, frame_count, current_camera.transition_frames)
                    frame_count += 1
                else:
                    frame_count = 0
                    # Switch to the next camera
                    current_camera_index = target_camera_index
                    current_camera = cameras[current_camera_index]
                    target_camera_index = (current_camera_index + 1) % len(cameras)
                    target_camera = cameras[target_camera_index]


if __name__ == "__main__":
    main()
