import numpy as np

import imageio

import OpenGL.GL as gl


class CubeMap:

    def __init__(self, cube_map_img=None):

        self.cube_map_img = cube_map_img


    @property
    def cube_map_img(self):
        return self._cube_map_img

    @cube_map_img.setter(self, cube_map_img):

        if not isinstance(cube_map_img, np.ndarray):
            cube_map_img = imageio.imread(cube_map_img)

        self._cube_map_img = cube_map_img


"""

        (self.img_h, self.img_w, self.img_c) = self.cube_map_img.shape

        self.face_size = self.img_h // 3

        assert self.img_w == self.face_size * 4

        face_attrs = (
            None,
            "y_pos",
            None,
            None,
            "x_neg",
            "z_pos",
            "x_pos",
            "z_neg",
            None,
            "y_neg",
            None,
            None,
        )

        for (i_face, face_attr) in enumerate(face_attrs):

            if not face_attr:
                continue

            (i_row, i_col) = np.unravel_index(indices=i_face, shape=(3, 4))

            row_slice = slice(
                i_row * self.face_size, i_row * self.face_size + self.face_size
            )
            col_slice = slice(
                i_col * self.face_size, i_col * self.face_size + self.face_size
            )

            setattr(
                self, face_attr, np.copy(self.cube_map_img[row_slice, col_slice, :])
            )

        self.target_map = {
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: self.x_pos,
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: self.x_neg,
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: self.y_pos,
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: self.y_neg,
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: self.z_pos,
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: self.z_neg,
        }

        self.pos = np.array(
            [
                -1.0,  1.0, -1.0,
                -1.0, -1.0, -1.0,
                 1.0, -1.0, -1.0,
                 1.0, -1.0, -1.0,
                 1.0,  1.0, -1.0,
                -1.0,  1.0, -1.0,

                -1.0, -1.0,  1.0,
                -1.0, -1.0, -1.0,
                -1.0,  1.0, -1.0,
                -1.0,  1.0, -1.0,
                -1.0,  1.0,  1.0,
                -1.0, -1.0,  1.0,

                 1.0, -1.0, -1.0,
                 1.0, -1.0,  1.0,
                 1.0,  1.0,  1.0,
                 1.0,  1.0,  1.0,
                 1.0,  1.0, -1.0,
                 1.0, -1.0, -1.0,

                -1.0, -1.0,  1.0,
                -1.0,  1.0,  1.0,
                 1.0,  1.0,  1.0,
                 1.0,  1.0,  1.0,
                 1.0, -1.0,  1.0,
                -1.0, -1.0,  1.0,

                -1.0,  1.0, -1.0,
                 1.0,  1.0, -1.0,
                 1.0,  1.0,  1.0,
                 1.0,  1.0,  1.0,
                -1.0,  1.0,  1.0,
                -1.0,  1.0, -1.0,

                -1.0, -1.0, -1.0,
                -1.0, -1.0,  1.0,
                 1.0, -1.0, -1.0,
                 1.0, -1.0, -1.0,
                -1.0, -1.0,  1.0,
                 1.0, -1.0,  1.0
            ]
        )
        
        self.apos = np.array(
            [
                -1, -1, -1,
                -1, -1, 1,
                -1, 1, 1,
                -1, 1, 1,
                -1, 1, -1,
                -1, -1, -1
            ]
        ).astype("float")

def cubemapVals(radius, clockwise = True):

    a = math.sqrt(3 * (radius**2))
        
    #ZPOS
    pos =  [(-a,a,a),(a,a,a),(-a,-a,a)]
    pos += [(-a,-a,a),(a,a,a),(a,-a,a)]
    #ZNEG
    pos += [(a,a,-a),(-a,a,-a),(-a,-a,-a)]
    pos += [(a,a,-a),(-a,-a,-a),(a,-a,-a)]
    #XNEG
    pos += [(-a,a,-a),(-a,a,a),(-a,-a,-a)]
    pos += [(-a,-a,-a),(-a,a,a),(-a,-a,a)]
    #XPOS
    pos += [(a,a,a),(a,a,-a),(a,-a,-a)]
    pos += [(a,a,a),(a,-a,-a),(a,-a,a)]
    #YPOS
    pos += [(-a,a,a),(-a,a,-a),(a,a,a)]
    pos += [(a,a,a),(-a,a,-a),(a,a,-a)]
    #YNEG
    pos += [(-a,-a,-a),(-a,-a,a),(a,-a,a)]
    pos += [(-a,-a,-a),(a,-a,a),(a,-a,-a)]

    if not clockwise:
        for i in range(0,36,3):
            vn = pos[i]
            pos[i] = pos[i+1]
            pos[i+1] = vn

    return pos
"""
