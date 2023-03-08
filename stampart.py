import cv2 as cv
from mecode import G
from random import randint
from math import sin, cos

max_width = 200 # mm
max_height = 200 # mm
step_length = 1 # size of each pixel in mm
speed = 1000
import_imgfile = 'test_images/' + 'test4.jpg'
export_imgfile = 'test_images/' + 'test4save.jpg'
export_gcodefile = 'stampart.gcode'


### PROCESSING IMAGE
# read image
img = cv.imread(import_imgfile, cv.IMREAD_GRAYSCALE) # read as grayscale
if img is None:
     print("Check file path")

# resize image to fit in a4 dimensions 
scale_percent = 100
margin = 10 # mm
if img.shape[0] > max_height/step_length:
    if scale_percent > int((max_height-margin*2) / step_length / img.shape[0] * 100):
        scale_percent = int((max_height-margin*2) / step_length / img.shape[0] * 100)
if img.shape[1] > max_width/step_length:
    if scale_percent > int((max_width-margin*2) / step_length / img.shape[1] * 100):
        scale_percent = int((max_width-margin*2) / step_length / img.shape[1] * 100) 

width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
resized = cv.resize(img, dim, interpolation = cv.INTER_AREA)

# change contrast and brightness to improve results 
alpha = 1.2
beta = -40
contrast_resized = cv.convertScaleAbs(resized, alpha=alpha, beta=beta)

final_img = contrast_resized 
cv.imwrite(export_imgfile, final_img)

# find average value (might be a good cutoff point for brightness-biased images)
# avg_brightness = 0
# for y in range(height):
#     for x in range(width):
#         avg_brightness += final_img[y][x]
# avg_brightness = avg_brightness / (width*height)


### ALPHABETS INTO GCODE STAMPS (couldn't be used because the g-code files are too big)
# alphabets = [
#     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
#     'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
# ]
# alphabets_gcode = []

# for alphabet in alphabets:
#     txtfile = 'gcode_alphabets/' + alphabet + '.txt' # cnc-apps.com was used 
#     txtoutput = ""
#     with open(txtfile, 'r') as f:
#         lines = f.readlines()
#         for line in lines:
#             txtoutput += line
#     alphabets_gcode.append(txtoutput)

# def random_alphabet():
#     ind = randint(0, len(alphabets_gcode)-1)
#     return alphabets_gcode[ind]


### STARS INTO GCODE STAMPS
# this formula is wrong - it won't create a star for certain values of n 
# https://math.fandom.com/wiki/Star_polygon
def star(n):
    sides = n
    angle = 2 * 360 / sides
    
    for n in range(sides):
        g.move(x=step_length*cos(-angle*n), y=step_length*sin(-angle*n))


### GENERATING GCODE
# functions for convenience
def penup():
    g.write("M8\n")
def pendown():
    g.write("M9\n")

# initialise
g = G(outfile=export_gcodefile)
g.write("G21")
g.write("F"+str(speed))
g.home()
penup()

def processpixel(x, y):
    value = 1 - final_img[y][x] / 255 # 0 is white, 1 is black
    g.absolute()
    penup() # removing this line may look better depending on preference 
    g.move(x=x*step_length, y=y*step_length)
    pendown()
    g.relative()

    # draw a star with more vertices for darker pixels 
    if (value > 0.9):
        star(11)
    elif (value > 0.75):
        star(9)
    elif (value > 0.6):
        star(8)
    elif (value > 0.45):
        star(7)
    elif (value > 0.3):
        star(6)

# iterate through each pixels 
for y in range(height-1,0,-1):
    for x in range(width):
        processpixel(x, y)

# end gcode
g.write("M8\nM2")
