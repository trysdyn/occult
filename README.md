occult
======
- Version 0.1.0
- October 13, 2013

Overlay Countdown Clock Utility

A simple utility to display a countdown clock in a number of formats fit for import into livestreams or video projects.

Getting occult
------------------
Github hosts the source for occult, you can check that out at [https://github.com/trysdyn/occult](https://github.com/trysdyn/occult.html). If you plan to run occult from source, please make sure you meet the requirements below.

To get a binary you can run on a Windows system, without needing to meet the source version requirements, please visit [http://www.voidfox.com/projects/occult](http://www.voidfox.com/projects/occult). This binary is pretty hefty, due to needing to bundle the Python runtimes with it; source is recommended if at all possible.

Requirements (source version)
-----------------------------
- Python 2.6+
- Pygame 1.9
- wxPython 2.8

Usage
-----
Launch the utility and you will be presented with the clock control panel. Set the control options to your taste and click "Set" to create the clock. Once ready, click "Start" to actually begin time keeping. Once the clock has been created, you can drag it around the screen with the left mouse button. To exit, close the clock control panel.

Options
-------
The clock control panel is divided into two halves:

### Left Half
- **Clock Time:** Three spinner boxes within which you can define the clock's starting time in hours, minutes, and seconds respectively.
- **Clock Color:** Three spinner boxes within which you define the clock's text color in red, green, and blue respectively.
- **Background Color:** Three spinner boxes within which you define the clock's background color in red, green, and blue respectively. Background is not visible unless "Show Background" is checked.
- **Font:** Font name and size in points to use for the clock. Font name can be provided in one of three manners:
- - A filename of a font in the same directory as the tool (e.g Anton.ttf)
- - An absolute path to a font file on the system (e.g C:\users\trysdyn\desktop\font.ttf)
- - A name of a system font installed on the system (e.g Arial, or Sans, or Serif)

A default font will be provided if the given font cannot be found.

### Right Half
- **Show Background:** If checked, the background around the clock text will be displayed. Having this enabled is required for streaming software that uses chromakey masking. Having this disabled is suggested if you plan to simply drag the clock over the application you are recording.
- **Always On Top:** Toggles whether or not the clock will always appear above other applications. Enabling this is recommended if you are dragging the clock over the application you are recording.
- **Count Up:** If enabled, the clock will count up from the designated Clock Time instead of down.
- **Set** Pushes the settings currently displayed in the control application to the clock, or creates the clock if it has not already been created.
- **Get** Pulls the current time and settings from the clock into the control application.
- **Start** Starts the clock, or pauses it if the clock has already been started, or resumes the clock if the clock has been paused.

Todo
----
- Proper color selection and font file selection controls
- Tidy up the clock redrawing
- Tidy up widget packing into the control frame
- Better in-code documentation
- Generally tidy up the code. One 500 line spaghatti file is going to give people a bad time
- The ability to display text along side the clock
- Defaults defined within a configuration file, instead of hard-coded

Disclaimer
----------
This is the project I used to learn wxPython. It may not be fit for human consumption. Initially this was hacked together in an hour to help a friend who was running a livestream. Only after the hackery did I realize this could be useful to other people. Use at your own risk :)
