class Camera:
    def __init__(self, id, position, direction, up_vector, field_of_view, transition_frames):
        """
        Initializes a Camera object.

        Parameters:
        - id (any): Unique identifier for the camera.
        - position (list): The position of the camera in 3D space.
        - direction (list): The direction the camera is facing.
        - up_vector (list): The up vector of the camera.
        - field_of_view (float): The field of view of the camera.
        - transition_frames (int): Number of frames for smooth transitions.

        Attributes:
        - id: Unique identifier for the camera.
        - position: The position of the camera in 3D space.
        - direction: The direction the camera is facing.
        - up_vector: The up vector of the camera.
        - field_of_view: The field of view of the camera.
        - transition_frames: Number of frames for smooth transitions.
        - view_matrix: The calculated view matrix for the camera.
        """
        self.id = id
        self.position = position
        self.direction = direction
        self.up_vector = up_vector
        self.field_of_view = field_of_view
        self.transition_frames = transition_frames

        # Calculate the view matrix
        self.view_matrix = self.calculate_view_matrix()

    def calculate_view_matrix(self):
        """
        Calculates the view matrix for the camera.

        Returns:
        list: The 4x4 view matrix representing the camera's view.
        """
        forward = self.direction
        right = cross_product(forward, self.up_vector)
        up = cross_product(right, forward)

        # Normalize the vectors
        forward = normalize(forward)
        right = normalize(right)
        up = normalize(up)

        view_matrix = [
            right[0], up[0], -forward[0], 0,
            right[1], up[1], -forward[1], 0,
            right[2], up[2], -forward[2], 0,
            -dot_product(right, self.position),
            -dot_product(up, self.position),
            dot_product(forward, self.position),
            1
        ]

        return view_matrix

    def interpolate(self, target_camera, current_frame, total_frames):
        """
        Performs linear interpolation between the current camera and a target camera.

        Parameters:
        - target_camera (Camera): The target camera for interpolation.
        - current_frame (int): The current frame in the interpolation.
        - total_frames (int): Total frames for the interpolation.

        Returns:
        None
        """
        # Linear interpolation for smooth transition
        t = current_frame / total_frames
        self.position = lerp(self.position, target_camera.position, t)
        self.direction = lerp(self.direction, target_camera.direction, t)
        self.up_vector = lerp(self.up_vector, target_camera.up_vector, t)

        # Recalculate the view matrix after interpolation
        self.view_matrix = self.calculate_view_matrix()


# Helper functions for vector operations
def cross_product(a, b):
    """
    Calculates the cross product of two 3D vectors.

    Parameters:
    - a (list): The first 3D vector.
    - b (list): The second 3D vector.

    Returns:
    list: The cross product vector.
    """
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ]

def normalize(v):
    """
    Normalizes a 3D vector.

    Parameters:
    - v (list): The 3D vector to be normalized.

    Returns:
    list: The normalized vector.
    """
    length = sum(v_i**2 for v_i in v)**0.5
    if length != 0:
        return [v_i / length for v_i in v]
    else:
        return v

def dot_product(a, b):
    """
    Calculates the dot product of two vectors.

    Parameters:
    - a (list): The first vector.
    - b (list): The second vector.

    Returns:
    float: The dot product of the two vectors.
    """
    return sum(a_i * b_i for a_i, b_i in zip(a, b))

def lerp(a, b, t):
    """
    Performs linear interpolation between two vectors.

    Parameters:
    - a (list): The starting vector.
    - b (list): The target vector.
    - t (float): Interpolation factor (between 0 and 1).

    Returns:
    list: The interpolated vector.
    """
    return [a_i + (b_i - a_i) * t for a_i, b_i in zip(a, b)]
