"""
Advanced Traffic Roundabout Simulation with Intelligent Car Path Planning and Traffic Lights
NOW WITH 4 SWITCHABLE SCENES!

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
NUM_CARS = 25  
MIN_RADIUS = 100 
MAX_RADIUS = 300 
CAR_WIDTH = 6
CAR_LENGTH = 12
CAR_SPEED = 1.5  # degrees per frame
SHOW_INSTRUCTIONS = True
USE_MPCA = True
TRAFFIC_LIGHT_INTERVAL = 200  # frames per light change
NUM_LANES = 5 

# ------------------------ State (MODIFIED) ------------------------
cars = []
frame_counter = 0
traffic_light_state = 0  
current_scene = 1 # 1=Simulation, 2=MPCA Visualizer, 3=Control Panel, 4=Metrics
MAX_SCENES = 4

# ------------------------ SCENE MANAGEMENT FUNCTIONS (NEW) ------------------------

def switch_scene():
    """Cycles the current_scene state variable."""
    global current_scene
    current_scene = (current_scene % MAX_SCENES) + 1
    glutPostRedisplay()

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
    max_lane_radius = MAX_RADIUS - CAR_WIDTH/2
    min_lane_radius = MIN_RADIUS + CAR_WIDTH/2
    
    for _ in range(num):
        lane_radius = random.uniform(min_lane_radius, max_lane_radius)
        angle = random.uniform(0, 360)
        speed = CAR_SPEED * random.uniform(0.8, 1.2)
        cars.append(Car(lane_radius, angle, speed))

# ---------------- Draw Roundabout ------------------
def draw_roundabout():
    lane_width = (MAX_RADIUS - MIN_RADIUS)/NUM_LANES
    for i in range(NUM_LANES):
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

# ---------------- Draw Cars ------------------
def draw_cars():
    glLineWidth(1.0) 
    
    for car in cars:
        x, y = car.position()
        car_rotation_angle = car.angle - 90 
        
        glPushMatrix()
        glTranslatef(x, y, 0)
        glRotatef(car_rotation_angle, 0, 0, 1)
        
        # Car Body
        glColor3f(*car.color)
        glBegin(GL_QUADS)
        glVertex2f(-CAR_LENGTH/2, -CAR_WIDTH/2)
        glVertex2f( CAR_LENGTH/2, -CAR_WIDTH/2)
        glVertex2f( CAR_LENGTH/2,  CAR_WIDTH/2)
        glVertex2f(-CAR_LENGTH/2,  CAR_WIDTH/2)
        glEnd()
        
        # Headlight
        glColor3f(1.0, 1.0, 0.0) 
        glBegin(GL_QUADS)
        glVertex2f(CAR_LENGTH/2 - 2, -CAR_WIDTH/2)
        glVertex2f(CAR_LENGTH/2, -CAR_WIDTH/2)
        glVertex2f(CAR_LENGTH/2,  CAR_WIDTH/2)
        glVertex2f(CAR_LENGTH/2 - 2, CAR_WIDTH/2)
        glEnd()
        
        glPopMatrix()

# ---------------- Traffic Lights ------------------
def draw_traffic_lights():
    global traffic_light_state
    xc, yc = WIDTH/2, HEIGHT/2
    entry_radius = MIN_RADIUS - 30
    light_radius = 10
    colors = [(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (1.0, 0.0, 0.0)] 
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
    # The fix is ensuring x and y are integers before calling glRasterPos2i
    # The coordinates should already be ints when called, but we'll ensure it here too, 
    # and require integer inputs at the call site.
    glRasterPos2i(int(x), int(y)) 
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

# --- SCENE 1: Primary Simulation ---
def draw_simulation_scene():
    """The main running traffic simulation."""
    # Car movement update is only needed in the active simulation scene
    for car in cars:
        car.update()
        
    draw_roundabout()
    draw_cars()
    draw_traffic_lights()
    
    # Display scene info
    glColor3f(1.0, 1.0, 1.0)
    draw_text(WIDTH - 150, HEIGHT - 20, "Scene 1: Simulation")


# --- SCENE 2: MPCA Visualizer (NEW) ---
def draw_mpca_scene():
    """Demonstrates the Mid-Point Circle Algorithm drawing multiple circles."""
    xc, yc = WIDTH/2, HEIGHT/2
    glPointSize(1)
    
    glColor3f(1.0, 1.0, 1.0)
    draw_text(WIDTH - 250, HEIGHT - 20, "Scene 2: MPCA Visualization")
    draw_text(10, 50, "Showing multiple circles rendered via Mid-Point Circle Algorithm.")
    
    # Draw several MPCA circles
    for r in range(50, 350, 50):
        color = (r/400.0, 1.0 - r/400.0, 0.5, 0.5) 
        draw_circle_mpca(xc, yc, r, color)


# --- SCENE 3: Traffic Light Control Panel (NEW) ---
def draw_control_panel():
    """A static scene showing current traffic control status."""
    global traffic_light_state
    
    # Background
    glColor4f(0.05, 0.05, 0.1, 1.0) 
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(WIDTH, 0); glVertex2f(WIDTH, HEIGHT); glVertex2f(0, HEIGHT)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    draw_text(WIDTH - 250, HEIGHT - 20, "Scene 3: Control Panel")
    
    # FIX APPLIED HERE: Cast float divisions to int
    draw_text(int(WIDTH/2 - 100), int(HEIGHT/2 + 100), "Current Light State:")
    
    # Display light status
    colors = [(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (1.0, 0.0, 0.0)] 
    statuses = ["GREEN (Flowing)", "YELLOW (Warning)", "RED (Stopped)"]
    
    glColor3f(*colors[traffic_light_state])
    # FIX APPLIED HERE: Cast float divisions to int
    draw_text(int(WIDTH/2 - 100), int(HEIGHT/2 + 50), statuses[traffic_light_state], GLUT_BITMAP_HELVETICA_18)
    
    glColor3f(1.0, 1.0, 1.0)
    draw_text(10, 20, "Press 'T' to cycle scenes. Light state changes automatically in Scene 1.")


# --- SCENE 4: Metrics View (NEW) ---
def draw_metrics_scene():
    """A scene displaying simulation configuration and metrics."""
    # Background
    glColor4f(0.05, 0.05, 0.1, 1.0)
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(WIDTH, 0); glVertex2f(WIDTH, HEIGHT); glVertex2f(0, HEIGHT)
    glEnd()
    
    # Display Info
    glColor3f(1.0, 1.0, 1.0)
    draw_text(WIDTH - 250, HEIGHT - 20, "Scene 4: Metrics View")
    
    y_pos = int(HEIGHT/2 + 50) # FIX APPLIED HERE: Cast to int
    # FIX APPLIED HERE: Cast float divisions to int
    draw_text(int(WIDTH/2 - 150), y_pos, f"Total Current Cars: {NUM_CARS}")
    y_pos -= 30
    draw_text(int(WIDTH/2 - 150), y_pos, f"Base Car Speed: {CAR_SPEED:.1f} degrees/frame")
    y_pos -= 30
    draw_text(int(WIDTH/2 - 150), y_pos, f"Number of Lanes: {NUM_LANES}")
    y_pos -= 30
    draw_text(int(WIDTH/2 - 150), y_pos, f"Roundabout Radius: {MIN_RADIUS} to {MAX_RADIUS}")
    
    glColor3f(0.7, 0.7, 0.7)
    draw_text(10, 20, "Configuration metrics are displayed here.")


# ---------------- Display (MODIFIED) ------------------
def display():
    global frame_counter, traffic_light_state, current_scene
    
    # Only update traffic light and run car logic in the active simulation scene
    if current_scene == 1:
        frame_counter += 1
        if frame_counter % TRAFFIC_LIGHT_INTERVAL == 0:
            traffic_light_state = (traffic_light_state + 1) % 3

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # --- Scene Switching Logic ---
    if current_scene == 1:
        draw_simulation_scene()
    elif current_scene == 2:
        draw_mpca_scene()
    elif current_scene == 3:
        draw_control_panel()
    elif current_scene == 4:
        draw_metrics_scene()

    # Instructions are visible regardless of the scene
    if SHOW_INSTRUCTIONS:
        glColor3f(1.0, 1.0, 1.0)
        lines = [
            f"Scene: {current_scene}/4 (Press 'T' to switch)",
            f"Traffic Density: {NUM_CARS} cars (use '+' / '-' to change)",
            f"Car Speed: {CAR_SPEED:.1f} degrees/frame (use S/s to change)",
            "I toggle instructions, Q/Esc quit"
        ]
        y = 40
        for ln in lines:
            # draw_text calls use integer coordinates (10, y) so no change needed here
            draw_text(10, y, ln) 
            y += 16

    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)

# ---------------- Keyboard (MODIFIED) ------------------
def keyboard(key, x, y):
    global NUM_CARS, CAR_SPEED, SHOW_INSTRUCTIONS
    k = key.decode('utf-8') if isinstance(key, bytes) else key
    
    if k in ('t', 'T'): 
        switch_scene() # Key to switch between the 4 scenes
    
    # Only allow controls in the simulation scene (Scene 1)
    if current_scene == 1:
        if k == '+': NUM_CARS += 1; generate_cars(NUM_CARS)
        elif k == '-': NUM_CARS = max(1, NUM_CARS - 1); generate_cars(NUM_CARS)
        elif k in ('s', 'S'):
            if k == 's': CAR_SPEED = max(0.1, CAR_SPEED - 0.2)
            else: CAR_SPEED += 0.2
            for car in cars: car.speed = CAR_SPEED * random.uniform(0.8, 1.2)
        
    if k in ('i', 'I'): SHOW_INSTRUCTIONS = not SHOW_INSTRUCTIONS
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
    
    screen_width = glutGet(GLUT_SCREEN_WIDTH)
    screen_height = glutGet(GLUT_SCREEN_HEIGHT)
    window_x = (screen_width - WIDTH) // 2
    window_y = (screen_height - HEIGHT) // 2
    
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(window_x, window_y)
    
    glutCreateWindow(b"Advanced Traffic Roundabout Simulation with 4 Scenes")

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