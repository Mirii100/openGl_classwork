from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, time

# Window parameters
WIDTH, HEIGHT = 800, 800
SWEEP_SPEED = 1.5  # degrees per frame
angle = 0
targets = []

# Parameters for target generation
MAX_TARGETS = 20
RADIUS_LIMIT = 300

# --- Midpoint Circle Algorithm ---
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

def draw_circle(x_center, y_center, radius, color=(0.0, 0.8, 0.0)):
    glColor3f(*color)
    glBegin(GL_POINTS)
    for (x, y) in midpoint_circle_points(x_center, y_center, radius):
        glVertex2f(x, y)
    glEnd()

# --- Random Targets ---
def generate_targets():
    global targets
    targets = []
    for _ in range(random.randint(10, MAX_TARGETS)):
        r = random.uniform(30, RADIUS_LIMIT)
        theta = random.uniform(0, 2 * math.pi)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        intensity = random.random()
        targets.append((x, y, intensity))

# --- Radar Sweep Beam ---
def draw_radar_beam(angle):
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for a in range(int(angle - 2), int(angle + 2)):
        x = RADIUS_LIMIT * math.cos(math.radians(a))
        y = RADIUS_LIMIT * math.sin(math.radians(a))
        glVertex2f(x, y)
    glEnd()

# --- Target Dots ---
def draw_targets():
    glPointSize(5)
    glBegin(GL_POINTS)
    for (x, y, intensity) in targets:
        if random.random() < intensity * 0.7:  # simulate noise detection
            glColor3f(0.0, 1.0, 0.0)
            glVertex2f(x, y)
    glEnd()

# --- Display Function ---
def display():
    global angle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # Draw Radar Circles
    for r in range(50, RADIUS_LIMIT + 1, 50):
        draw_circle(0, 0, r, (0.0, 0.4, 0.0))

    # Draw Beam
    draw_radar_beam(angle)

    # Draw Targets
    draw_targets()

    glutSwapBuffers()
    angle = (angle + SWEEP_SPEED) % 360

def timer(value):
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Radar Scanner Simulation - Midpoint Circle Algorithm")
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(-400, 400, -400, 400)
    generate_targets()
    glutDisplayFunc(display)
    glutTimerFunc(33, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
