import cv2
import time
import os

def video_to_frames(input_loc, output_loc):

    try:
        os.mkdir(output_loc)
    except OSError:
        pass
    # Log the time
    time_start = time.time()
    # Start capturing the feed
    cap = cv2.VideoCapture(input_loc)
    # Find the number of frames
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print ("Number of frames: ", video_length)
    count = 0
    print ("Converting video..\n")
    # Start converting the video
    while cap.isOpened():
        # Extract the frame
        ret, frame = cap.read()
        #1000 is 1 frame per second, so currently getting 2 frames per second
        cap.set(cv2.CAP_PROP_POS_MSEC, (count*500))
        # Write the results back to output location.
        cv2.imwrite(output_loc + "/%#05d.jpg" % (count+1), frame)
        count = count + 1
        # If there are no more frames left
        if (count*15 > (video_length-1)): #change the count according for a 30fps count is set at 15
            # Log the time again
            time_end = time.time()
            # Release the feed
            cap.release()
            # Print stats
            print ("Done extracting frames.\n%d frames extracted" % count)
            print ("It took %d seconds forconversion." % (time_end-time_start))
            break

input_loc = r"C:\Users\MyongJoon\Desktop\Senior_Spring\COSI149B\python_script\training\IMG_1008.MOV"
output_loc = r"C:\Users\MyongJoon\Desktop\Senior_Spring\COSI149B\python_script\training\IMG"
video_to_frames(input_loc, output_loc)
