"""
football_accuracy_radar.py

Smart Sport Analysis System - Football Free-Kick Accuracy Radar
Uses Mid-Point Circle Algorithm (MPCA) for rendering goal, ball trajectories, and radar.

Features:
- Football goal visualized
- Player avatars as simple shapes (triangles / rectangles)
- Animated ball trajectory for free-kicks
- Accuracy radar showing hit/miss positions
- Multiple shot simulation
- Keyboard controls: Space=kick ball, R=reset, I=toggle instructions
- Self-contained Python + PyOpenGL code

Run:
    python3 football_accuracy_radar.py

"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# ---------------- Configuration ----------------
WIDTH, HEIGHT = 900, 600
BALL_RADIUS = 8
GOAL_WIDTH = 200
GOAL_HEIGHT = 100
PLAYER_SIZE = 12
SHOW_INSTRUCTIONS = True
MAX_SHOTS = 10
BALL_SPEED = 5.0  # pixels per frame

# state
ball_pos = [WIDTH/2, 100]
ball_target = [WIDTH/2, HEIGHT - GOAL_HEIGHT]
ball_in_motion = False
shots = []  # stores (x, y) positions of ball hits
frame_counter = 0

# ---------------- Mid-Point Circle Algorithm ----------------
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

# ---------------- Draw Helpers ----------------
def draw_circle_mpca(xc, yc, radius, color=(0.0, 1.0, 0.0, 0.5)):
    r, g, b, a = color
    glColor4f(r, g, b, a)
    glBegin(GL_POINTS)
    for (x, y) in midpoint_circle_points(int(round(xc)), int(round(yc)), int(round(radius))):
        glVertex2i(x, y)
    glEnd()

def draw_rectangle(xc, yc, width, height, color=(0.0, 0.0, 1.0)):
    r, g, b = color
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(xc - width/2, yc)
    glVertex2f(xc + width/2, yc)
    glVertex2f(xc + width/2, yc + height)
    glVertex2f(xc - width/2, yc + height)
    glEnd()

# ---------------- Draw Players ----------------
def draw_player(x, y, color=(1.0, 0.0, 0.0)):
    glColor3f(*color)
    glBegin(GL_TRIANGLES)
    size = PLAYER_SIZE
    glVertex2f(x, y)
    glVertex2f(x - size/2, y - size)
    glVertex2f(x + size/2, y - size)
    glEnd()

# ---------------- Draw Goal ----------------
def draw_goal():
    glColor3f(1.0, 1.0, 1.0)
    draw_rectangle(WIDTH/2, HEIGHT - GOAL_HEIGHT, GOAL_WIDTH, GOAL_HEIGHT)

# ---------------- Draw Ball ----------------
def draw_ball():
    glColor3f(1.0, 1.0, 0.0)
    draw_circle_mpca(ball_pos[0], ball_pos[1], BALL_RADIUS, (1.0, 1.0, 0.0, 1.0))

# ---------------- Draw Radar ----------------
def draw_radar():
    for shot in shots:
        draw_circle_mpca(shot[0], shot[1], 5, (0.0, 1.0, 0.0, 0.7))

# ---------------- Update Ball ----------------
def update_ball():
    global ball_pos, ball_in_motion, shots
    if ball_in_motion:
        dx = ball_target[0] - ball_pos[0]
        dy = ball_target[1] - ball_pos[1]
        dist = math.hypot(dx, dy)
        if dist < BALL_SPEED:
            ball_pos = list(ball_target)
            ball_in_motion = False
            shots.append(list(ball_pos))
            if len(shots) > MAX_SHOTS:
                shots.pop(0)
        else:
            ball_pos[0] += BALL_SPEED * dx / dist
            ball_pos[1] += BALL_SPEED * dy / dist

# ---------------- Draw Instructions ----------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_12):
    glRasterPos2i(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

# ---------------- Display ----------------
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    draw_goal()
    draw_radar()
    draw_ball()

    # Draw players at goal line
    draw_player(WIDTH/2 - GOAL_WIDTH/4, HEIGHT - GOAL_HEIGHT, (1.0,0.0,0.0))
    draw_player(WIDTH/2 + GOAL_WIDTH/4, HEIGHT - GOAL_HEIGHT, (0.0,0.0,1.0))

    update_ball()

    if SHOW_INSTRUCTIONS:
        glColor3f(1.0, 1.0, 1.0)
        lines = [
            "Space: Kick ball",
            "R: Reset shots",
            "I: Toggle instructions",
            "Multiple shots will show radar hits"
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

# ---------------- Keyboard ----------------
def keyboard(key, x, y):
    global ball_in_motion, ball_pos, shots, SHOW_INSTRUCTIONS
    k = key.decode('utf-8') if isinstance(key, bytes) else key
    if k == ' ':
        if not ball_in_motion:
            ball_pos = [WIDTH/2, 100]
            ball_in_motion = True
    elif k in ('r', 'R'):
        shots.clear()
        ball_pos = [WIDTH/2, 100]
        ball_in_motion = False
    elif k in ('i','I'):
        SHOW_INSTRUCTIONS = not SHOW_INSTRUCTIONS
    elif k in ('q','Q','\x1b'):
        glutLeaveMainLoop()

    glutPostRedisplay()

# ---------------- Timer ----------------
def timer(value):
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)

# ---------------- Main ----------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_ALPHA)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Football Free-Kick Accuracy Radar")

    glClearColor(0.1, 0.4, 0.1, 1.0)

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(33, timer, 0)

    glutMainLoop()

if __name__ == '__main__':
    main()