"""
heart_pulse_animation_autonomous.py - CORRECTED

IT IS ONLY SHOWING white screen fix.
Most likely causes: PyOpenGL/GLUT setup issue or window creation failure.
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import sys # Import sys for potential exit handling

# ---------------- Configuration ----------------
WIDTH, HEIGHT = 800, 600
pulse_phase = 0.0
pulse_speed = 0.15 
last_time = time.time()

# Heart points for shape (Cardioid formula)
heart_points = []
for angle in range(0, 360, 2):
    rad = math.radians(angle)
    # Parametric heart curve equations
    x = 16 * math.sin(rad)**3
    y = 13*math.cos(rad) - 5*math.cos(2*rad) - 2*math.cos(3*rad) - math.cos(4*rad)
    # Scale coordinates for the window view
    heart_points.append( (x*20, y*20) )

# ---------------- Draw Helpers ----------------
def draw_heart_outline():
    """Draws the black outline of the heart shape."""
    glColor3f(0.0,0.0,0.0)
    glBegin(GL_LINE_LOOP)
    for x, y in heart_points:
        glVertex2f(x, y)
    glEnd()

def draw_pulse():
    """Draws the red pulsating effect simulating the blood flow/pressure wave."""
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
    # Set the background to white
    # glClearColor(1.0,1.0,1.0,1.0)
    # glClear(GL_COLOR_BUFFER_BIT)
    # glLoadIdentity()
    # In the display() function:
    glClearColor(0.0, 0.0, 0.5, 1.0) # <--- Change to Blue
    glClear(GL_COLOR_BUFFER_BIT)

    # --- Update Animation Logic ---
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    # Update the phase for continuous running
    # Added a simple check for dt to prevent massive jumps if the program pauses for a long time
    if dt < 1.0: 
        pulse_phase += pulse_speed * dt * 60

    # --- Draw Elements ---
    draw_heart_outline()
    draw_pulse()
    
    glutSwapBuffers()

# ---------------- Timer ----------------
def timer(value):
    """
    Called by GLUT's timer function to request a display update.
    """
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)

# ---------------- Main ----------------
def main():
    """Initializes GLUT, sets up the window and the main loop."""
    try:
        # 1. Initialize GLUT
        glutInit(sys.argv)
    except:
        # This catch block is for systems where GLUT initialization fails early
        print("ERROR: GLUT failed to initialize.")
        print("Please ensure your system has GLUT installed (e.g., freeglut on Linux/Windows, or check XQuartz on macOS).")
        return
        
    try:
        # 2. Configure and Create Window
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(WIDTH, HEIGHT)
        glutCreateWindow(b"Autonomous Heart Beat Simulation")
        
        # 3. Setup 2D Projection
        gluOrtho2D(-WIDTH/2, WIDTH/2, -HEIGHT/2, HEIGHT/2)

        # 4. Register Callbacks
        glutDisplayFunc(display)
        glutTimerFunc(33, timer, 0)

        # 5. Start Loop
        print("INFO: OpenGL/GLUT window opened. Simulation should be visible.")
        glutMainLoop()

    except Exception as e:
        print(f"An unexpected error occurred during rendering: {e}")
        print("This often indicates a problem with the OpenGL driver or context.")
        
if __name__ == '__main__':
    main()