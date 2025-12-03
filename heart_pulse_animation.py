"""
heart_pulse_animation_hardened.py - FINAL VISIBILITY FIX

This version explicitly resets the projection and model-view matrices 
in the display function to prevent drawing outside the visible area.
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import sys

# ---------------- Configuration ----------------
WIDTH, HEIGHT = 800, 600
pulse_phase = 0.0
pulse_speed = 0.15 
last_time = time.time()
BLOOD_FLOW_RADIUS = 30
BLOOD_FLOW_AMPLITUDE = 15

# Heart points for shape (Cardioid formula)
heart_points = []
for angle in range(0, 360, 2):
    rad = math.radians(angle)
    x = 16 * math.sin(rad)**3
    y = 13*math.cos(rad) - 5*math.cos(2*rad) - 2*math.cos(3*rad) - math.cos(4*rad)
    heart_points.append( (x*20, y*20) ) # Scale coordinates (approx -320 to 260)

# ---------------- MCA Helper Function ----------------
# (Unchanged from previous successful version)
def draw_circle_points(xc, yc, x, y):
    """Draws points in all 8 octants of the circle."""
    glVertex2f(xc + x, yc + y)
    glVertex2f(xc - x, yc + y)
    glVertex2f(xc + x, yc - y)
    glVertex2f(xc - x, yc - y)
    glVertex2f(xc + y, yc + x)
    glVertex2f(xc - y, yc + x)
    glVertex2f(xc + y, yc - x)
    glVertex2f(xc - y, yc - x)

def draw_blood_flow_mca(xc, yc, R):
    """Implements the Midpoint Circle Algorithm to draw a circle outline."""
    glColor3f(0.0, 1.0, 0.0) # Green color for blood flow
    glPointSize(2)
    glBegin(GL_POINTS)
    
    x = 0
    y = R
    p = 1 - R  # Initial decision parameter

    draw_circle_points(xc, yc, x, y)
    
    while x < y:
        x += 1
        if p < 0:
            p = p + 2 * x + 1
        else:
            y -= 1
            p = p + 2 * x + 1 - 2 * y

        draw_circle_points(xc, yc, x, y)

    glEnd()

# ---------------- Draw Helpers ----------------
def draw_heart_outline():
    """Draws the black outline of the heart shape."""
    glColor3f(0.0,0.0,0.0)
    glBegin(GL_LINE_LOOP)
    for x, y in heart_points:
        glVertex2f(x, y)
    glEnd()

def draw_pulse():
    """Draws the red pulsating effect (pressure wave)."""
    glColor3f(1.0,0.0,0.0)
    glPointSize(4)
    glBegin(GL_POINTS)
    for i, (x, y) in enumerate(heart_points):
        phase = (i/len(heart_points))*2*math.pi + pulse_phase
        offset = 2 * math.sin(phase)
        glVertex2f(x + offset, y + offset)
    glEnd()

# ---------------- Display ----------------
def display():
    """The main drawing function, called repeatedly."""
    global pulse_phase, last_time
    
    # --- 1. Clear Screen and Setup View ---
    # Set background to white
    glClearColor(1.0, 1.0, 1.0, 1.0) 
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Always reset the modelview matrix before drawing to ensure no cumulative transformations
    glLoadIdentity()

    # --- 2. Update Animation Logic ---
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    if dt < 1.0: 
        pulse_phase += pulse_speed * dt * 60

    # --- 3. Calculate Animated Radius ---
    animated_radius = BLOOD_FLOW_RADIUS + BLOOD_FLOW_AMPLITUDE * (0.5 + 0.5 * math.sin(pulse_phase * 0.5))
    
    # --- 4. Draw Elements ---
    draw_heart_outline()
    draw_pulse()
    draw_blood_flow_mca(0, 0, int(animated_radius))
    
    # --- 5. Swap Buffers ---
    glutSwapBuffers()

# ---------------- Timer ----------------
def timer(value):
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)

# ---------------- Main ----------------
def main():
    """Initializes GLUT, sets up the window and the main loop."""
    try:
        glutInit(sys.argv)
    except:
        print("ERROR: GLUT failed to initialize. Check PyOpenGL/FreeGLUT installation.")
        return
        
    try:
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(WIDTH, HEIGHT)
        glutCreateWindow(b"Autonomous Heart Beat & MCA Blood Flow")
        
        # --- Explicit Projection Setup (Crucial for Visibility) ---
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Define the view volume (centered at 0,0)
        gluOrtho2D(-WIDTH/2, WIDTH/2, -HEIGHT/2, HEIGHT/2)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # ----------------------------------------------------------

        glutDisplayFunc(display)
        glutTimerFunc(33, timer, 0)

        print("INFO: OpenGL/GLUT window opened. Simulation should be visible.")
        glutMainLoop()

    except Exception as e:
        print(f"An unexpected error occurred during rendering: {e}")
        
if __name__ == '__main__':
    main()