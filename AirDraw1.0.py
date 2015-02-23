from Tkinter import *
import cv2
import numpy as np

# color ranges 
lower_blue = np.array([110,50,50], np.uint8)
upper_blue = np.array([130,255,255], np.uint8)

lower_red = np.array([0, 100, 100], np.uint8)
upper_red = np.array([20, 255, 255], np.uint8)

lower_yellow = np.array([25, 80, 80],np.uint8)
upper_yellow = np.array([34, 255, 255],np.uint8)

lower_green = np.array([50, 100, 100],np.uint8)
upper_green = np.array([70, 255, 255],np.uint8)

cam_index = 0 # Default camera is at index 0.
cv2.namedWindow("Air Draw 1.0", cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(cam_index) # Video capture object
cap.open(cam_index) # Enable the camera

points = []
webcamButtonTimer = 0
canvasButtonTimer = 0

bestCnt = 0

def openWebcamDrawing():
	cam_index = 0 # Default camera is at index 0.
	cv2.namedWindow("real", cv2.WINDOW_NORMAL)
	cap = cv2.VideoCapture(cam_index) # Video capture object
	cap.open(cam_index) # Enable the camera

	
	points = []
	saved = False
	picCount = 1
	colorChosen = False
	bestCnt = 0
	timer = 0
	textTimer = 0
	help = False
	color = (0, 0, 255) # Start off as red marker
	chooseColor = False
	draw = False
	clickTimer = 0
	brushSize = 4
	chooseBrush = False
	brushTimer = 0
	maximumArea = 3000

	# Button boundary checking

	def green(x, y):
		return 30 <= x <= 150 and 50 <= y <= 140

	def blue(x, y):
		return 30 <= x <= 150 and 160 <= y <= 250

	def red(x, y):
		return 30 <= x <= 150 and 270 <= y <= 360

	def small(x, y):
		return 1000 <= x <= 1100 and 100 <= y <= 150

	def medium(x, y):
		return 950 <= x <= 1150 and 200 <= y <= 300

	def big(x, y):
		return 900 <= x <= 1200 and 350 <= y <= 500

	# Which color user chose
	def BGR2CLR(color):
		if color[0] == 255:
			return "Blue"
		elif color[1] == 255:
			return "Green"
		else:
			return "Red"


	while True:
	    ret, frame = cap.read()
	    # Iff webcam is open
	    if frame is not None:
	    	# Getting thresholded image for specified color
	        frame = cv2.flip(frame, 1)
	        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	        frame_threshed = cv2.inRange(hsv_img, lower_yellow, upper_yellow)

	        # Checking is user is still on the board
	     	centroid_x, centroid_y = (None, None)
	        contours, hierarchy = cv2.findContours(frame_threshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	        # Finds object in user's hand
	        maxArea = 0
	        for cnt in contours:
	            area = cv2.contourArea(cnt)
	            if area > maxArea:
	                maxArea = area
	                bestCnt = cnt

	        # Making sure other yellow in the room isn't picked up
	        if cv2.contourArea(bestCnt) > maximumArea:

	            M = cv2.moments(bestCnt)
	            if M['m00'] != 0.0:
	                centroid_x = int(M['m10']/M['m00'])
	                centroid_y = int(M['m01']/M['m00'])
	                # Marker attributes and information
	                if draw: points.append((centroid_x, centroid_y, color, brushSize))
	            	else: points.append((True, True))

	                cv2.circle(frame, (centroid_x, centroid_y), 5*brushSize, color, -1)
	        else:
	        	# If user went off board
	            if len(points) > 0:
	                points.append((True, True))

	        for i in xrange(len(points)-1):
	            if points[i][:2] == (True, True) or points[i+1][:2] == (True, True):
	                continue
	            else:
	                initX, initY = points[i][:2]
	                cv2.line(frame, (initX, initY), points[i+1][:2], points[i][2], points[i][3])

	        if help == True:
	        	cv2.putText(frame, "Make sure the color is always facing the camera!", 
	        	(50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 4)
	        	cv2.putText(frame, "Press 'c' to choose a different color by hovering your pointer over it!", (50, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(frame, "Press 'd' to toggle the drawing option.", 
	        		(50, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(frame, "Press 's' to save the image to your Pictures folder!", 
	        		(50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(frame, "Press 'r' to erase all your drawings!", 
	        		(50, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(frame, "Press 'b' to change your brush size by hovering over the size. ", 
	        		(50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(frame, "Press 'Esc' to go back to the main screen!", 
	        		(50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

	        if textTimer < 30: # Arbitrary button waiting time
	        	cv2.putText(frame, "Press 'h' for help!", (50, 600), cv2.FONT_HERSHEY_SIMPLEX, 
	        		1, (0, 255, 0), 3)
	        	textTimer += 1
	        if saved:
	        	if timer < 10:
	        		cv2.putText(frame, "Saved!", (400, 500), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 0,), 4)
	        		timer += 1
	        	else:
	        		timer = 0
	        		saved = False

	        if chooseColor:

	        	cv2.rectangle(frame, (30, 50), (150, 140), (0, 255, 0), -1)
	        	cv2.rectangle(frame, (30, 160), (150, 250), (255, 0, 0), -1)
	        	cv2.rectangle(frame, (30, 270), (150, 360), (0, 0, 255), -1)
	        	if (centroid_x, centroid_y) != (None, None) and green(centroid_x, centroid_y):
	        		if clickTimer <= 15: # Arbitrary button waiting time
	        			clickTimer += 1
	        			# Button animation
	        			cv2.rectangle(frame, (30, 50), (150, 140), (0, 255, 0), 6)
	        		else:
	        			clickTimer = 0
	        			color = (0, 255, 0)
	        			colorChosen = True
	        	elif (centroid_x, centroid_y) != (None, None) and blue(centroid_x, centroid_y):
	        		if clickTimer <= 15:
	        			clickTimer += 1
	        			cv2.rectangle(frame, (30, 160), (150, 250), (255, 0, 0), 6)
	        		else:
	        			clickTimer = 0
	        			color = (255, 0, 0)
	        			colorChosen = True
	        	elif (centroid_x, centroid_y) != (None, None) and red(centroid_x, centroid_y):
	        		if clickTimer <= 15:
	        			clickTimer += 1
	        			cv2.rectangle(frame, (30, 270), (150, 360), (0, 0, 255), 6)
	        		else:
	        			clickTimer = 0
	        			color = (0, 0, 255)
	        			colorChosen = True
	        	else: clickTimer = 0
	        if colorChosen:
	        	if timer < 20:
	        		cv2.putText(frame, BGR2CLR(color), (400, 500), cv2.FONT_HERSHEY_SIMPLEX, 4, color, 4)
	        		timer += 1
	        	else:
	        		timer = 0
	        		colorChosen = False

	        if chooseBrush:
	        	cv2.rectangle(frame, (1000, 100), (1100, 150), (0, 0, 0), -1)
	        	cv2.putText(frame, "Small", (1005, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
	        	cv2.rectangle(frame, (950, 200), (1150, 300), (0, 0, 0), -1)
	        	cv2.putText(frame, "Medium", (990, 260), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
	        	cv2.rectangle(frame, (900, 350), (1200, 500), (0, 0, 0), -1)
	        	cv2.putText(frame, "Big", (1020, 440), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
	        	if (centroid_x, centroid_y) != (None, None) and small(centroid_x, centroid_y):
	        		if brushTimer <= 15:
	        			brushTimer += 1
	        			cv2.rectangle(frame, (1000, 100), (1100, 150), (255, 255, 255), 6)
	        		else:
	        			brushTimer = 0
	        			brushSize = 2
	        	elif (centroid_x, centroid_y) != (None, None) and medium(centroid_x, centroid_y):
	        		if brushTimer <= 15:
	        			brushTimer += 1
	        			cv2.rectangle(frame, (950, 200), (1150, 300), (255, 255, 255), 6)
	        		else:
	        			brushTimer = 0
	        			brushSize = 5
	        	elif (centroid_x, centroid_y) != (None, None) and big(centroid_x, centroid_y):
	        		if brushTimer <= 15:
	        			brushTimer += 1
	        			cv2.rectangle(frame, (900, 350), (1200, 500), (255, 255, 255), 6)
	        		else:
	        			brushTimer = 0
	        			brushSize = 8
	        	else:
	        		brushTimer = 0
	        cv2.imshow("real", frame)

	    k = cv2.waitKey(1) & 0xFF

	    if k == ord('r'):
	    	points = []
	    elif k == ord('d'):
	    	draw = not draw
	    elif k == ord('s'):
	    	saved = True
	    	cv2.imwrite('Webcam%s.png' % str(picCount), frame)
	    	picCount += 1
	    elif k == ord('h'):
	    	help = not help
	    elif k == ord('c'):
	    	chooseColor = not chooseColor
	    elif k == ord('b'):
	    	chooseBrush = not chooseBrush
	    elif k == 27: # Esc
	    	break
	cv2.destroyAllWindows()

def openBlankCanvasDrawing():
	cam_index = 0 # Default camera is at index 0.
	cv2.namedWindow("real", cv2.WINDOW_NORMAL)
	cap = cv2.VideoCapture(cam_index) # Video capture object
	cap.open(cam_index) # Enable the camera
	img = np.zeros((720, 1280,3), np.uint8)

	points = []
	erase = []
	timer = 0
	picCount = 1
	saved = False
	centers = []
	color = (0, 0, 255)
	beginning = True
	drawing = False
	help = False
	textTimer = 0

	#bestCnt = 0

	def nothing(x):
	    pass

	cv2.createTrackbar('R','real',0,255,nothing)
	cv2.createTrackbar('G','real',0,255,nothing)
	cv2.createTrackbar('B','real',0,255,nothing)

	def draw(points, frame):
	    for i in xrange(len(points)-1):
	        if points[i][:2] == (True, True) or points[i+1][:2] == (True, True):
	            continue
	        else:
	            print points[i][:2]
	            initX, initY = points[i][:2]
	            cv2.line(img, (initX, initY), points[i+1][:2], color, 4)

	cv2.putText(img, "Red", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
	cv2.putText(img, "Green", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
	cv2.putText(img, "Blue", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

	while True:
	    ret, frame = cap.read()
	    if frame is not None:
	        frame = cv2.flip(frame, 1)
	        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	        frame_threshed = cv2.inRange(hsv_img, lower_yellow, upper_yellow)
	     
	        contours, hierarchy = cv2.findContours(frame_threshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	        r = cv2.getTrackbarPos('R','real')
	        g = cv2.getTrackbarPos('G','real')
	        b = cv2.getTrackbarPos('B','real')

	        maxArea = 0
	        for cnt in contours:
	            area = cv2.contourArea(cnt)
	            if area > maxArea:
	                maxArea = area
	                bestCnt = cnt
	        if cv2.contourArea(bestCnt) > 4000:

	            M = cv2.moments(bestCnt)
	            if M['m00'] != 0.0:
	                centroid_x = int(M['m10']/M['m00'])
	                centroid_y = int(M['m01']/M['m00'])
	                if beginning:
	                    initX, initY = centroid_x, centroid_y
	                    beginning = False
	                else:
	                    if drawing: cv2.line(img, (initX, initY), (centroid_x, centroid_y), (b, g, r), 4)
	                    initX, initY = centroid_x, centroid_y
	        else:
	            beginning = True


	        frame_threshed = cv2.inRange(hsv_img, lower_blue, upper_blue)
	        contours, hierarchy = cv2.findContours(frame_threshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	        maxArea = 0
	        for cnt in contours:
	            area = cv2.contourArea(cnt)
	            if area > maxArea:
	                maxArea = area
	                bestCnt = cnt

	        if cv2.contourArea(bestCnt) > 5000:
	            M = cv2.moments(bestCnt)
	            if M['m00'] != 0.0:
	                centroid_x = int(M['m10']/M['m00'])
	                centroid_y = int(M['m01']/M['m00'])
	                cv2.circle(img, (centroid_x, centroid_y), 40, (0, 0, 0), -1)

	        if textTimer < 30:
	        	cv2.namedWindow("Start", cv2.WINDOW_NORMAL)
	        	start = np.zeros((720, 1280, 3), np.uint8)
	        	cv2.putText(start, "Press 'h' for help!", (50, 700), cv2.FONT_HERSHEY_SIMPLEX, 
	        		1, (0, 255, 0), 2)
	        	cv2.imshow("Start", start)
	        	textTimer += 1
	        else:
	        	cv2.destroyWindow("Start")

	        if saved:
	        	cv2.namedWindow("Saved", cv2.WINDOW_NORMAL)
	        	save = np.zeros((720, 1280,3), np.uint8)
	        	cv2.putText(save, "Saved!", (450, 500), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 2)
	        	cv2.imshow("Saved", save)
	        	if timer == 10: # Arbitrary button time
	        		cv2.destroyWindow("Saved")
	        		timer = 0
	        		saved = False
	        	else:
	        		timer += 1

	        if help == True:
	        	cv2.namedWindow("Help", cv2.WINDOW_NORMAL)
	        	helping = np.zeros((720, 1280, 3), np.uint8)
	        	cv2.putText(helping, "Make sure the color is always facing the camera!", 
	        		(50, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(helping, "Use your mouse to change the trackbar values to choose any color!", 
	        		(50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(helping, "Press 'd' to toggle the drawing option.", 
	        		(50, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(helping, "Press 's' to save the image to your Pictures folder!", 
	        		(50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(helping, "Press 'r' to erase all your drawing!", 
	        		(50, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(helping, "You can erase specific parts of your drawing by waving the blue object.", 
	        		(50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.putText(helping, "Press 'Esc' to go back to the main screen!", 
	        		(50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
	        	cv2.imshow("Help", helping)


	        else:
	        	cv2.imshow("real", img)

	    k = cv2.waitKey(1) & 0xFF

	    if k == ord('r'):
	        points = []
	        img = np.zeros((720, 1280,3), np.uint8)
	        cv2.putText(img, "Red", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
	        cv2.putText(img, "Green", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
	        cv2.putText(img, "Blue", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
	    elif k == ord('s'):
	    	saved = True
	    	cv2.imwrite('Canvas%s.png' % str(picCount), img)
	    	picCount += 1
	    elif k == ord('d'):
	    	drawing = not drawing
	    elif k == ord('h'):
	    	help = not help
	    	if help == False:
	    		cv2.destroyWindow("Help")
	    elif k == 27:
	        break

	cv2.destroyAllWindows()

def withinBoundsWebcam(x, y):
	return 100 <= x <= 400 and 200 <= y <= 500 # Button bounaries 

def withinBoundsBlank(x, y):
	return 900 <= x <= 1200 and 200 <= y <= 500

webcamButtonColor = (255, 0, 0)
canvasButtonColor = (0, 0, 255)

# Main page
while True:
    ret, frame = cap.read()
    if frame is not None:
    	
        frame = cv2.flip(frame, 1)
        
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame_threshed = cv2.inRange(hsv_img, lower_yellow, upper_yellow)
        
     
        contours, hierarchy = cv2.findContours(frame_threshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        webcamButtonColor = (255, 0, 0)
        canvasButtonColor = (0, 0, 255)
        maxArea = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > maxArea:
                maxArea = area
                bestCnt = cnt
        if cv2.contourArea(bestCnt) > 5000:
        	
            M = cv2.moments(bestCnt)
            if M['m00'] != 0.0:
                centroid_x = int(M['m10']/M['m00'])
                centroid_y = int(M['m01']/M['m00'])
                cv2.circle(frame, (centroid_x, centroid_y), 15, (255, 0, 255), -1)
            if withinBoundsWebcam(centroid_x, centroid_y):
            	webcamButtonColor = (0, 0, 0)
            	if webcamButtonTimer == 20:
            		webcamButtonTimer = 0
            		openWebcamDrawing()
            	else: webcamButtonTimer += 1
            else:
            	webcamButtonTimer = 0
            	webcamButtonColor = (255, 0, 0)

            if withinBoundsBlank(centroid_x, centroid_y):
            	canvasButtonColor = (0, 0, 0)
            	if canvasButtonTimer == 20:
            		canvasButtonTimer = 0
            		openBlankCanvasDrawing()
            	else: canvasButtonTimer += 1
            else:
            	canvasButtonTimer = 0
            	canvasButtonColor = (0, 0, 255)

        # Buttons/ Help statements/ Title
        cv2.rectangle(frame, (100, 200), (400, 500), webcamButtonColor, -1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame,'Webcam Drawing',(120,350), font, 1,(255,255,255),2)
        cv2.rectangle(frame, (900, 200), (1200, 500), canvasButtonColor, -1)
        cv2.putText(frame, "Blank Canvas", (950, 350), font, 1, (255, 255, 255), 2)
        cv2.putText(frame, "Use the yellow object to choose where you'd like to draw! (It's your 'cursor')", 
        	(20, 550), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press Esc to quit the app!", (430, 250), cv2.FONT_HERSHEY_SIMPLEX, 
        	1, (0, 255, 0), 2)
        cv2.putText(frame, "Air Draw 1.0", (350, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, 
        	(255, 255, 255), 3)
        cv2.imshow("Air Draw 1.0", frame)

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
            break
cv2.destroyAllWindows()