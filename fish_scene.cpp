#include <GL/glut.h>
#include <cmath>

void drawPixel(int x, int y) {
    glBegin(GL_POINTS);
        glVertex2i(x, y);
    glEnd();
}

void midpointCircle(int xc, int yc, int r) {
    int x = 0, y = r;
    int d = 1 - r;
    while (x <= y) {
        drawPixel(xc + x, yc + y);
        drawPixel(xc - x, yc + y);
        drawPixel(xc + x, yc - y);
        drawPixel(xc - x, yc - y);
        drawPixel(xc + y, yc + x);
        drawPixel(xc - y, yc + x);
        drawPixel(xc + y, yc - x);
        drawPixel(xc - y, yc - x);
        if (d < 0)
            d += 2 * x + 3;
        else {
            d += 2 * (x - y) + 5;
            y--;
        }
        x++;
    }
}

float fishX = -0.8;

void drawFish() {
    glColor3f(1.0, 0.5, 0.0);
    glBegin(GL_POLYGON);
        glVertex2f(fishX, 0.0);
        glVertex2f(fishX + 0.2, 0.1);
        glVertex2f(fishX + 0.2, -0.1);
    glEnd();

    // Tail
    glBegin(GL_TRIANGLES);
        glVertex2f(fishX - 0.05, 0.0);
        glVertex2f(fishX - 0.15, 0.1);
        glVertex2f(fishX - 0.15, -0.1);
    glEnd();

    // Eye using Midpoint Circle
    glColor3f(0, 0, 0);
    glPointSize(3);
    midpointCircle((int)((fishX + 0.15) * 100), (int)(0.02 * 100), 3);
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    drawFish();
    glFlush();
}

void timer(int) {
    fishX += 0.01;
    if (fishX > 1.0) fishX = -1.0;
    glutPostRedisplay();
    glutTimerFunc(50, timer, 0);
}

void init() {
    glClearColor(0.2, 0.5, 0.9, 1.0);
    glMatrixMode(GL_PROJECTION);
    gluOrtho2D(-1, 1, -1, 1);
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB);
    glutInitWindowSize(600, 600);
    glutCreateWindow("Fish Swimming with Midpoint Circle");
    init();
    glutDisplayFunc(display);
    glutTimerFunc(0, timer, 0);
    glutMainLoop();
    return 0;
}
