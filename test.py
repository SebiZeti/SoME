from manim import *
import math

from matplotlib import image
from matplotlib.pyplot import arrow

#manim test.py -pqm CreateConcavePolygon
#Render video with this command

fill_color = BLUE_D
stroke_color = BLUE_E
hull_color = PURE_RED
highlight_color = RED

# For two points `a` and `b`, return True if the entire polygon is on one side
# of the AB line. Otherwise, return False.
def convexCheck(a: list, b: list, points) -> bool:

    check = 0 # -1 => on left side, 0 => on the line, 1 => on the right side 
    if (a[0] == b[0]):
        
        for p in points:

            if (p[0] < a[0]):

                if (check == 1):
                    return False
                else:
                    check = -1

            elif (p[0] > a[0]):

                if (check == -1):
                    return False
                else:
                    check = 1

        return True 

    else:
        c = [a[0]-b[0], a[1]-b[1], a[2]-b[2]]
        for p in points:
            d = [p[0]-b[0], p[1]-b[1], p[2]-b[2]]
            if (c[0]*d[1] - c[1]*d[0] < 0): # cross product
                if (check == 1):
                    return False
                else :
                    check = -1

            elif c[0]*d[1] - c[1]*d[0] > 0:
                if (check == -1):
                    return False
                else:
                    check = 1
        return True

#Flips between a and b points, sets the coordinates in the points list
def flip(a: list, b: list, points):
    if a[0] == b[0]:
        while i % len(points) != points.index(b):

            d = points[i % len(points)][0] - b[0] # distance
            points[i % len(points)][0] += 2 * d

            i += 1
    else:
        m = (b[1] - a[1]) / (b[0] - a[0]) # slope
        c = (b[0] * a[1] - a[0] * b[1]) / (b[0] - a[0]) # intercept

        i = points.index(a) + 1
        while i % len(points) != points.index(b):

            d = (points[i % len(points)][0] + (points[i % len(points)][1] - c) * m) / (1 + m * m) # distance

            points[i % len(points)][0] = 2 * d - points[i % len(points)][0]
            points[i % len(points)][1] = 2 * d * m - points[i % len(points)][1] + 2 * c

            i += 1

#Project points in the array 'point' between the indecies a and b on the line defined by the point a and b
def projectPointsOnLine(a: int, b: int, points) -> list:
    c = b
    if a > b:
        c = b + len(points)
    result = []
    v1 = [points[a][0]-points[b][0],points[a][1]-points[b][1],points[a][2]-points[b][2]]
    v1Length = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
    for p in (points*2)[a+1:c]:
        v2 = [p[0]-points[b][0],p[1]-points[b][1],p[2]-points[b][2]]
        dotProduct = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
        lengthfactor = dotProduct/(v1Length**2)
        if lengthfactor < 0:
            lengthfactor = 0
        elif lengthfactor > 1:
            lengthfactor = 1
        projectedP = [x*lengthfactor + y for x, y in zip(v1, points[b])]
        result.append(projectedP)
    return result

def rotateList (l: list, first_index: int) -> list:
    return l[first_index:] + l[:first_index]

#Returns the points of the convex hull of the polygon defined by the given list (it must be list[list[3]])
def getHullPoints(points: list) -> list:

    hull_points = []
    first = min(points)
    first_index = points.index(first)
    hull_points.append(points[first_index])
    last = first_index
    i = first_index + 1

    while i != first_index:
        if convexCheck(points[last], points[i], points):
            hull_points += projectPointsOnLine(last, i, points)
            hull_points.append(points[i])
            last = i
        i = (i + 1)%len(points)
    hull_points += projectPointsOnLine(last, first_index, points)
    hull_points = rotateList(hull_points, len(points) - first_index)
    return hull_points

#Calculates camera scale from the polygon's size
def getCameraWidth(points) -> int:
    
    multiplyer = 2  # <- modify this to change scale multiplyer

    return (max(points)[0] - min(points)[0]) * multiplyer

#Finds a flip and executes it, and checks wether the polygon is convex after the flip
def findFlip(points):
    c = 2
    i = 0
    while c <= len(points) / 2:
        while i <= len(points)-1:
            if convexCheck(points[i], points[(i+c) % len(points)], points):
                flip(points[i], points[(i+c) % len(points)], points)

                return True
            i += 1
        c += 1
        i = 0
    print("It's convex!")
    return False

# Generates dashed lines between the given points, returns the lines in a VGroup
def generateDashedLines(points):

    storage = []

    for i in range(len(points)):
        storage.append(DashedLine(points[i-1], points[i], color = stroke_color))

    return VGroup(*storage)

# Finds the midpoint of the line defind by a and b points
def findMidPoint(a: list, b:list) -> list:
    result = []

    for i in range(3):
        result.append((a[i] + b[i]) / 2)

    return result
        

#Runned class, contains all animations
class CreateConcavePolygon(MovingCameraScene):
    def construct(self):
        #The points of the concave polygon
        Frank_points = [
            [1, 3, 0], 
            [0, 2, 0], 
            [0, 0, 0], 
            [-3, 0, 0], 
            [-1, -1, 0], 
            [0, -3, 0], 
            [1, -1, 0], 
            [4, 0, 0],  
            [2, 1, 0],
        ]

        concave = Polygon(*Frank_points, color = stroke_color) # Create Frank
        concave.set_fill(fill_color, opacity=0.75)
        concave.save_state()

        self.play(self.camera.frame.animate.move_to(concave).set(width = getCameraWidth(Frank_points))) # Adjust camera size and position
        self.play(FadeIn(concave), run_time = 2) # Show Frank on screen
        self.wait(2)

        convex_frank = [   # The points of deformed Frank
            [1, 3, 0],     
            [0, 3, 0], 
            [-2, 1.5, 0], 
            [-3, 0, 0], 
            [-2.5, -2, 0],
            [0, -3, 0], 
            [3.5, -3, 0], 
            [4, 0, 0],  
            [3, 2.5, 0],
            ]

        

        wrong_convex = Polygon(*convex_frank, color = stroke_color) # Create Deformed Frank
        wrong_convex.set_fill(fill_color, opacity = 0.75)

        self.play(self.camera.frame.animate.move_to(wrong_convex).set(width = getCameraWidth(Frank_points))) # Adjust camera size and position
        self.play(Transform(concave, wrong_convex)) # Frank -> Deformed Frank
        self.wait(3)
        self.play(Restore(concave)) # Deformed Frank -> Frank

        flip(Frank_points[0], Frank_points[4], Frank_points)  # Flip randonly

        self_intersect = Polygon(*Frank_points, color = stroke_color) # Create self-intersecting "polygon"
        self_intersect.set_fill(fill_color, opacity = 0.75)

        self.play(Transform(concave, self_intersect)) # Execute flip
        self.wait(0.5)

        dashed = generateDashedLines(Frank_points) # Generate dashed outline of the filpped polygon
        self.play(ReplacementTransform(concave, dashed)) # Show dashed oultine (probably buggy, but looks cool)

        self.play(FadeOut(dashed)) # Fade out dashed outline
        self.wait(1)

        Frank_2_points = [  # Define the points for Frank 2
            [0, 4, 0],
            [-1, 0, 0],
            [-1, 2, 0],
            [-2, 3, 0],
            [-3, 1, 0],
            [-1, -1, 0],
            [-5, -1, 0],
            [-3, -2, 0],
            [2, 0, 0],
            [0, 1, 0],
        ]

        #flip(points[0], points[4])  # Flip randomly

        concave = Polygon(*Frank_2_points, color = stroke_color) # Create Frank 2
        concave.set_fill(fill_color, opacity=0.75)
        concave.save_state()

        copy_of_frank_2 = Polygon(*Frank_2_points, color = highlight_color)

        self.play(self.camera.frame.animate.move_to(concave).set(width = getCameraWidth(Frank_2_points))) # Adjust camera size and position
        self.play(Create(concave))  # Show Frank 2
        
        hull = Polygon(*getHullPoints(Frank_2_points)) # Create convex hull
        hull.set_stroke(hull_color) 
        self.bring_to_front(hull) # Put the hull in front of the polygon    

        self.play(Create(hull)) # show the hull on screen
        self.wait(2)

        #automatcally convexifies the polygon
        while findFlip(Frank_2_points):

            flipped = Polygon(*Frank_2_points, color = stroke_color) # Create the polygon after the flip
            flipped.set_fill(fill_color, opacity=0.75)

            flipped_hull = Polygon(*getHullPoints(Frank_2_points)) # Recalculate the hull after the flip
            flipped_hull.set_stroke(hull_color)

            self.play(    # Show the flip
                  Transform(concave, flipped),
                  Transform(hull, flipped_hull,), 
                )
            self.play(self.camera.frame.animate.move_to(flipped).set(width = getCameraWidth(Frank_2_points))) # Adjust camera size and position

        Frank_2_points = [ # Reset Frank 2
            [0, 4, 0],
            [-1, 0, 0],
            [-1, 2, 0],
            [-2, 3, 0],
            [-3, 1, 0],
            [-1, -1, 0],
            [-5, -1, 0],
            [-3, -2, 0],
            [2, 0, 0],
            [0, 1, 0],
            ]

        self.play(Uncreate(hull), Restore(concave))
        self.play(self.camera.frame.animate.move_to(concave).set(width = getCameraWidth(Frank_2_points))) # Adjust camera size and position

        self.play(ShowPassingFlash(copy_of_frank_2.copy().set_color(highlight_color), run_time =2, time_width = 1)) # Highligh Frank 2's perimiter
        self.wait(2)

        prev_line_a = Line(Frank_2_points[0], Frank_2_points[9], color = highlight_color)
        prev_line_b = Line(Frank_2_points[9], Frank_2_points[8], color = highlight_color)
        point_before_flip = Frank_2_points[9]

        flip(Frank_2_points[8], Frank_2_points[0], Frank_2_points)

        flipped = Polygon(*Frank_2_points, color = stroke_color)
        flipped.set_fill(fill_color, opacity=0.75)

        self.play(Transform(concave, flipped), Create(prev_line_a), Create(prev_line_b))
        self.wait(1)

        arrow_a = Arrow(findMidPoint(Frank_2_points[0], point_before_flip), findMidPoint(Frank_2_points[0], Frank_2_points[9]), color = highlight_color)
        arrow_b = Arrow(findMidPoint(point_before_flip, Frank_2_points[8]), findMidPoint(Frank_2_points[8], Frank_2_points[9]), color = highlight_color)
        self.play(Create(arrow_a), Create(arrow_b))
        self.wait(2)

            

class Image(Scene):
    def construct(self):
        
        image = ImageMobject("D:\Sebi\??rp??d\matek\SoME\erdos.jpg")
        image.height = 10
        self.play(FadeIn(image))
        self.wait(5)