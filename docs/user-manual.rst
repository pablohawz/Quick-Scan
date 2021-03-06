User Manual
*********************

Introduction
================

This is the Operation Manual for Quick Scan. Here you will find detailed information 
about all the features and functions in the program.

Platform-Independent Documentation
-----------------------------------------

The documentation applies to the operating systems Windows and macOS.
Features and settings that are specific to one of these platforms are clearly indicated. In all other 
cases, the descriptions and procedures in the documentation are valid for Windows and macOS.
One point to consider:
- The screenshots are taken from Windows.

Set-up
================

For this utility to work you will need the following:

- A camara (or web-cam)
- A microphone

Also, you need to ensure to have their drivers properly set up before initializing the application.

Loading / Creating a project
================================

To create a project you will need to (in no-particular order):

- chose a location for it
- give it a name
- set up the drivers and devices you want to use for data acquisition
- Choose the range to perform the **spectrum analysis**

From the same screen you can open a project, just navigate to its folder, and load the `.pro` file.

** Frequency range influences the minimum time of recording per cell in the **Grid System**.

Calibrating the Equipment
================================

Microphone
--------------------

If you use an external audio interface, ensure the gain is set up properly, following the guidelines from each manufacturer. If you decide to connect the microphone directly to the jack in the PC or through the USB, ensure, through the driver that the input signal is at healthy levels.

Camera
--------------------

Camera-wise, you will only need to white-balance the image, if the camera allows for it. To prove optimal image quality, use artificial light if natural is not available or scarce.

Data Acquisition
================================

For this step, you will have to do the following:

1. Prepare the camera and set up the grid system.
2. Take the picture pressing the button. This is a mandatory step, if not, the results can not be displayed on top  of the picture.
3. Press "Start" to start the recording process, indicated by a small red circle on the upper-left corner of the image.
    1. The grid will turn red and whenever the microphone is in one cell, it will slowly turn blue, to indicate that the minimum recording time is completed.
    2. When all cells are completed, the "Stop" button will activate and you can display the results.

Results Screen
================================

In this screen you will be able to see the sound pressure map per frequency range, the frequency response per cell and the project information
If you press the **dropdown menu** bellow the image, you can select any of the 1/3 octave filters to represent the sound pressure map in that frequency range.
If you press in any cell, the spectrum analysis will change to that cell's analysis.