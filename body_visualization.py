########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

"""
   This sample shows how to detect a human objects and draw their
   modelised skeleton in an OpenGL window

   Edited by Will Bradford
   Version: 9/18/23
"""
import math
import time

import cv2
import sys
import pyzed.sl as sl
import ogl_viewer.viewer as gl
import cv_viewer.tracking_viewer as cv_viewer
import numpy as np
import argparse
import keyboard

usage = "usage: python3 body_track.py [(-r | --record) record_filename] [(-p | --playback) playback_filename] [-s | --skeleton keypoints]\n" \
        "\trecord_filename: SVO file name for recording frame data. Must be .svo" \
        "\tplayback_filename: SVO file name for playback. Must be .svo" \
        "\tkeypoints: keypoint values being recorded. By default not using this flag will record all points"

if __name__ == "__main__":
  filename = "output.txt"
  recording = False
  playback = False
  analyzed_keypoints = []
  try:
    argparser = argparse.ArgumentParser(description='process arguments for configuration of ZED2')
    argparser.add_argument('-r', '--record', metavar='filename', dest='record_filename',
                           type=str, nargs=1,
                           help="record_filename: SVO file name for recording frame data. Must be .svo")
    argparser.add_argument('-p', '--playback', metavar='filename', dest='playback_filename',
                           type=str, nargs=1, help="playback_filename: SVO file name for playback. Must be .svo")
    argparser.add_argument('-k', '--keypoints', metavar='keypoint', dest='keypoints', action='append',
                           type=str, nargs="*", help="keypoints: list of keypoints to keep track of")
    args = argparser.parse_args()
    if args.record_filename:
      filename = args.record_filename[0]
      recording = True
    if args.playback_filename:
      filename = args.playback_filename[0]
      playback = True
    if args.record_filename and args.playback_filename:
      raise Exception("\tcannot playback and record a video at the same time")
    if args.keypoints:
      analyzed_keypoints += [int(number) for number in args.keypoints[0]]
    else:
      # analyzed_keypoints = range(0, 18)
      analyzed_keypoints = [4]  # temporary tests
  except Exception as e:
    print("Invalid use of main.py. Error:\n")
    print("\t", e)
    exit(1)

  print("Running Body Tracking sample ... Press 'q' to quit")

  """ Configuration of the Camera """
  init_params = sl.InitParameters()

  # Configuration for playback
  input_type = None
  if playback:
    print("Using SVO file: {0}".format(filename))
    input_type = sl.InputType()
    input_type.set_from_svo_file(filename)
    init_params = sl.InitParameters(input_t=input_type, svo_real_time_mode=True)

  """
  Create a InitParameters object and set configuration parameters
  Camera Resolution:
      1080p  = sl.RESOLUTION.HD1080
      720p   = sl.RESOLUTION.HD720: Best for fast movements
  Camera FPS:
      init_params.camera_fps = (60, 30, 15 for 720p) (30, 15 for 1080p)
  Coordinate Units:
      meters = sl.UNIT.METER
  Coordinate System:
      right-hand y-vertical: sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
  depth mode:
      The depth camera has a default depth range of 0.4m to 20m (minimum-maximum of 0.3m-40m)
          - configured by depth_minimum_distance and depth_maximum_distance
      ULTRA       = sl.DEPTH_MODE.ULTRA: Highest depth range and better preserves Z-accuracy.
      QUALITY     = sl.DEPTH_MODE.QUALITY: has a strong filtering stage giving smooth surfaces.
      PERFORMANCE = sl.DEPTH_MODE.PERFORMANCE: designed to be smooth, can miss some details.
  depth calculation:
      Triangulation using Dr=Z^2*alpha, where Dr is depth resolution, Z the distance and alpha a constant.
  """
  init_params.camera_resolution = sl.RESOLUTION.HD1080
  init_params.coordinate_units = sl.UNIT.METER
  init_params.depth_mode = sl.DEPTH_MODE.ULTRA
  init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

  """
  Tracking Parameters
  https://www.stereolabs.com/docs/api/structsl_1_1PositionalTrackingParameters.html#a1c23e6c0df4bc26e7cc5421aea4d880e

  The intent is for this camera to be static and ignoring IMU data
  Important configuration
  initial_world_transform: Position of the camera in the world frame when the camera is started. By default, it should be identity. 
  enable_pose_smoothing: This mode enables smooth pose correction for small drift correction. default false.
  area_file_path: Area localization file that describes the surroundings, saved from a previous tracking session.
  https://www.stereolabs.com/docs/positional-tracking/area-memory/
  set_as_static: allows the depth stabilizer module to know the camera is static so it can disable visual tracking and reduce computational load
  """

  # Initialize Camera
  zed = sl.Camera()
  err = zed.open(init_params)
  if err != sl.ERROR_CODE.SUCCESS:
    exit(1)
  # err = zed.enable_positional_tracking(tracking_params)
  # if err != sl.ERROR_CODE.SUCCESS:
  #     exit(1)

  # Configuration for recording
  if recording:
    """
    # Set the compression quality to:
    # H.264 (AVCHD), H.265 (HEVC), LOSSY (JPG), LOSSLESS (PNG)
    """
    recording_param = sl.RecordingParameters(filename, sl.SVO_COMPRESSION_MODE.H265)
    err = zed.enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
      print("Error with recording file:\n")
      zed.close()
      exit(1)

  # Enable Positional tracking (mandatory for object detection)
  positional_tracking_parameters = sl.PositionalTrackingParameters()

  # If the camera is static, set to True for efficiency
  positional_tracking_parameters.set_as_static = True
  positional_tracking_parameters.area_file_path = "filename.area"
  zed.enable_positional_tracking(positional_tracking_parameters)

  """ Skeleton Tracking Configuration """
  obj_param = sl.ObjectDetectionParameters()
  obj_param.enable_body_fitting = True  # enables the fitting process of each detected person
  obj_param.enable_tracking = True  # Track people across images flow

  """ Skeleton Configuration """
  obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_ACCURATE  # ACCURATE or FAST
  obj_param.body_format = sl.BODY_FORMAT.POSE_34  # Choose the BODY_FORMAT you wish to use; 18 or 34 keypoints

  # Enabling skeleton capture
  obj_param.image_sync = True

  # Enable Object Detection module
  zed.enable_object_detection(obj_param)

  obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
  obj_runtime_param.detection_confidence_threshold = 40

  # Get ZED camera information
  camera_info = zed.get_camera_information()

  # 2 CV viewer utilities
  display_resolution = sl.Resolution(min(camera_info.camera_resolution.width, 1280),
                                     min(camera_info.camera_resolution.height, 720))
  image_scale = [display_resolution.width / camera_info.camera_resolution.width
    , display_resolution.height / camera_info.camera_resolution.height]

  # Create OpenGL viewer
  viewer = gl.GLViewer()
  left_cam = camera_info.calibration_parameters.left_cam
  viewer.init(left_cam, obj_param.enable_tracking, obj_param.body_format)

  # Create ZED objects filled in the main loop
  objects = sl.Objects()
  image = sl.Mat()

  # Window to smooth skeleton movement (non-functional)
  # window = []

  # Windows for left and right wrists. Filter will only work with one object (person)
  left_window = []
  right_window = []

  with open(filename[:-4] + ".txt", 'w') as file:
    interval_time = time.time()
    while viewer.is_available():
      #if not initialized_vectors > 5:
      #  input("Press Enter for sampling location of %s" % vectors[initialized_vectors])  # wait for input of vector initialization
      # get unix_time of received image
      unix_time = time.time()

      # Grab an image
      if zed.grab() == sl.ERROR_CODE.SUCCESS and unix_time - interval_time > 0.01:
        """
        Retrieving an Image
        zed.retrieve_image(image, sl.VIEW, sl.MEM.CPU, display_resolution)
        image: image object from zed2
        sl.VIEW: LEFT, RIGHT, SIDE_BY_SIDE, UNRECTIFIED
        """

        zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, display_resolution)

        # Retrieve objects
        zed.retrieve_objects(objects, obj_runtime_param)

        # Update GL view
        viewer.update_view(image, objects)
        # Update OCV view
        image_left_ocv = image.get_data()

        # Bypass non-functional filter
        image_to_show = image_left_ocv

        # Non-functional filter
        '''# Update window
        window.append(image_left_ocv)

        # Change this value to shorten or lengthen the moving window
        # Currently only works as a delay and does not properly filter
        # Need to sort only using the part of the image that the hand/wrist is in. window.sort() sorts entire image
        if len(window) > 1:
          window.pop(0)

        # Grab median image
        image_to_show = window[int(len(window) / 2)]'''

        cv_viewer.render_2D(image_to_show, image_scale, objects.object_list, obj_param.enable_tracking,
                            obj_param.body_format)

        # Rectangle to hold unix time
        # cv2.rectangle(image_to_show, (0, 0), (700, 25), (255, 255, 255), -1)

        if objects.is_new:
          # Count the number of objects detected
          obj_array = objects.object_list

          if len(obj_array) > 0:
            for object in objects.object_list:
              file.write("{},".format(unix_time))

              # Get wrist keypoints
              left_wrist = object.keypoint[16]
              right_wrist = object.keypoint[17]

              # Add to window
              left_window.append(left_wrist)
              right_window.append(right_wrist)

              # Variable for window length. Must be >= 2
              window_length = 5
              median_index = int(len(left_window) / 2)

              # Enforce window length
              if len(left_window) > window_length:
                left_window.pop(0)
              if len(right_window) > window_length:
                right_window.pop(0)

              # Calculate magnitudes of arrays
              lw_mag = [np.linalg.norm(coord) for coord in left_window]
              rw_mag = [np.linalg.norm(coord) for coord in right_window]

              # Argsort; median of this is the index of the median value in the window
              lw_sorted = np.argsort(np.array(lw_mag))# list(np.sort(np.array(left_window)))
              rw_sorted = np.argsort(np.array(rw_mag))# list(np.sort(np.array(right_window)))

              # Replace current keypoint with median value
              object.keypoint[16] = left_window[lw_sorted[median_index]]
              object.keypoint[17] = right_window[rw_sorted[median_index]]

              for keypoint in analyzed_keypoints:
                point = object.keypoint[keypoint]
                # Writing to just this point at the moment
                file.write("{},{},{}".format(object.keypoint[keypoint][0],
                                             object.keypoint[keypoint][1],
                                             object.keypoint[keypoint][2]))

                # Display skeleton coordinates
                '''if keyboard.is_pressed("c"):
                  # Calculation of point coordinate
                  u_screen = int(display_resolution.width - 100 - (
                            ((point[0] / point[2]) * left_cam.fx + left_cam.cx) * image_scale[0]))
                  v_screen = int(((point[1] / point[2]) * left_cam.fy + left_cam.cy) * image_scale[1]) - 10

                  # Draw Image
                  bottomLeftCornerOfText = (u_screen, v_screen)
                  font = cv2.FONT_HERSHEY_PLAIN
                  fontScale = 2
                  thickness = 2
                  lineType = 2
                  cv2.putText(image_left_ocv,
                              '{:.4f},{:.4f},{:.3f}'.format(point[0], point[1], point[2]),
                              bottomLeftCornerOfText,
                              font,
                              fontScale,
                              (0, 100, 255),
                              thickness,
                              lineType)'''

              file.write("\n")

        # Incompatible with image flipping
        """cv2.putText(image_to_show,
                    'UNIX TIME {}'.format(unix_time),
                    (10, 25),
                    cv2.FONT_HERSHEY_PLAIN,
                    1.5,
                    (0, 0, 0),
                    2,
                    3)"""

        # Flip image horizontally
        image_to_show = np.flip(image_to_show, axis=1)

        cv2.imshow("ZED | 2D View", image_to_show)
        cv2.waitKey(10)
      elif zed.grab() == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
        print("SVO end has been reached. Looping back to first frame")
        zed.set_svo_position(0)

  print("\nConfidence threshold: {0}".format(zed.get_runtime_parameters().confidence_threshold))
  print("Depth min and max range values: {0}, {1}".format(zed.get_init_parameters().depth_minimum_distance,
                                                          zed.get_init_parameters().depth_maximum_distance))
  print("Frame count: {0}.\n".format(zed.get_svo_number_of_frames()))

  viewer.exit()

  image.free(sl.MEM.CPU)
  # Disable modules and close camera

  zed.disable_object_detection()
  # zed.disable_positional_tracking("lab_room.area")
  zed.close()
