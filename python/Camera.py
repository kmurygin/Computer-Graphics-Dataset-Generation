class Camera:
    def __init__(self, position, direction, up_vector, field_of_view, transition_frames):
        self.position = position
        self.direction = direction
        self.up_vector = up_vector
        self.field_of_view = field_of_view
        self.transition_frames = transition_frames

        # Calculate the view matrix
        self.view_matrix = self.calculate_view_matrix()

    def calculate_view_matrix(self):
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
        # Linear interpolation for smooth transition
        t = current_frame / total_frames
        self.position = lerp(self.position, target_camera.position, t)
        self.direction = lerp(self.direction, target_camera.direction, t)
        self.up_vector = lerp(self.up_vector, target_camera.up_vector, t)

        # Recalculate the view matrix after interpolation
        self.view_matrix = self.calculate_view_matrix()


# Helper functions for vector operations
def cross_product(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ]

def normalize(v):
    length = sum(v_i**2 for v_i in v)**0.5
    if length != 0:
        return [v_i / length for v_i in v]
    else:
        return v
def dot_product(a, b):
    return sum(a_i * b_i for a_i, b_i in zip(a, b))


# linear interpolation
def lerp(a, b, t):
    return [a_i + (b_i - a_i) * t for a_i, b_i in zip(a, b)]
