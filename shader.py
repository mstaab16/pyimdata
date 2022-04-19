from OpenGL.GL import *
from OpenGL.GL.shaders import *
from OpenGL.GLUT import *
import numpy as np

def load_shader_code(file):
    with open(file, "r") as file_context:
        shader_str = file_context.read()
    return shader_str

class Shader:
    def __init__(self):
        self.vertex_source = "vert.vert"
        self.fragment_source = "frag.frag"
        
    def compile(self):
        VERTEX_SHADER = compileShader(load_shader_code(self.vertex_source), GL_VERTEX_SHADER)
        print(f"Compiled vertex shader: {self.vertex_source}")

        FRAGMENT_SHADER = compileShader(load_shader_code(self.fragment_source), GL_FRAGMENT_SHADER)
        print(f"compiled fragment shader: {self.fragment_source}")
        
        self.program = compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        print(f"--------SHADER program ready!--------")
        return self.program

    
    def use_program(self):
        glUseProgram(self.program)

    def set_int(self, name: str, num: int) -> None:
        self.use_program()
        glUniform1i(glGetUniformLocation(self.program, name), num)
        glUseProgram(0)

    def set_float(self, name: str, num: int) -> None:
        self.use_program()
        glUniform1f(glGetUniformLocation(self.program, name), num)
        glUseProgram(0)

    def set_vec3(self, name: str, vec3: int) -> None:
        vec3 = np.array(vec3, dtype=np.float32)
        self.use_program()
        glUniform3fv(glGetUniformLocation(self.program, name), 1, vec3)
        glUseProgram(0)
