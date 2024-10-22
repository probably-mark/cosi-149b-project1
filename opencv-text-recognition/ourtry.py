# USAGE
# python text_detection_video.py --east frozen_east_text_detection.pb

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from imutils.object_detection import non_max_suppression
import numpy as np
import argparse
import imutils
import time
import cv2
import pytesseract


def decode_predictions(scores, geometry):
    # grab the number of rows and columns from the scores volume
    # initialize our set of bounding box rectangles and corresponding confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []
    x_count = []
    y_count = []
    offsetX_box = []

    # loop over the number of rows
    for y in range(0, numRows):
        # extract the scores, followed by the geometrical data used to derive potential bounding box
        # coordinates that surround text
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # loop over the number of columns
        for x in range(0, numCols):
            # if our score does not have sufficient probability, ignore it
            if scoresData[x] < args["min_confidence"]:
                continue

            # compute the offset factor as our resulting feature maps will be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # extract the rotation angle for the prediction and then compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height of the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # compute both the starting and ending (x, y)-coordinates for the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # add the bounding box coordinates and probability score to our respective lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])
            x_count.append(x)
            y_count.append(y)
            offsetX_box.append(offsetX)

    # return a tuple of the bounding boxes and associated confidences
    return (rects, confidences, x_count, y_count, xData1, xData3, offsetX_box)


def filter_text(text):
    if text is "":
        return True

    is_removed_dash_digit = text.replace("-", "").isdigit()
    return not is_removed_dash_digit


def write_to_file(path, text):
    f = open(path + ".txt", "a+")
    f.write(text + "\n")
    return f


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-east", "--east", type=str, required=True,
                help="path to input EAST text detector")
ap.add_argument("-v", "--video", type=str,
                help="path to optinal input video file")
ap.add_argument("-c", "--min-confidence", type=float, default=0.3,
                help="minimum probability required to inspect a region")
ap.add_argument("-w", "--width", type=int, default=320,
                help="resized image width (should be multiple of 32)")
ap.add_argument("-e", "--height", type=int, default=320,
                help="resized image height (should be multiple of 32)")
args = vars(ap.parse_args())

# initialize the original frame dimensions, new frame dimensions, and ratio between the dimensions
(W, H) = (None, None)
(newW, newH) = (args["width"], args["height"])
(rW, rH) = (None, None)

# define the two output layer names for the EAST detector model that we are interested -- the first is the ]
# output probabilities and the second can be used to derive the bounding box coordinates of text
layerNames = [
    "feature_fusion/Conv_7/Sigmoid",
    "feature_fusion/concat_3"]

# load the pre-trained EAST text detector
print("[INFO] loading EAST text detector...")
net = cv2.dnn.readNet(args["east"])

vs = cv2.VideoCapture(args["video"])
width = int(vs.get(3))
height = int(vs.get(4))

# start the FPS throughput estimator
fps = FPS().start()
frame_count = 0

# loop over frames from the video stream
while True:
    # grab the current frame, then handle if we are using a
    # VideoStream or VideoCapture object
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    frame_count += 1

    # check to see if we have reached the end of the stream
    if frame is None:
        break

    # resize the frame, maintaining the aspect ratio
    frame = imutils.resize(frame, width=1000)
    # TODO: Gray scale frames
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    orig = frame.copy()

    # if our frame dimensions are None, we still need to compute the
    # ratio of old frame dimensions to new frame dimensions
    if W is None or H is None:
        (H, W) = frame.shape[:2]
        rW = W / float(newW)
        rH = H / float(newH)

    # resize the frame, this time ignoring aspect ratio
    frame = cv2.resize(frame, (newW, newH))

    # construct a blob from the frame and then perform a forward pass
    # of the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(frame, 1.0, (newW, newH),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    # decode the predictions, then  apply non-maxima suppression to
    # suppress weak, overlapping bounding boxes
    (rects, confidences, x_count, y_count, xData1, xData3, offsetX_box) = decode_predictions(scores, geometry)
    boxes = non_max_suppression(np.array(rects), probs=confidences)


    # Config for Tesseract
    config = ('-l eng --oem 1 --psm 6')

    # loop over the bounding boxes
    for (startX, startY, endX, endY) in boxes:
        # scale the bounding box coordinates based on the respective
        # ratios
        startX = max(int(startX * rW), 0)
        startY = max(int(startY * rH), 0)
        endX = int(endX * rW)
        endY = int(endY * rH)

        tempImage = orig.copy()
        cv2.rectangle(tempImage, (startX, startY), (endX, endY), (0, 255, 0), 2)

        # Crop image and focus only in bounding box
        cropped = tempImage[startY:(startY + endY), startX:(startX + endX)].copy()
        text = pytesseract.image_to_string(cropped, config=config)
        if filter_text(text):
            continue

        frame_no = int(vs.get(1))
        text_file = "Frame " + str(frame_no) + ": [" + str(startX) + ", " + str(startY) + ", " + str(endX) + ", " \
                    + str(endY) + "], " + text
        f = write_to_file(args["video"], text_file)
        print("Frame " + str(frame_no) + ": [" + str(startX) + ", " + str(startY) + ", " + str(endX) + ", " \
              + str(endY) + "], " + text)

        # draw the bounding box on the frame
        cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
        cv2.putText(orig, text, (startX, startY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

    # update the FPS counter
    fps.update()

    # show the output frame
    cv2.imshow("Text Detection", orig)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# if we are using a webcam, release the pointer
if not args.get("video", False):
    vs.stop()

# otherwise, release the file pointer
else:
    vs.release()

# Close file
f.close()

# close all windows
cv2.destroyAllWindows()
