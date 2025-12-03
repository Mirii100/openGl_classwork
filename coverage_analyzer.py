"""
coverage_analyzer.py

Interactive Cellular Coverage Analyzer (Python + PyOpenGL)
Uses the Mid-Point Circle Algorithm (MPCA) for rendering all circular visuals.

Features:
- Multiple Access Points (APs) with radius visualized using MPCA
- Real-screen coordinates (0..WIDTH, 0..HEIGHT)
- Simple channel assignment heuristic to reduce interference
- Toggleable interference heatmap (alpha-blended concentric circles)
- Keyboard controls: Space=regen APs, +/- = change AP count, H=toggle heatmap, M=toggle MPCA/poly, I=toggle instructions
- Fake resource usage bar for visual effect (no external packages)

Dependencies:
- Python 3.8+
- PyOpenGL

Run:
    python3 coverage_analyzer.py

"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import numpy as np

# ------------------------ Configuration ------------------------
WIDTH, HEIGHT = 900, 700
AP_COUNT = 10
MIN_RADIUS = 60
MAX_RADIUS = 220
CHANNELS = [1, 6, 11]
SHOW_HEATMAP = True
USE_MPCA = True

# state
aps = []
show_instructions = True
frame_counter = 0

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

# -------------- Utility: draw circle -------------
def draw_circle_mpca(xc, yc, radius, color=(0.0, 1.0, 0.0, 0.5)):
    r, g, b, a = color
    glColor4f(r, g, b, a)
    glPointSize(1)
    glBegin(GL_POINTS)
    for (x, y) in midpoint_circle_points(int(round(xc)), int(round(yc)), int(round(radius))):
        glVertex2i(x, y)
    glEnd()

def draw_circle_poly(xc, yc, radius, color=(0.0, 1.0, 0.0, 0.5), segments=64):
    r, g, b, a = color
    glColor4f(r, g, b, a)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(xc, yc)
    for i in range(segments + 1):
        theta = 2.0 * math.pi * float(i) / float(segments)
        x = xc + math.cos(theta) * radius
        y = yc + math.sin(theta) * radius
        glVertex2f(x, y)
    glEnd()

# -------------------- Interference / Channel Heuristic --------------------
def interference_score(x, y, radius, channel, other_aps):
    score = 0.0
    for ap in other_aps:
        d = math.hypot(x - ap['x'], y - ap['y'])
        if d < (radius + ap['radius']):
            overlap_factor = (radius + ap['radius'] - d)
            chan_penalty = 1.0 if channel == ap['channel'] else 0.4
            score += overlap_factor * chan_penalty
    return score

def assign_channels(aps_list):
    for i, ap in enumerate(aps_list):
        best_c = CHANNELS[0]
        best_score = float('inf')
        for ch in CHANNELS:
            ap['channel'] = ch
            s = interference_score(ap['x'], ap['y'], ap['radius'], ch, aps_list[:i])
            if s < best_score:
                best_score = s
                best_c = ch
        ap['channel'] = best_c

# -------------------- Generate APs --------------------
def generate_aps(count=AP_COUNT):
    global aps
    aps = []
    margin = 30
    for _ in range(count):
        radius = random.uniform(MIN_RADIUS, MAX_RADIUS)
        x = random.uniform(margin + radius, WIDTH - margin - radius)
        y = random.uniform(margin + radius, HEIGHT - margin - radius)
        aps.append({'x': x, 'y': y, 'radius': radius, 'channel': random.choice(CHANNELS)})
    assign_channels(aps)

# -------------------- Rendering --------------------
def draw_heatmap():
    for ap in aps:
        cx, cy, r = ap['x'], ap['y'], ap['radius']
        rings = 8
        for i in range(rings, 0, -1):
            frac = i / rings
            alpha = 0.18 * frac
            if ap['channel'] == CHANNELS[0]: color = (0.2, 0.6, 1.0, alpha)
            elif ap['channel'] == CHANNELS[1]: color = (0.4, 1.0, 0.2, alpha)
            else: color = (1.0, 0.6, 0.2, alpha)
            if USE_MPCA:
                draw_circle_mpca(cx, cy, r * frac, color)
            else:
                draw_circle_poly(cx, cy, r * frac, color)

def draw_aps():
    glPointSize(6)
    glBegin(GL_POINTS)
    for ap in aps:
        if ap['channel'] == CHANNELS[0]: glColor3f(0.2, 0.6, 1.0)
        elif ap['channel'] == CHANNELS[1]: glColor3f(0.4, 1.0, 0.2)
        else: glColor3f(1.0, 0.6, 0.2)
        glVertex2f(ap['x'], ap['y'])
    glEnd()

    for ap in aps:
        color = (0.8, 0.8, 0.8, 0.9)
        if USE_MPCA: draw_circle_mpca(ap['x'], ap['y'], ap['radius'], color)
        else: draw_circle_poly(ap['x'], ap['y'], ap['radius'], color)
    glColor3f(1.0, 1.0, 1.0)
    for ap in aps: draw_text(int(ap['x']) + 6, int(ap['y']) + 6, f"CH:{ap['channel']}")

# -------------------- Text helper --------------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_12):
    glRasterPos2i(x, y)
    for ch in text: glutBitmapCharacter(font, ord(ch))

# -------------------- Display / Callbacks --------------------
def display():
    global frame_counter
    frame_counter += 1

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # grid
    glColor3f(0.12, 0.12, 0.12)
    glBegin(GL_LINES)
    step = 50
    for x in range(0, WIDTH, step): glVertex2f(x,0); glVertex2f(x,HEIGHT)
    for y in range(0, HEIGHT, step): glVertex2f(0,y); glVertex2f(WIDTH,y)
    glEnd()

    if SHOW_HEATMAP: draw_heatmap()
    draw_aps()

    # Fake resource usage bar (animated)
    usage = 50 + 30 * math.sin(frame_counter * 0.1)
    glColor3f(1.0,0.8,0.2)
    glBegin(GL_QUADS)
    glVertex2f(10, 20)
    glVertex2f(10 + usage*2, 20)
    glVertex2f(10 + usage*2, 25)
    glVertex2f(10, 25)
    glEnd()
    draw_text(10, 28, f"Laptop Resource Bar (simulated)")

    if show_instructions:
        glColor3f(1.0,1.0,1.0)
        lines = [
            "Controls: Space=regen APs  +/-=change AP count  H=toggle heatmap",
            "M=toggle MPCA/poly  I=toggle instructions  Q/Esc=quit",
        ]
        y = HEIGHT - 20
        for ln in lines: draw_text(10, y, ln); y -= 16

    glutSwapBuffers()

def reshape(w, h):
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = w, h
    glViewport(0,0,w,h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global AP_COUNT, SHOW_HEATMAP, USE_MPCA, show_instructions
    k = key.decode('utf-8') if isinstance(key, bytes) else key
    if k == ' ': generate_aps(AP_COUNT)
    elif k == '+': AP_COUNT+=1; generate_aps(AP_COUNT)
    elif k == '-': AP_COUNT=max(1,AP_COUNT-1); generate_aps(AP_COUNT)
    elif k in ('h','H'): SHOW_HEATMAP=not SHOW_HEATMAP
    elif k in ('m','M'): USE_MPCA=not USE_MPCA
    elif k in ('i','I'): show_instructions=not show_instructions
    elif k in ('q','Q','\x1b'): glutLeaveMainLoop()
    glutPostRedisplay()

def timer(value):
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0)

# -------------------- Main --------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_ALPHA)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Coverage Analyzer - MPCA")
    glClearColor(0.06, 0.06, 0.06, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)

    generate_aps(AP_COUNT)

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(33, timer, 0)
    try:
        glutMainLoop()
    except Exception as e:
        print('Exiting:', e)

if __name__ == '__main__':
    main()