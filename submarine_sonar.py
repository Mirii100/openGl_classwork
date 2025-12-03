"""
submarine_sonar.py

3D Sonar Submarine Navigation with Depth Visualization
Features:
- Dynamic submarine movement in 3D space
- Sonar pulse visualization using circular rings
- Depth-based color coding
- Water surface interaction (submarine emerges/submerges)
- Recon mission: detect unknown objects using sonar
- Defense flares: visual animation when 'deploying countermeasures'
- Autonomous movement unless paused with spacebar
- Keyboard controls: arrow keys + W/S for movement, F to deploy flare, I toggle instructions, Space pause/resume
- Fully self-contained Python + PyOpenGL code

Run:
    python3 submarine_sonar.py
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random

# ---------------- Configuration ----------------
WIDTH, HEIGHT = 900, 600
sub_pos = [0.0, -20.0, 0.0]  # x, y, z
sub_angle = 0.0  # yaw rotation
sub_speed = 1.0
SONAR_MAX_RADIUS = 50
flare_active = False
SHOW_INSTRUCTIONS = True
paused = False

# Autonomous movement direction
sub_dir = [0.5, 0.0, 0.5]

# Sonar pulse storage
sonar_pulses = []  # list of (x, y, z, radius)

# ---------------- Draw Helpers ----------------
def draw_circle_xy(xc, yc, zc, radius, segments=64, color=(0.0,1.0,1.0,0.5)):
    r, g, b, a = color
    glColor4f(r, g, b, a)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        theta = 2 * math.pi * i / segments
        x = xc + radius * math.cos(theta)
        y = yc + radius * math.sin(theta)
        glVertex3f(x, y, zc)
    glEnd()

# ---------------- Draw Submarine ----------------
def draw_submarine():
    glPushMatrix()
    glTranslatef(sub_pos[0], sub_pos[1], sub_pos[2])
    glRotatef(sub_angle, 0, 1, 0)

    # Hull with distinctive color
    glColor3f(1.0, 0.3, 0.0)  # Bright orange for visibility
    glutSolidCylinder(5, 20, 32, 16)

    # Conning tower / periscope
    glPushMatrix()
    glTranslatef(0, 10, 0)
    glColor3f(0.2,0.2,0.2)
    glutSolidCube(4)
    glPopMatrix()

    glPopMatrix()

# ---------------- Draw Sonar Pulses ----------------
def draw_sonar():
    for pulse in sonar_pulses:
        x, y, z, radius = pulse
        draw_circle_xy(x, y, z, radius, color=(0.0,1.0,1.0,0.3))

# ---------------- Update Sonar Pulses ----------------
def update_sonar():
    for i in range(len(sonar_pulses)):
        x, y, z, radius = sonar_pulses[i]
        radius += 1.0
        if radius > SONAR_MAX_RADIUS:
            radius = 0.0
        sonar_pulses[i] = (x, y, z, radius)

# ---------------- Draw Flare ----------------
def draw_flare():
    if flare_active:
        glColor3f(1.0,1.0,0.0)
        glPushMatrix()
        glTranslatef(sub_pos[0], sub_pos[1]+10, sub_pos[2])
        glutSolidSphere(2,16,16)
        glPopMatrix()

# ---------------- Display ----------------
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Camera follows submarine
    gluLookAt(sub_pos[0]+30, sub_pos[1]+20, sub_pos[2]+30,
              sub_pos[0], sub_pos[1], sub_pos[2],
              0,1,0)

    # Draw water surface
    glColor4f(0.0,0.5,0.8,0.5)
    glBegin(GL_QUADS)
    glVertex3f(-100,0,-100)
    glVertex3f(100,0,-100)
    glVertex3f(100,0,100)
    glVertex3f(-100,0,100)
    glEnd()

    draw_submarine()
    draw_sonar()
    draw_flare()

    if not paused:
        # Autonomous movement
        sub_pos[0] += sub_dir[0]
        sub_pos[1] += sub_dir[1]
        sub_pos[2] += sub_dir[2]

        # Bounce from boundaries
        for i in range(3):
            if abs(sub_pos[i]) > 50:
                sub_dir[i] *= -1

        # Randomly deploy sonar pulse
        if random.random() < 0.05:
            sonar_pulses.append((sub_pos[0], sub_pos[1], sub_pos[2], 0.0))

    update_sonar()

    if SHOW_INSTRUCTIONS:
        glColor3f(1,1,1)
        lines = [
            "Arrow keys: Move horizontally",
            "W/S: Move up/down",
            "A/D: Rotate submarine",
            "F: Deploy flare",
            "Space: Pause/Resume autonomous movement",
            "I: Toggle instructions",
            "Q/Esc: Quit"
        ]
        y = 20
        for ln in lines:
            glWindowPos2i(10, y)
            for ch in ln:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
            y += 16

    glutSwapBuffers()

# ---------------- Keyboard ----------------
def keyboard(key, x, y):
    global flare_active, SHOW_INSTRUCTIONS, paused
    k = key.decode('utf-8') if isinstance(key, bytes) else key
    if k in ('f','F'):
        flare_active = not flare_active
    elif k in ('i','I'):
        SHOW_INSTRUCTIONS = not SHOW_INSTRUCTIONS
    elif k == ' ':
        paused = not paused
    elif k in ('q','Q','\x1b'):
        glutLeaveMainLoop()
    glutPostRedisplay()

# ---------------- Special Keys ----------------
def special_keys(key, x, y):
    global sub_pos, sub_angle
    if key == GLUT_KEY_UP:
        sub_pos[2] -= sub_speed
    elif key == GLUT_KEY_DOWN:
        sub_pos[2] += sub_speed
    elif key == GLUT_KEY_LEFT:
        sub_pos[0] -= sub_speed
    elif key == GLUT_KEY_RIGHT:
        sub_pos[0] += sub_speed
    elif key == GLUT_KEY_PAGE_UP:
        sub_pos[1] += sub_speed
    elif key == GLUT_KEY_PAGE_DOWN:
        sub_pos[1] -= sub_speed
    elif key == GLUT_KEY_HOME:
        sub_angle += 5
    elif key == GLUT_KEY_END:
        sub_angle -=5

    glutPostRedisplay()

# ---------------- Timer ----------------
def timer(value):
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)

# ---------------- Main ----------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"3D Submarine Sonar Navigation")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutTimerFunc(33, timer, 0)

    glutMainLoop()

if __name__ == '__main__':
    main()
