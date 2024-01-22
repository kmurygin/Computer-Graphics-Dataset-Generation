from pygame.constants import *
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OBJ import *
import json
import sys
from Camera import *
from datetime import datetime
import os

rotate = False
move = False


def init_camera():
    """
    Initialize the camera with predefined parameters.

    Returns:
    Camera: The initialized camera object.
    """
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
    """
    Load camera data from a JSON file.

    Parameters:
    - json_filename (str): The filename of the JSON file containing camera data.

    Returns:
    list: A list of Camera objects.
    """
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
    """
    Render an object with the specified camera settings.

    Parameters:
    - obj (OBJ): The object to render.
    - camera (Camera): The camera used for rendering.

    Returns:
    None
    """
    glLoadIdentity()

    # Apply the view matrix from the current camera
    glMultMatrixf(camera.view_matrix)

    obj.render()


def camera_handle_mouse_down(event, camera):
    """
    Handle mouse button down event for camera interaction.

    Parameters:
    - event: The mouse button down event.
    - camera (Camera): The camera to interact with.

    Returns:
    None
    """
    global rotate, move
    if event.button == 1:
        rotate = True
    elif event.button == 3:
        move = True


def camera_handle_mouse_motion(event, camera):
    """
    Handle mouse motion event for camera interaction.

    Parameters:
    - event: The mouse motion event.
    - camera (Camera): The camera to interact with.

    Returns:
    None
    """
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
    """
    Handle input events for camera interaction.

    Parameters:
    - camera (Camera): The camera to interact with.

    Returns:
    None
    """
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
    """
    Set up the projection matrix based on camera parameters.

    Parameters:
    - camera (Camera): The camera for which to set up the projection.
    - width (int): The width of the viewport.
    - height (int): The height of the viewport.

    Returns:
    None
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(camera.field_of_view, width / float(height), 1, 100.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)


def init():
    """
    Initialize the Pygame and OpenGL environment.

    Returns:
    None
    """
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

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)


def load_objects_from_json(json_filename):
    """
    Load object data from a JSON file.

    Parameters:
    - json_filename (str): The filename of the JSON file containing object data.

    Returns:
    list: A list of OBJ objects.
    """
    with open(json_filename, 'r') as file:
        objects_data = json.load(file)

    objects = []
    for obj_data in objects_data:
        obj = OBJ(obj_data["filename"], obj_data.get("swapyz", False), obj_data.get("position"),
                  obj_data.get("rotation"))
        objects.append(obj)

    return objects


def setup_projection(width, height):
    """
    Set up the projection matrix.

    Parameters:
    - width (int): The width of the viewport.
    - height (int): The height of the viewport.

    Returns:
    None
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90.0, width / float(height), 1, 100.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)


def handle_input(rx, ry, tx, ty, zpos):
    """
    Handle user input events.

    Parameters:
    - rx (list): List containing the rotation around the x-axis.
    - ry (list): List containing the rotation around the y-axis.
    - tx (list): List containing the translation along the x-axis.
    - ty (list): List containing the translation along the y-axis.
    - zpos (list): List containing the zoom position.

    Returns:
    None
    """
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
    """
    Handle mouse button down event.

    Parameters:
    - event: The mouse button down event.
    - zpos (list): List containing the zoom position.

    Returns:
    None
    """
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
    """
    Handle mouse button up event.

    Parameters:
    - event: The mouse button up event.

    Returns:
    None
    """
    global rotate, move
    if event.button == 1:
        rotate = False
    elif event.button == 3:
        move = False


def handle_mouse_motion(event, rx, ry, tx, ty):
    """
    Handle mouse motion event.

    Parameters:
    - event: The mouse motion event.
    - rx (list): List containing the rotation around the x-axis.
    - ry (list): List containing the rotation around the y-axis.
    - tx (list): List containing the translation along the x-axis.
    - ty (list): List containing the translation along the y-axis.

    Returns:
    None
    """
    global rotate, move
    i, j = event.rel
    if rotate:
        rx[0] += i
        ry[0] += j
    if move:
        tx[0] += i
        ty[0] -= j


def render_phong(self):
    """
    Render the object using Phong shading.

    Parameters:
    - self: The OBJ object.

    Returns:
    None
    """
    glBegin(GL_TRIANGLES)
    for face in self.faces:
        for i in range(3):
            vertex_index = face[i][0]
            normal_index = face[i][2]

            glNormal3fv(self.normals[normal_index])
            glVertex3fv(self.vertices[vertex_index])
    glEnd()


def render_object(obj, tx, ty, zpos, rx, ry):
    """
    Render an object with transformations.

    Parameters:
    - obj (OBJ): The object to render.
    - tx (list): List containing the translation along the x-axis.
    - ty (list): List containing the translation along the y-axis.
    - zpos (list): List containing the zoom position.
    - rx (list): List containing the rotation around the x-axis.
    - ry (list): List containing the rotation around the y-axis.

    Returns:
    None
    """
    glLoadIdentity()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))

    glTranslate(tx[0] / 20., ty[0] / 20., -zpos[0])
    glRotate(ry[0], 1, 0, 0)
    glRotate(rx[0], 0, 1, 0)
    obj.render()


def create_folder():
    """
    Create a folder with a timestamped name.

    Returns:
    str: The name of the created folder.
    """
    time_now = datetime.now()
    folder_name = time_now.strftime('%d%m%Y_%H%M')
    os.makedirs(f'./{folder_name}')
    return folder_name


def capture_screenshot(camera_id, folder_name):
    """
    Capture and save a screenshot for a specific camera.

    Parameters:
    - camera_id (int): The ID of the camera.
    - folder_name (str): The name of the folder to save the screenshot.

    Returns:
    None
    """
    screen = pygame.display.get_surface()
    size = screen.get_size()
    buffer = glReadPixels(0, 0, *size, GL_RGBA, GL_UNSIGNED_BYTE)
    screen_surf = pygame.image.fromstring(buffer, size, "RGBA")
    pygame.image.save(screen_surf, f"./{folder_name}/screenshot{camera_id}.jpg")


def render_with_one_camera(objects):
    """
    Render the scene using a single camera.

    Parameters:
    - objects (list): A list of objects to render.

    Returns:
    None
    """
    clock = pygame.time.Clock()
    width, height = 1000, 1000
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


def render_with_some_cameras(objects, cameras):
    """
    Render the scene using multiple cameras.

    Parameters:
    - objects (list): A list of objects to render.
    - cameras (list): A list of Camera objects.

    Returns:
    None
    """
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


def main():
    """
    Main function to run the program based on command line arguments.

    Returns:
    None
    init()
    if sys.argv[1] == "obj":
        objects = [OBJ("models/Football.obj", swapyz=True)]
        render_with_one_camera(objects)

    elif sys.argv[1] == "json":
        objects = load_objects_from_json("objects.json")
        render_with_one_camera(objects)

    elif sys.argv[1] == "cam":
        if sys.argv[2] == "obj":
            objects = [OBJ("models/Football.obj", swapyz=True)]
            cameras = [Camera(id=2, position=[0, 0, -5], direction=[0, 0, -1], up_vector=[0, 1, 0], field_of_view=60.0,
                              transition_frames=60),
                       Camera(id=3, position=[5, 5, 5], direction=[0, 0, 0], up_vector=[0, 1, 0], field_of_view=60.0,
                              transition_frames=60)]
            render_with_some_cameras(objects, cameras)

        elif sys.argv[2] == "json":
            objects = load_objects_from_json("objects.json")
            cameras = load_cameras_from_json("cameras.json")
            render_with_some_cameras(objects, cameras)


if __name__ == "__main__":
    main()
