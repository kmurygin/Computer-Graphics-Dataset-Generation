import pygame
from OpenGL.GL import *
import os

PHONG_AMBIENT = (0.2, 0.2, 0.2, 1.0)
PHONG_DIFFUSE = (0.8, 0.8, 0.8, 1.0)
PHONG_SPECULAR = (1.0, 1.0, 1.0, 1.0)
PHONG_SHININESS = 50.0

# Klasa reprezentująca obiekt wczytany z pliku Wavefront OBJ
class OBJ:
    """
    Represents an object loaded from a Wavefront OBJ file.

    Attributes:
    - generate_on_init (bool): If True, generate OpenGL display list on object initialization.
    - PHONG_AMBIENT, PHONG_DIFFUSE, PHONG_SPECULAR, PHONG_SHININESS (tuple): Phong shading parameters.

    Methods:
    - load_texture(cls, image_file): Load texture from an image file.
    - load_material(cls, filename): Load materials from an .mtl file.
    - __init__(self, filename, swapyz=False, position=None, rotation=None): Constructor for OBJ class.
    - generate(self): Generate OpenGL display list for rendering.
    - render(self): Render the object in the scene.
    - free(self): Free resources associated with the object.
    """
    generate_on_init = True

    # Metoda do wczytywania tekstur z pliku obrazu
    @classmethod
    def load_texture(cls, image_file):
        """
        Load texture from an image file.

        Parameters:
        - image_file (str): The path to the image file.

        Returns:
        int: OpenGL texture ID.
        """
        surf = pygame.image.load(image_file)
        image = pygame.image.tostring(surf, 'RGBA', 1)
        ix, iy = surf.get_rect().size
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        return texid

    # Metoda do wczytywania materiałów z pliku .mtl
    @classmethod
    def load_material(cls, filename):
        """
        Load materials from an .mtl file.

        Parameters:
        - filename (str): The path to the .mtl file.

        Returns:
        dict: Dictionary of material properties.
        """
        contents = {}
        mtl = None
        dirname = os.path.dirname(filename)

        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'newmtl':
                mtl = contents[values[1]] = {}
            elif mtl is None:
                raise ValueError("mtl file doesn't start with newmtl stmt")
            elif values[0] == 'map_Kd':
                mtl[values[0]] = values[1]
                imagefile = os.path.join(dirname, mtl['map_Kd'])
                mtl['texture_Kd'] = cls.load_texture(imagefile)
            else:
                mtl[values[0]] = list(map(float, values[1:]))
        return contents

    # Konstruktor klasy OBJ
    def __init__(self, filename, swapyz=False, position=None, rotation=None):
        """Loads a Wavefront OBJ file. """
        """
        Constructor for the OBJ class.

        Parameters:
        - filename (str): The path to the Wavefront OBJ file.
        - swapyz (bool): If True, swap Y and Z coordinates.
        - position (list): The initial position of the object.
        - rotation (list): The initial rotation of the object.
        """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.gl_list = 0
        dirname = os.path.dirname(filename)

        material = None
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = self.load_material(os.path.join(dirname, values[1]))
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))

        self.position = position or [0, 0, 0]
        self.rotation = rotation or [0, 0, 0]

        if self.generate_on_init:
            self.generate()

    # Metoda do generowania listy wyświetlania obiektu w OpenGL
    def generate(self):
        """
        Generate OpenGL display list for rendering.

        Returns:
        None
        """
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)

        glPushMatrix()  # Zachowanie aktualnej macierzy modelView
        glTranslatef(*self.position)  # Zastosowanie pozycji obiektu

        for face in self.faces:
            vertices, normals, texture_coords, material = face

            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                glColor(*mtl['Kd'])

            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, mtl['Ka'])
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, mtl['Kd'])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, PHONG_SPECULAR)
            glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, PHONG_SHININESS)

            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()

        glPopMatrix()   # Przywrócenie oryginalnej macierzy modelView
        glDisable(GL_TEXTURE_2D)
        glEndList()

    # Metoda do renderowania obiektu w scenie
    def render(self):
        """
        Render the object in the scene.

        Returns:
        None
        """
        glEnable(GL_TEXTURE_2D)
        glCallList(self.gl_list)
        glDisable(GL_TEXTURE_2D)

    # Metoda do zwolnienia zasobów związanych z obiektem
    def free(self):
        """
        Free resources associated with the object.

        Returns:
        None
        """
        glDeleteLists([self.gl_list])
