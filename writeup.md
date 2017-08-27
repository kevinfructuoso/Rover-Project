## Project: Search and Sample Return

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./output/non_inverted_img.jpg
[image2]: ./output/inverted_img.jpg
[image3]: ./output/inverted_no_mask.jpg 
[image4]: ./output/inverted_with_mask.jpg
[image5]: ./output/rock_sample_finder.jpg
[image6]: ./output/process_image_video_as_gif.gif
[image7]: ./output/rover_sample.gif

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

In order to identify obstacles, the color_thresh function was extended to receive an 'invert' parameter as an input in order to return the obstacles. It is defaulted to a value of 'False' in order to prevent function errors. If invert is passed a 'True' value, the function will search for all values lower than the passed rgb_thresh.

![alt text][image1]     ![alt text][image2]

A mask was added to the perspect_transform function in order to remove the blank corners of vision from the image after the image is transformed. This was added to prevent the false addition of obstacles to the world map. This is achieved by implementing a 'bit-wise and' operation between the mask and the image transform. The below images show the obstacles in white.

![alt text][image3]     ![alt text][image4]

A new function was defined to determine if an image contains a rock sample. The method is similar to the color_thresh but searches for a hard-coded set of values. Yellow hues have lower blue thresholds and relatively even red and green thresholds. The below image shows a result of the rock sample finder useing the example rock image.

![alt text][image5]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

See sample of results here!

![alt text][image6]

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

See the below .gif and more [here](output).

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

![alt text][image7]

* Simulator Settings:

    * Resolution: 1280 x 720
    * Video Quality: Good
    * Frame Rate: ~20-25 FPS


* Results summary:

    * This rover design will consistently meet the requirements to map 40% at 60% fidelity and locate a sample rock within 5 minutes. This design will typically reach 50-60% of map at 70-80% fidelity in 7 minutes. Additionally, it will pick up any samples it comes across. In certain cases, the rover may become stuck against a rock due to a bug that actaully allows the rover to see through the rock. To obtain these results, the rover uses the methods below. See all attached images, gifs, and extra video content of this rover design in the [output](output) folder.


* Methods:

    * In addition to the vision techniques discussed in the Jupyter notebook, map fidelity was improved by mapping only when the rover was not tilted at more than a 0.5 degree angle in the pitch and roll directions. Rover tilt will distort the mapping transformation from the images and result in a loss of accuracy.

    * When a sample is in view, the rover's steering range is broadened in order to improve response and motion towards the sample. The velocity and brakes scale linearly with distance from the sample in order to smooth out motion towards it.

    * The rover implements five modes of motion - 'forward,' 'stop,' 'right,' 'left,' 'turning around.' The 'forward' motion is for typical driving with open areas to navigate. The 'stop' motion is used when either the rover detects it has no room to move ahead or to situate itself to pick up rock samples. The 'right' and 'left' driving modes are used after a rover has entered the 'stop' mode. Depending on the vision input, the rover will decide to turn either direction until it sees a relatively straight path onward. The 'turning around' driving mode is designed to get the rover unstuck behind or on top of a rock. In this mode, the rover turns in either direction at 60 degrees and then is set to stop mode to reassess it's potential path forward.
    
    * Individual counters were designed to determine if the rover is stuck in two ways - the rover gets stuck behind a rock or is tilted/caught on top of a rock. When either of these situations are detected, the rover enters the 'turning around' mode to attempt to correct the situation.


* Improvements:

    * The below lists out potential improvements to optimize the rover project.
        * faster movement - increase velocity limit and adjust steering as necessary to improve time efficiency
        * increase map fidelity - lower the 'obstacle' color detection thresholds so that it only determines the cliffs and rocks as impassable terrain; terrain that is far away enough may detected as an obstacle
        * better map awareness - set up an algorithm such that the rover does not return to paths already taken
        * pick up all rocks and return to the starting position - if all rocks are located, set up another driving mode to navigate back to the start position
        * NaN errors - improve data handling to eliminate the occasional NaN error that appears when observing the console output
