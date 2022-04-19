# -*- coding: utf-8 -*-
import os
import sys

# For Linux/Wayland users.
if os.getenv("XDG_SESSION_TYPE") == "wayland":
    os.environ["XDG_SESSION_TYPE"] = "x11"

import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
from ctypes import c_void_p
import numpy as np

from shader import Shader
from utilities import timefunc
from IgorIO import load_itx

arpes_data_igor = load_itx("La1_0020_136.itx")

active = {
    "Diagnostics": True,
    "OpenGL Window": True,
    "Controls": True,
    "tooltip": False,
    "menu bar": False,
    "popup": False,
    "popup modal": False,
    "popup context item": False,
    "popup context window": False,
    "drag drop": False,
    "group": False,
    "tab bar": False,
    "list box": False,
    "popup context void": False,
    "table": False,
}

path_to_font = None  # "path/to/font.ttf"
# path_to_font = "/System/Library/Fonts/Supplemental/Arial.tff"

opened_state = True

class MyGLWindow:
    def __init__(self):

        self.screen_quad_verts = np.array([[-1,-1],[1,-1],[1,1],[-1,-1],[1,1],[-1,1]], dtype = np.float32)
        self.VAO = gl.glGenVertexArrays(1)
        self.VBO = gl.glGenBuffers(1)
        self.FBO = gl.glGenFramebuffers(1)
        self.render_texture = gl.glGenTextures(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBindVertexArray(self.VAO)

        self.shader = Shader()
        self.shader_program = self.shader.compile()

        self.low_intensity_color = 0,0,0
        self.high_intensity_color = 1,1,1
        self.shader.set_vec3('u_low_color', self.low_intensity_color)
        self.shader.set_vec3('u_high_color', self.high_intensity_color)
        
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.screen_quad_verts.nbytes, self.screen_quad_verts, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.FBO)

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.render_texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F, arpes_data_igor.data.shape[0], arpes_data_igor.data.shape[1], 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, c_void_p(0))
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)	
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.render_texture, 0)
        
        #Sending ARPES data
        self.ARPES_texture = gl.glGenTextures(1)
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.ARPES_texture)
        self.shader.set_int('arpes_data', 1)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RED, arpes_data_igor.data.shape[1], arpes_data_igor.data.shape[0], 0, gl.GL_RED, gl.GL_FLOAT, (arpes_data_igor.data/np.max(arpes_data_igor.data)).astype(np.float32))
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)	
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

        self._cleanup()
    
    @timefunc
    def draw(self):
        w_width, w_height = imgui.get_window_size()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.FBO)
        gl.glClearColor(1,0,0,1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glActiveTexture(gl.GL_TEXTURE0)

        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBindVertexArray(self.VAO)
        gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT0)
        self.shader.use_program()
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.screen_quad_verts.shape[0])
        pos = imgui.get_cursor_screen_pos()
        imgui.image(self.render_texture, arpes_data_igor.data.shape[0], arpes_data_igor.data.shape[1], (0,1), (1,0)) 
        
        self._cleanup()
        
    def _cleanup(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)
        gl.glUseProgram(0)
        gl.glDrawBuffer(gl.GL_FRONT)


def frame_commands(my_subwindow, time_to_render_frame):
    gl.glClearColor(0.15, 0.15, 0.15, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    io = imgui.get_io()

    if io.key_ctrl and io.keys_down[glfw.KEY_Q]:
        sys.exit(0)

    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("File", True):
            clicked_quit, selected_quit = imgui.menu_item("Quit", "Ctrl+Q", False, True)

            if clicked_quit:
                sys.exit(0)

            imgui.end_menu()
        imgui.end_main_menu_bar()

    # turn windows on/off
    imgui.begin("Active examples")
    for label, enabled in active.copy().items():
        _, enabled = imgui.checkbox(label, enabled)
        active[label] = enabled
    imgui.end()

    if active["OpenGL Window"]:
        imgui.set_next_window_size(arpes_data_igor.data.shape[0],arpes_data_igor.data.shape[1])
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, imgui.Vec2(0,0))
        imgui.begin("Awesome Stuff Here", flags = (imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_SCROLL_WITH_MOUSE))
        # imgui.begin_child("Renderwindow")
        draw_time, _ = my_subwindow.draw()
        # imgui.end_child()
        imgui.end()
        imgui.pop_style_var(1) 

    if active["Diagnostics"]:
        imgui.begin("Time information")
        imgui.text(f"Time to render whole frame: {time_to_render_frame*1000 : 0.2f}ms")
        imgui.text(f"Total FPS: {1/(time_to_render_frame+1e-10) : 0.0f}FPS")
        if active["OpenGL Window"]:
            imgui.text(f"Time to render OpenGL window: {draw_time*1000 : 0.2f}ms")
            imgui.text(f"Framerate of OpenGL Window: {1/draw_time : 0.0f}FPS")
        imgui.end()

    if active["Controls"]:
        imgui.begin("Simulation Controls")
        
        changed_high_color, my_subwindow.low_intensity_color = imgui.color_edit3("Low Intensity Color", *my_subwindow.low_intensity_color)
        if changed_high_color:
            my_subwindow.shader.set_vec3('u_low_color', my_subwindow.low_intensity_color)
        
        changed_low_color, my_subwindow.high_intensity_color = imgui.color_edit3("High Intensity Color", *my_subwindow.high_intensity_color)
        if changed_low_color:
            my_subwindow.shader.set_vec3('u_high_color', my_subwindow.high_intensity_color)
        imgui.end()

    if active["tooltip"]:
        imgui.begin("Example: tooltip")
        imgui.button("Click me!")
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("This button is clickable.")
            imgui.end_tooltip()
        imgui.end()

    if active["menu bar"]:
        try:
            flags = imgui.WINDOW_MENU_BAR
            imgui.begin("Child Window - File Browser", flags=flags)
            if imgui.begin_menu_bar():
                if imgui.begin_menu('File'):
                    clicked, state = imgui.menu_item('Close')
                    if clicked:
                        active["menu bar"] = False
                        raise Exception
                    imgui.end_menu()
                imgui.end_menu_bar()
            imgui.end()
        except Exception:
            print("exception caught, but too late!")

    if active["popup"]:
        imgui.begin("Example: simple popup")
        if imgui.button("select"):
            imgui.open_popup("select-popup")
        imgui.same_line()
        if imgui.begin_popup("select-popup"):
            imgui.text("Select one")
            imgui.separator()
            imgui.selectable("One")
            imgui.selectable("Two")
            imgui.selectable("Three")
            imgui.end_popup()
        imgui.end()

    if active["popup modal"]:
        imgui.begin("Example: simple popup modal")
        if imgui.button("Open Modal popup"):
            imgui.open_popup("select-popup-modal")
        imgui.same_line()
        if imgui.begin_popup_modal("select-popup-modal")[0]:
            imgui.text("Select an option:")
            imgui.separator()
            imgui.selectable("One")
            imgui.selectable("Two")
            imgui.selectable("Three")
            imgui.end_popup()
        imgui.end()

    if active["popup context item"]:
        imgui.begin("Example: popup context view")
        imgui.text("Right-click to set value.")
        if imgui.begin_popup_context_item("Item Context Menu"):
            imgui.selectable("Set to Zero")
            imgui.end_popup()
        imgui.end()

    if active["popup context window"]:
        imgui.begin("Example: popup context window")
        if imgui.begin_popup_context_window():
            imgui.selectable("Clear")
            imgui.end_popup()
        imgui.end()

    if active["popup context void"]:
        if imgui.begin_popup_context_void():
            imgui.selectable("Clear")
            imgui.end_popup()

    if active["drag drop"]:
        imgui.begin("Example: drag and drop")
        imgui.button('source')
        if imgui.begin_drag_drop_source():
            imgui.set_drag_drop_payload('itemtype', b'payload')
            imgui.button('dragged source')
            imgui.end_drag_drop_source()
        imgui.button('dest')
        if imgui.begin_drag_drop_target():
            payload = imgui.accept_drag_drop_payload('itemtype')
            if payload is not None:
                print('Received:', payload)
            imgui.end_drag_drop_target()
        imgui.end()

    if active["group"]:
        imgui.begin("Example: item groups")
        imgui.begin_group()
        imgui.text("First group (buttons):")
        imgui.button("Button A")
        imgui.button("Button B")
        imgui.end_group()
        imgui.same_line(spacing=50)
        imgui.begin_group()
        imgui.text("Second group (text and bullet texts):")
        imgui.bullet_text("Bullet A")
        imgui.bullet_text("Bullet B")
        imgui.end_group()
        imgui.end()

    if active["tab bar"]:
        imgui.begin("Example Tab Bar")
        if imgui.begin_tab_bar("MyTabBar"):
            if imgui.begin_tab_item("Item 1")[0]:
                imgui.text("Here is the tab content!")
                imgui.end_tab_item()
            if imgui.begin_tab_item("Item 2")[0]:
                imgui.text("Another content...")
                imgui.end_tab_item()
            global opened_state
            selected, opened_state = imgui.begin_tab_item("Item 3", opened=opened_state)
            if selected:
                imgui.text("Hello Saylor!")
                imgui.end_tab_item()
            imgui.end_tab_bar()
        imgui.end()

    if active["list box"]:
        imgui.begin("Example: custom listbox")
        if imgui.begin_list_box("List", 200, 100):
            imgui.selectable("Selected", True)
            imgui.selectable("Not Selected", False)
            imgui.end_list_box()
        imgui.end()

    if active["table"]:
        imgui.begin("Example: table")
        if imgui.begin_table("data", 2):
            imgui.table_next_column()
            imgui.table_header("A")
            imgui.table_next_column()
            imgui.table_header("B")

            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("123")

            imgui.table_next_column()
            imgui.text("456")

            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("789")

            imgui.table_next_column()
            imgui.text("111")

            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("222")

            imgui.table_next_column()
            imgui.text("333")
            imgui.end_table()
        imgui.end()
        

@timefunc
def render_frame(impl, window, my_subwindow, font, time_to_render_frame):
    glfw.poll_events()
    impl.process_inputs()
    imgui.new_frame()

    gl.glClearColor(0.1, 0.1, 0.1, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    if font is not None:
        imgui.push_font(font)
    frame_commands(my_subwindow, time_to_render_frame)
    if font is not None:
        imgui.pop_font()

    imgui.render()
    
    impl.render(imgui.get_draw_data())
    

    

    glfw.swap_buffers(window)


def impl_glfw_init():
    width, height = 1300, 720
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    my_subwindow = MyGLWindow()

    return window, my_subwindow

def main():
    imgui.create_context()
    window, my_subwindow = impl_glfw_init()

    impl = GlfwRenderer(window)

    io = imgui.get_io()
    jb = io.fonts.add_font_from_file_ttf(path_to_font, 30) if path_to_font is not None else None
    impl.refresh_font_texture()

    previous_time = 0
    while not glfw.window_should_close(window):
        time_to_render_whole_frame, _ = render_frame(impl, window, my_subwindow, jb, previous_time)
        previous_time = time_to_render_whole_frame

    impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    main()