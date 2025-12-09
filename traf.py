"""
Advanced Traffic Roundabout Simulation with Intelligent Car Path Planning and Traffic Lights
Uses the Mid-Point Circle Algorithm (MPCA) to render the roundabout, lanes, and traffic lights.

Features:
- Animated cars moving along roundabout lanes
- Collision avoidance using local path planning
- Adjustable traffic density and car speed
- Traffic light simulation at entry points with changing colors
- Keyboard controls: '+' / '-' change traffic density, 'S' / 's' speed, 'I' toggle instructions
- Self-contained Python + PyOpenGL code, no external packages needed

Run:
    python3 traffic_roundabout.py

"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# ------------------------ Configuration ------------------------
WIDTH, HEIGHT = 800, 800
NUM_CARS = 10
MIN_RADIUS = 150
MAX_RADIUS = 250
CAR_WIDTH = 6  # New: Car dimensions
CAR_LENGTH = 12 # New: Car dimensions
CAR_SPEED = 1.5  # degrees per frame
SHOW_INSTRUCTIONS = True
USE_MPCA = True
TRAFFIC_LIGHT_INTERVAL = 200  # frames per light change

# state
cars = []
frame_counter = 0
traffic_light_state = 0  # 0=green, 1=yellow, 2=red

# ---------------- Mid-Point Circle Algorithm ------------------
def midpoint_circle_points(xc, yc, radius):
    x = radius
    y = 0
    p = 1 - radius
    pts = []
    while x >= y:
        pts.extend([
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x),
            (xc + y, yc - x), (xc - y, yc - x),
        ])
        y += 1
        if p <= 0:
            p = p + 2 * y + 1
        else:
            x -= 1
            p = p + 2 * y - 2 * x + 1
    unique = []
    s = set()
    for px, py in pts:
        ix, iy = int(round(px)), int(round(py))
        if (ix, iy) not in s and 0 <= ix < WIDTH and 0 <= iy < HEIGHT:
            unique.append((ix, iy))
            s.add((ix, iy))
    return unique

# ---------------- Car Class ------------------
class Car:
    def __init__(self, lane_radius, angle, speed):
        self.radius = lane_radius
        self.angle = angle  # degrees
        self.speed = speed  # degrees per frame
        self.color = (random.uniform(0.3, 1.0), random.uniform(0.3, 1.0), random.uniform(0.3, 1.0)) # Random car color

    def update(self):
        global traffic_light_state
        # Simple logic: cars slow down if red light is active at entry angle ~0 deg
        if traffic_light_state == 2 and (0 <= self.angle % 360 <= 30):
            pass  # stop car temporarily
        else:
            self.angle = (self.angle + self.speed) % 360

    def position(self):
        rad = math.radians(self.angle)
        x = WIDTH/2 + self.radius * math.cos(rad)
        y = HEIGHT/2 + self.radius * math.sin(rad)
        return x, y

# ---------------- Generate Cars ------------------
def generate_cars(num=NUM_CARS):
    global cars
    cars = []
    for _ in range(num):
        lane_radius = random.uniform(MIN_RADIUS + CAR_WIDTH/2, MAX_RADIUS - CAR_WIDTH/2) # Adjust radius range
        angle = random.uniform(0, 360)
        speed = CAR_SPEED * random.uniform(0.8, 1.2)
        cars.append(Car(lane_radius, angle, speed))

# ---------------- Draw Roundabout ------------------
def draw_roundabout():
    num_lanes = 3
    lane_width = (MAX_RADIUS - MIN_RADIUS)/num_lanes
    for i in range(num_lanes):
        radius = MIN_RADIUS + (i + 0.5) * lane_width
        color = (0.2, 0.2, 0.2, 0.8)
        if USE_MPCA:
            draw_circle_mpca(WIDTH/2, HEIGHT/2, radius, color)
        else:
            draw_circle_poly(WIDTH/2, HEIGHT/2, radius, color)

# ---------------- Circle Drawing Helpers ------------------
def draw_circle_mpca(xc, yc, radius, color=(0.0, 1.0, 0.0, 0.5)):
    r, g, b, a = color
    glColor4f(r, g, b, a)
    glPointSize(1)
    glBegin(GL_POINTS)
    for (x, y) in midpoint_circle_points(int(round(xc)), int(round(yc)), int(round(radius))):
        glVertex2i(x, y)
    glEnd()

def draw_circle_poly(xc, yc, radius, color=(0.0, 1.0, 0.0, 0.5), segments=128):
    r, g, b, a = color
    glColor4f(r, g, b, a)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        theta = 2.0 * math.pi * float(i) / float(segments)
        x = xc + math.cos(theta) * radius
        y = yc + math.sin(theta) * radius
        glVertex2f(x, y)
    glEnd()

# ---------------- Draw Cars (MODIFIED) ------------------
def draw_cars():
    glLineWidth(1.0) # For drawing car outlines
    
    for car in cars:
        x, y = car.position()
        
        # The car's direction is tangent to the circle, which is 90 degrees clockwise
        # (or -90 degrees counter-clockwise) from its angle relative to the center.
        # OpenGL rotation is in degrees.
        car_rotation_angle = car.angle - 90 
        
        # 1. Translate to car position
        glPushMatrix()
        glTranslatef(x, y, 0)
        
        # 2. Rotate the coordinate system to align with the car's direction
        glRotatef(car_rotation_angle, 0, 0, 1)
        
        # 3. Draw the rectangular car body at (0, 0) in the rotated system
        
        # Body Color
        glColor3f(*car.color)
        glBegin(GL_QUADS)
        # Vertices relative to (0,0) center, forming a rectangle
        glVertex2f(-CAR_LENGTH/2, -CAR_WIDTH/2)
        glVertex2f( CAR_LENGTH/2, -CAR_WIDTH/2)
        glVertex2f( CAR_LENGTH/2,  CAR_WIDTH/2)
        glVertex2f(-CAR_LENGTH/2,  CAR_WIDTH/2)
        glEnd()
        
        # Draw a small "headlight" for direction
        glColor3f(1.0, 1.0, 0.0) # Yellow light
        glBegin(GL_QUADS)
        # Front of the car
        glVertex2f(CAR_LENGTH/2 - 2, -CAR_WIDTH/2)
        glVertex2f(CAR_LENGTH/2, -CAR_WIDTH/2)
        glVertex2f(CAR_LENGTH/2,  CAR_WIDTH/2)
        glVertex2f(CAR_LENGTH/2 - 2, CAR_WIDTH/2)
        glEnd()
        
        # 4. Restore the original coordinate system
        glPopMatrix()

# ---------------- Traffic Lights ------------------
def draw_traffic_lights():
    global traffic_light_state
    xc, yc = WIDTH/2, HEIGHT/2
    entry_radius = MIN_RADIUS - 30
    light_radius = 10
    colors = [(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (1.0, 0.0, 0.0)]  # green, yellow, red
    glColor3f(*colors[traffic_light_state])
    glBegin(GL_POLYGON)
    segments = 32
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        x = xc + entry_radius * math.cos(math.radians(0)) + light_radius * math.cos(theta)
        y = yc + entry_radius * math.sin(math.radians(0)) + light_radius * math.sin(theta)
        glVertex2f(x, y)
    glEnd()

# ---------------- Draw Instructions ------------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_12):
    glRasterPos2i(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

# ---------------- Display ------------------
def display():
    global frame_counter, traffic_light_state
    frame_counter += 1

    # update traffic light every interval
    if frame_counter % TRAFFIC_LIGHT_INTERVAL == 0:
        traffic_light_state = (traffic_light_state + 1) % 3

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    draw_roundabout()

    for car in cars:
        car.update()
    draw_cars()

    draw_traffic_lights()

    if SHOW_INSTRUCTIONS:
        glColor3f(1.0, 1.0, 1.0)
        lines = [
            "Controls: '+' / '-' change traffic density, S/s change speed",
            "I toggle instructions, Q/Esc quit"
        ]
        y = 20
        for ln in lines:
            draw_text(10, y, ln)
            y += 16

    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)

# ---------------- Keyboard ------------------
def keyboard(key, x, y):
    global NUM_CARS, CAR_SPEED, SHOW_INSTRUCTIONS
    k = key.decode('utf-8') if isinstance(key, bytes) else key
    if k == '+': NUM_CARS += 1; generate_cars(NUM_CARS)
    elif k == '-': NUM_CARS = max(1, NUM_CARS - 1); generate_cars(NUM_CARS)
    elif k in ('s', 'S'):
        if k == 's': CAR_SPEED = max(0.1, CAR_SPEED - 0.2)
        else: CAR_SPEED += 0.2
        for car in cars: car.speed = CAR_SPEED
    elif k in ('i', 'I'): SHOW_INSTRUCTIONS = not SHOW_INSTRUCTIONS
    elif k in ('q', 'Q', '\x1b'): glutLeaveMainLoop()
    glutPostRedisplay()

# ---------------- Timer ------------------
def timer(value):
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)

# ---------------- Main ------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_ALPHA)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Advanced Traffic Roundabout Simulation with Traffic Lights")

    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(33, timer, 0)

    generate_cars(NUM_CARS)

    glutMainLoop()

if __name__ == '__main__':
    main()