from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time

window_width, window_height = 800, 600
angle = 0

def draw_circle_midpoint(x_center, y_center, radius):
    glBegin(GL_POINTS)
    for (x, y) in midpoint_circle_points(x_center, y_center, radius):
        glVertex2f(x, y)
    glEnd()

def midpoint_circle_points(x_center, y_center, radius):
    x = radius
    y = 0
    p = 1 - radius
    points = []
    while x >= y:
        points.extend([
            (x_center + x, y_center + y),
            (x_center - x, y_center + y),
            (x_center + x, y_center - y),
            (x_center - x, y_center - y),
            (x_center + y, y_center + x),
            (x_center - y, y_center + x),
            (x_center + y, y_center - x),
            (x_center - y, y_center - x)
        ])
        y += 1
        if p <= 0:
            p = p + 2 * y + 1
        else:
            x -= 1
            p = p + 2 * y - 2 * x + 1
    return points

def draw_planet_orbit(x_center, y_center, radius, color):
    glColor3f(*color)
    draw_circle_midpoint(x_center, y_center, radius)

def draw_planet(x, y, size, color):
    glColor3f(*color)
    glBegin(GL_POLYGON)
    for theta in range(0, 360, 10):
        glVertex2f(x + size * math.cos(math.radians(theta)),
                   y + size * math.sin(math.radians(theta)))
    glEnd()

def display():
    global angle
    glClear(GL_COLOR_BUFFER_BIT)
    glPointSize(2)

    # Draw orbits
    draw_planet_orbit(0, 0, 100, (0.4, 0.4, 0.4))
    draw_planet_orbit(0, 0, 200, (0.4, 0.4, 0.4))

    # Draw central sun
    draw_planet(0, 0, 20, (1.0, 1.0, 0.0))

    # Planet 1
    x1 = 100 * math.cos(math.radians(angle))
    y1 = 100 * math.sin(math.radians(angle))
    draw_planet(x1, y1, 10, (0.0, 0.0, 1.0))

    # Planet 2 (slower orbit)
    x2 = 200 * math.cos(math.radians(angle / 2))
    y2 = 200 * math.sin(math.radians(angle / 2))
    draw_planet(x2, y2, 15, (1.0, 0.0, 0.0))

    angle += 0.5
    glutSwapBuffers()

def timer(v):
    glutPostRedisplay()
    glutTimerFunc(33, timer, 1)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"OpenGL Orbiting Planets - Midpoint Circle Algorithm")
    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_PROJECTION)
    gluOrtho2D(-400, 400, -300, 300)
    glutDisplayFunc(display)
    glutTimerFunc(33, timer, 1)
    glutMainLoop()

if __name__ == "__main__":
    main()

