### Imports ###################################################################
 
from picamera.array import PiRGBArray
from picamera import PiCamera
from functools import partial
 
import multiprocessing as mp
import time
import cv2
 
 
### Setup #####################################################################
 
resX = 320
resY = 240
 
# Setup the camera
camera = PiCamera()
camera.resolution = ( resX, resY )
camera.framerate = 30
 
fps = 0
t_start = time.time()
 
# Use this as our output
rawCapture = PiRGBArray( camera, size=( resX, resY ) )
 
# The face cascade file to be used
face_cascade = cv2.CascadeClassifier( '/home/xuziheng/Desktop/models/haarcascade_eye_tree_eyeglasses.xml' )
 
 
### Helper Functions ##########################################################
 
def get_faces( img ):
 
    gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
    return face_cascade.detectMultiScale( gray ), img
 
def draw_frame( img, faces ):
 
    global fps
    global time_t
 
    print("Found " + str( len( faces ) ) + " eye(s)")
 
    # Draw a rectangle around every face
    for ( x, y, w, h ) in faces:
        cv2.rectangle( img, ( x, y ),( x + w, y + h ), ( 200, 255, 0 ), 2 )
 
    # Calculate and show the FPS
    fps = fps + 1
    sfps = fps / (time.time() - t_start)
    cv2.putText(img, "FPS : " + str( int( sfps ) ), ( 10, 10 ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 ) 
 
    cv2.imshow( "Frame", img )
    cv2.waitKey( 1 )
 
 
### Main ######################################################################
 
if __name__ == '__main__':
 
    pool = mp.Pool( processes=4 )
 
    i = 0
    rList = [None] * 17
    fList = [None] * 17
    iList = [None] * 17
 
    camera.capture( rawCapture, format="bgr" )  
 
    for x in range ( 17 ):
        rList[x] = pool.apply_async( get_faces, [ rawCapture.array ] )
        fList[x], iList[x] = rList[x].get()
        fList[x] = []
 
    rawCapture.truncate( 0 )    
 
    for frame in camera.capture_continuous( rawCapture, format="bgr", use_video_port=True ):
        image = frame.array
        image = cv2.flip( image, 0 )
 
        if   i == 1:
            rList[1] = pool.apply_async( get_faces, [ image ] )
            draw_frame( iList[2], fList[1] )
 
        elif i == 2:
            iList[2] = image
            draw_frame( iList[3], fList[1] )
 
        elif i == 3:
            iList[3] = image
            draw_frame( iList[4], fList[1] )
 
        elif i == 4:
            iList[4] = image
            fList[5], iList[5] = rList[5].get()
            draw_frame( iList[5], fList[5] )
 
        elif i == 5:
            rList[5] = pool.apply_async( get_faces, [ image ] )
            draw_frame( iList[6], fList[5] )
 
        elif i == 6:
            iList[6] = image
            draw_frame( iList[7], fList[5] )
 
        elif i == 7:
            iList[7] = image
            draw_frame( iList[8], fList[5] )
 
        elif i == 8:
            iList[8] = image
            fList[9], iList[9] = rList[9].get()
            draw_frame( iList[9], fList[9] )
 
        elif i == 9:
            rList[9] = pool.apply_async( get_faces, [ image ] )
            draw_frame( iList[10], fList[9] )
 
        elif i == 10:
            iList[10] = image
            draw_frame( iList[11], fList[9] )
 
        elif i == 11:
            iList[11] = image
            draw_frame( iList[12], fList[9] )
 
        elif i == 12:
            iList[12] = image
            fList[13], iList[13] = rList[13].get()
            draw_frame( iList[13], fList[13] )
 
        elif i == 13:
            rList[13] = pool.apply_async( get_faces, [ image ] )
            draw_frame( iList[14], fList[13] )
 
        elif i == 14:
            iList[14] = image
            draw_frame( iList[15], fList[13] )
 
        elif i == 15:
            iList[15] = image
            draw_frame( iList[16], fList[13] )
 
        elif i == 16:
            iList[16] = image
            fList[1], iList[1] = rList[1].get()
            draw_frame( iList[1], fList[1] )
 
            i = 0
 
        i += 1
 
        rawCapture.truncate( 0 )
