from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
import math

# Global animation variables
ripples = []   # Each ripple: [x, y, radius, speed]
last_time = time.time()

# ------------------- Midpoint Circle Algorithm -------------------
def midpoint_circle(xc, yc, r):
    x, y = 0, r
    p = 1 - r
    points = []

    while x <= y:
        points.extend([
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x),
            (xc + y, yc - x), (xc - y, yc - x)
        ])
        if p < 0:
            p += 2 * x + 3
        else:
            p += 2 * (x - y) + 5
            y -= 1
        x += 1
    return points

# ------------------- Draw Ripple -------------------
def draw_ripple(xc, yc, r):
    glBegin(GL_POINTS)
    glColor3f(0.2, 0.6, 1.0)
    for x, y in midpoint_circle(xc, yc, r):
        glVertex2f(x / 400, y / 400)
    glEnd()

# ------------------- Display -------------------
def display():
    global ripples, last_time
    glClear(GL_COLOR_BUFFER_BIT)

    # Time-based animation
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Update and draw ripples
    new_ripples = []
    for r in ripples:
        r[2] += r[3] * dt * 50  # increase radius
        if r[2] < 300:  # keep on screen
            draw_ripple(r[0], r[1], int(r[2]))
            new_ripples.append(r)
    ripples = new_ripples

    glutSwapBuffers()

# ------------------- Animation -------------------
def timer(v):
    glutPostRedisplay()
    glutTimerFunc(16, timer, 1)  # ~60 FPS

# ------------------- Mouse Input -------------------
def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Create a ripple at mouse location
        ripples.append([x - 400, 400 - y, 5, 50])  # x, y, radius, speed

# ------------------- Setup -------------------
def init():
    glClearColor(0.0, 0.0, 0.05, 1.0)
    glPointSize(2.0)

# ------------------- Main -------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(800, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Water Ripple Simulation - Midpoint Circle Algorithm")
    init()
    glutDisplayFunc(display)
    glutMouseFunc(mouse)
    glutTimerFunc(0, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
