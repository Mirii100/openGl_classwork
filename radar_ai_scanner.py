from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, numpy as np

WIDTH, HEIGHT = 800, 800
SWEEP_SPEED = 2.0  # degrees per frame
angle = 0

RADIUS_LIMIT = 300
MAX_TARGETS = 20
targets = []

# ========== KALMAN FILTER CLASS ==========
class KalmanFilter2D:
    def __init__(self, x, y):
        # State: [x, y, vx, vy]
        self.state = np.array([[x], [y], [0], [0]], dtype=float)
        self.P = np.eye(4) * 500
        self.F = np.array([[1, 0, 1, 0],
                           [0, 1, 0, 1],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])
        self.H = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]])
        self.R = np.eye(2) * 25
        self.Q = np.eye(4) * 0.1

    def predict(self):
        self.state = np.dot(self.F, self.state)
        self.P = np.dot(self.F, np.dot(self.P, self.F.T)) + self.Q
        return self.state[0, 0], self.state[1, 0]

    def update(self, x, y):
        Z = np.array([[x], [y]])
        Y = Z - np.dot(self.H, self.state)
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R
        K = np.dot(self.P, np.dot(self.H.T, np.linalg.inv(S)))
        self.state = self.state + np.dot(K, Y)
        I = np.eye(self.F.shape[0])
        self.P = np.dot((I - np.dot(K, self.H)), self.P)

# ========== MIDPOINT CIRCLE ALGORITHM ==========
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

# ========== TARGET SYSTEM ==========
class Target:
    def __init__(self, x, y, intensity):
        self.kf = KalmanFilter2D(x, y)
        self.intensity = intensity
        self.life = 0

    def update(self):
        x_pred, y_pred = self.kf.predict()
        # Random "noise" in real detection
        x_meas = x_pred + random.uniform(-5, 5)
        y_meas = y_pred + random.uniform(-5, 5)
        self.kf.update(x_meas, y_meas)
        self.life += 1
        return self.kf.state[0, 0], self.kf.state[1, 0]

def generate_targets():
    global targets
    targets = []
    for _ in range(random.randint(8, MAX_TARGETS)):
        r = random.uniform(30, RADIUS_LIMIT)
        theta = random.uniform(0, 2 * math.pi)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        intensity = random.uniform(0.6, 1.0)
        targets.append(Target(x, y, intensity))

# ========== DRAWING SYSTEM ==========
def draw_radar_beam(angle):
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for a in range(int(angle - 2), int(angle + 2)):
        x = RADIUS_LIMIT * math.cos(math.radians(a))
        y = RADIUS_LIMIT * math.sin(math.radians(a))
        glVertex2f(x, y)
    glEnd()

def draw_targets():
    glPointSize(5)
    glBegin(GL_POINTS)
    for t in targets:
        x, y = t.update()
        # AI filtering: only show persistent, high-intensity detections
        if t.life > 5 and t.intensity > 0.7:
            glColor3f(0.0, 1.0, 0.0)
            glVertex2f(x, y)
    glEnd()

# ========== DISPLAY ==========
def display():
    global angle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # Draw radar rings
    for r in range(50, RADIUS_LIMIT + 1, 50):
        draw_circle(0, 0, r, (0.0, 0.3, 0.0))

    # Draw rotating beam
    draw_radar_beam(angle)

    # Draw AI-filtered targets
    draw_targets()

    glutSwapBuffers()
    angle = (angle + SWEEP_SPEED) % 360

def timer(value):
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)

# ========== MAIN ==========
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"AI Radar Scanner Simulation - Kalman Filtering")
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(-400, 400, -400, 400)
    generate_targets()
    glutDisplayFunc(display)
    glutTimerFunc(33, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
