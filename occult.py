import wx
from os import path
from pygame import font, image, surface

class ClockFrame(wx.Frame):
    """
    The frame responsible for displaying the actual clock.

    Reshapes its borders to fit the edges of the clock text image each redraw.
    """
    def __init__(self, parent):
        self.default_style = wx.FRAME_SHAPED | wx.SIMPLE_BORDER
        style = self.default_style
        if defaults["aot"]:
            style = self.default_style | wx.STAY_ON_TOP

        wx.Frame.__init__(self, parent, -1, "OCCult Countdown Clock",
                style = style )
        self.hasShape = False
        self.delta = wx.Point(0,0)

        # Instantiate class members, suck in sane defaults
        self.parent = parent
        self.time = defaults["sec"]
        self.paused = True
        self.color = defaults["clockcolor"]
        self.bgcolor = defaults["bgcolor"]
        self.text_font = defaults["font"]
        self.text_size = defaults["size"]
        self.mask = defaults["mask"]
        self.aot = defaults["aot"]
        self.countup = defaults["countup"]

        # The pygame font object
        self.font = None

        # A background surface to paint text onto. Stored for faster access
        self.bgsurf = None

        # Event bindings to catch clicks and redraws
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_WINDOW_CREATE, self.SetWindowShape)

        # Run self.OnTimer every 1 second
        self.timer = wx.Timer(self, -1)
        self.timer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

    def redraw_background(self, img_size):
        """
        Re-generate the background surface, in the event that the needed
        background size, or color, changes.
        """
        self.bgsurf = surface.Surface(img_size)
        self.bgsurf.fill(self.bgcolor)        

    def SetOptions(self, sec=None, color=None, bgcolor=None, text_font=None,
                   text_size=None, mask=None, aot=None, countup=None):
        """
        Change options stored as instance variables, and do immediate logic
        needed to make those changes take effect before the next redraw.
        """
        if sec is not None:
            self.time = sec

        if color is not None:
            self.color = color

        if bgcolor is not None:
            if bgcolor != self.bgcolor:
                self.bgcolor = bgcolor

                # If our bgcolor has changed, redraw the background surface
                self.redraw_background(self.bgsurf.get_size())

        if text_font is not None or text_size is not None or self.font is None:
            if text_font is None:
                text_font = self.text_font
            else:
                self.text_font = text_font
            if text_size is None:
                text_size = self.text_size
            else:
                self.text_size = text_size

            self.font = load_font(text_font, text_size)

        if mask is not None:
            self.mask = mask

        if aot is not None and aot != self.aot:
            self.aot = aot
            style = self.default_style
            if aot:
                style = style | wx.STAY_ON_TOP

            self.SetWindowStyle(style)

        if countup is not None:
            self.countup = countup

        # Update the image to force new settings to take effect
        self.SetImage(self.time, self.color, self.mask)

    def SetImage(self, sec, color, mask):
        # Split the seconds up into d/h/m/s
        timelist = []
        timelist.append("%02d" % (sec / 86400))
        sec = sec % 86400
        timelist.append("%02d" % (sec / 3600))
        sec = sec % 3600
        timelist.append("%02d" % (sec / 60))
        sec = sec % 60
        timelist.append("%02d" % sec)

        # Pop left-hand 0's until just m/s are left, if < 1hr
        while timelist[0] == "00" and len(timelist) > 2:
            timelist.pop(0)

        # Turn that into a single string and render it
        text = ':'.join(timelist)
        text = self.font.render(text, 0, color, self.bgcolor)

        # Make sure our background surface is big enough. Grow it if not
        img_size = text.get_size()
        if self.bgsurf is None:
            self.redraw_background(img_size)
        else:
            bgsurf_size = self.bgsurf.get_size()
            if bgsurf_size[0] < img_size[0] or bgsurf_size[1] < img_size[1]:
                self.redraw_background(img_size)

        # Figure out where to blit text to background so it's centerprinted
        bgsurf_size = self.bgsurf.get_size()
        justify = (bgsurf_size[0] - img_size[0]) / 2

        # Blank our background, blit text
        self.bgsurf.fill(self.bgcolor)
        self.bgsurf.blit(text, (justify, 0))

        # Create the wx surface and load in the pygame surface's image_string
        image_string = image.tostring(self.bgsurf, "RGB")
        surf = wx.EmptyImage(*bgsurf_size)
        surf.SetData(image_string)
        surf.SetMaskColour(*self.bgcolor)
        surf.SetMask(mask) 
        self.bmp = surf.ConvertToBitmap()         

        # Shrink window and shape around image
        self.SetClientSize((self.bmp.GetWidth(), self.bmp.GetHeight()))
        self.SetWindowShape()
        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.bmp, 0,0, True)

    def SetWindowShape(self, evt=None):
        r = wx.RegionFromBitmap(self.bmp)
        self.hasShape = self.SetShape(r)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0,0, True)

    def OnExit(self, evt):
        self.Close()

    def OnLeftDown(self, evt):
        """
        Allow for dragging of the clock around the screen via the LMB.
        """
        self.CaptureMouse()
        pos = self.ClientToScreen(evt.GetPosition())
        origin = self.GetPosition()
        self.delta = wx.Point(pos.x - origin.x, pos.y - origin.y)

    def OnMouseMove(self, evt):
        """
        Move the clock during a LMB drag by checking if we're dragging and
        then moving the clock to the mouse's new location.
        """
        if evt.Dragging() and evt.LeftIsDown():
            pos = self.ClientToScreen(evt.GetPosition())
            newPos = (pos.x - self.delta.x, pos.y - self.delta.y)
            self.Move(newPos)

    def OnLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnTimer(self, evt):
        """
        Timer set to tick every 1000ms. Tick clock by 1 second unless we're
        paused.
        """
        if not self.paused:
            self.time += 1 if self.countup else -1
            if self.time < 0:
                self.time = 0

            self.SetImage(self.time, self.color, self.mask)

class ControlFrame(wx.Frame):
    """
    Control widget for the clock: displays all of the configurable options and
    allows for immediate import or export of time and settings to and from the
    clock frame.
    """
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "OCCult Clock Control",
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX ^
                          wx.RESIZE_BORDER)

        # Storage of our child widget (the clock itself)
        self.child = None

        # One panel for the control frame.
        # TAB_TRAVERSAL to allow tabbing between fields
        pan = wx.Panel(self, style=wx.TAB_TRAVERSAL)

        # H/M/S inputs
        self.hr = wx.SpinCtrl(pan, -1, min=0, max=999, size=(50, 20),
                              style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS |
                              wx.SP_WRAP)
        self.min = wx.SpinCtrl(pan, -1, min=0, max=59, size=(50, 20),
                               style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS |
                               wx.SP_WRAP)
        self.sec = wx.SpinCtrl(pan, -1, min=0, max=59, size=(50, 20),
                               style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS |
                               wx.SP_WRAP)

        self.hr.SetValue(defaults["hr"])
        self.min.SetValue(defaults["min"])
        self.sec.SetValue(defaults["sec"])

        # Clock R/G/B inputs
        self.r = wx.SpinCtrl(pan, -1, min=0, max=255, size=(50, 20),
                             style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS |
                             wx.SP_WRAP)
        self.g = wx.SpinCtrl(pan, -1, min=0, max=255, size=(50, 20),
                             style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS |
                             wx.SP_WRAP)
        self.b = wx.SpinCtrl(pan, -1, min=0, max=255, size=(50, 20),
                             style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS |
                             wx.SP_WRAP)

        self.r.SetValue(defaults["clockcolor"][0])
        self.g.SetValue(defaults["clockcolor"][1])
        self.b.SetValue(defaults["clockcolor"][2])

        # Background R/G/B inputs
        self.br = wx.SpinCtrl(pan, -1, min=0, max=255, size=(50, 20),
                              style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS |
                              wx.SP_WRAP)
        self.bg = wx.SpinCtrl(pan, -1, min=0, max=255, size=(50, 20),
                              style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS |
                              wx.SP_WRAP)
        self.bb = wx.SpinCtrl(pan, -1, min=0, max=255, size=(50, 20),
                              style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS | 
                              wx.SP_WRAP)

        self.br.SetValue(defaults["bgcolor"][0])
        self.bg.SetValue(defaults["bgcolor"][1])
        self.bb.SetValue(defaults["bgcolor"][2])        

        # Font input
        self.f = wx.TextCtrl(pan, -1, style=wx.TE_PROCESS_ENTER)
        self.f.write(defaults["font"])

        self.fs = wx.SpinCtrl(pan, -1, min=0, max=4096, size=(50, 20),
                              style=wx.TE_PROCESS_ENTER | wx.SP_ARROW_KEYS |
                              wx.SP_WRAP )
        self.fs.SetValue(defaults["size"])

        # Mask checkbox
        self.mask = wx.CheckBox(pan, -1)
        self.mask.SetValue(False if defaults["mask"] else True)

        # Always on top checkbox
        self.aot = wx.CheckBox(pan, -1)
        self.aot.SetValue(defaults["aot"])

        # Count up checkbox
        self.countup = wx.CheckBox(pan, -1)
        self.countup.SetValue(defaults["countup"])

        # Set, pause, and get buttons
        self.set = wx.Button(pan,-1, label="Set")
        self.get = wx.Button(pan, -1, label="Get")
        self.pause = wx.Button(pan, -1, label="Start")

        for control in (self.hr, self.min, self.sec, self.r,
                        self.g, self.b, self.br, self.bg, self.bb,
                        self.f, self.fs):
            self.Bind(wx.EVT_TEXT_ENTER, self.OnSetButton, control)

        # Create binds for the three control buttons
        self.Bind(wx.EVT_BUTTON, self.OnSetButton, self.set)
        self.Bind(wx.EVT_BUTTON, self.OnPauseButton, self.pause)
        self.Bind(wx.EVT_BUTTON, self.OnGetButton, self.get)

        # Begin widget packing

        # Sizers for each group of elements
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        hms_sizer = wx.BoxSizer(wx.HORIZONTAL)
        rgb_sizer = wx.BoxSizer(wx.HORIZONTAL)
        brgb_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font_sizer = wx.BoxSizer(wx.HORIZONTAL)

        options_sizer = wx.GridBagSizer()

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Fill the bottom level sizers with widgets
        hms_sizer.AddMany([(self.hr, 0, wx.ALL),
                           (self.min, 0, wx.ALL),
                           (self.sec, 0, wx.ALL)
                           ])

        rgb_sizer.AddMany([(self.r, 0, wx.ALL),
                           (self.g, 0, wx.ALL),
                           (self.b, 0, wx.ALL)
                           ])

        brgb_sizer.AddMany([(self.br, 0, wx.ALL),
                            (self.bg, 0, wx.ALL),
                            (self.bb, 0, wx.ALL)
                            ])

        font_sizer.AddMany([(self.f, 0, wx.ALL),
                            (self.fs, 0, wx.ALL)
                            ])

        options_sizer.AddMany([(self.mask, (0, 0)),
                               (wx.StaticText(pan, label="Show Background"),
                                              (0, 1)),
                               (self.aot, (1, 0)),
                               (wx.StaticText(pan, label="Always On Top"),
                                              (1, 1)),
                               (self.countup, (2, 0)),
                               (wx.StaticText(pan, label="Count Up"), (2, 1))
                               ])

        buttons_sizer.AddMany([(self.set, 0, wx.ALIGN_BOTTOM),
                               (self.get, 0, wx.ALIGN_BOTTOM),
                               (self.pause, 0, wx.ALIGN_BOTTOM)
                               ])

        # Stuff the above sizers into one of two sizers
        left_sizer.AddMany([(wx.StaticText(pan, label="Clock Time (hr/min/sec)"),
                                           1, wx.EXPAND),
                            (hms_sizer, 1, wx.EXPAND),
                            (wx.StaticText(pan, label="Clock Color (r/g/b)"),
                                           1, wx.EXPAND),
                            (rgb_sizer, 1, wx.EXPAND),
                            (wx.StaticText(pan, label="Background Color (r/g/b)"),
                                           1, wx.EXPAND),
                            (brgb_sizer, 1, wx.EXPAND),                            
                            (wx.StaticText(pan, label="Font"), 1, wx.EXPAND),
                            (font_sizer, 1, wx.EXPAND)
                            ])

        right_sizer.AddMany([(options_sizer, 1, wx.EXPAND),
                             (buttons_sizer, 1, wx.ALIGN_BOTTOM)
                             ])

        # Arrange those two sizers side by side in the panel
        main_sizer.AddMany([(left_sizer, 0, wx.RIGHT, 10),
                            (right_sizer, 1, wx.EXPAND)
                            ])

        # Size the panel, fit the window to the panel
        pan.SetSizerAndFit(main_sizer)
        self.Fit()
        self.Centre()

    def OnSetButton(self, evt):
        # Grab all of the settings from the control frame
        h = self.hr.GetValue()
        m = self.min.GetValue()
        s = self.sec.GetValue()

        r = self.r.GetValue()
        g = self.g.GetValue()
        b = self.b.GetValue()

        br = self.br.GetValue()
        bg = self.bg.GetValue()
        bb = self.bb.GetValue()

        font = self.f.GetValue()

        # If the font box is empty, set it to None so we don't clobber our font
        if font == "":
            font = None

        # If our font size isn't an int, set it to None
        try:
            font_size = int(self.fs.GetValue())
        except:
            font_size = None

        # Checkbox boolean values
        mask = False if self.mask.GetValue() else True
        aot = self.aot.GetValue()
        countup = self.countup.GetValue()

        # Turn h/m/s into seconds
        total = 0
        try:
            total += int(h) * 3600
        except:
            pass

        try:
            total += int(m) * 60
        except:
            pass

        try:
            total += int(s)
        except:
            pass            

        # If r/g/b inputs aren't ints, zero them
        # While we're at it, make sure they somehow don't exceed 255
        try:
            r = int(r) % 256
        except:
            r = 0

        try:
            g = int(g) % 256
        except:
            g = 0

        try:
            b = int(b) % 256
        except:
            b = 0

        # Create our clock frame if it's non-existent
        if self.child is None:
            self.child = ClockFrame(self)
            self.child.SetOptions()
            self.child.Show()

        # Set appropriate options
        self.child.SetOptions(total, (r, g, b), (br, bg, bb), font,
                              font_size, mask, aot, countup)

        # Grab what we just set back into the text inputs
        # This makes sure assumed defaults get populated back into the controls
        self.OnGetButton(None)

        # Force the child (clock) image to update
        self.child.SetImage(total, (r, g, b), mask)

    def OnPauseButton(self, evt):
        # Create a clock frame with some defaults if no clock frame exists
        if self.child is None:
            self.child = ClockFrame(self)
            self.child.SetOptions()
            self.child.Show()

            # Grab our defaults into the text inputs
            self.OnGetButton(None)

        # Flip paused status on button and clock frame
        self.child.paused = False if self.child.paused else True
        self.pause.Label = "Resume" if self.child.paused else "Pause"

    def OnGetButton(self, evt):
        # If we don't have a clock frame, do nothing
        if self.child is None:
            return False

        # Grab all the settings from the clock frame
        time = self.child.time
        r, g, b = self.child.color
        br, bg, bb = self.child.bgcolor

        f = self.child.text_font
        fs = self.child.text_size

        # Split seconds out into h/m/s
        h = time / 3600
        time = time % 3600
        m = time / 60
        time = time % 60
        s = time

        # Clear our string input fields
        self.f.Clear()

        # Place data in input fields
        self.hr.SetValue(h)
        self.min.SetValue(m)
        self.sec.SetValue(s)
        self.r.SetValue(r)
        self.g.SetValue(g)
        self.b.SetValue(b)
        self.br.SetValue(br)
        self.bg.SetValue(bg)
        self.bb.SetValue(bb)        
        self.f.write(str(f))
        self.fs.SetValue(fs)

        self.mask.SetValue(False if self.child.mask else True)
        self.aot.SetValue(self.child.aot)
        self.countup.SetValue(self.child.countup)

def load_font(font_name, font_size):
    """
    Attempt to load a font of the given name and size. Attempt in this order:

    1.) Attempt to load a font of the given name from the PWD
    2.) Append .ttf to the end and try again, if the name doesn't end in .ttf
    3.) Attempt to return a system font
    4.) Panic and return the system font "Sans", which should exist

    This is made complex by pyinstaller's propensity to make created EXEs crash
    when calling SysFont(), presumably due to not bundling Pygame's default
    font into the EXE properly.
    """
    try:
        # Try to just find the font in PWD
        return font.Font(font_name, font_size)
    except IOError:
        # If that failed, try it with .ttf appended
        if not font_name.endswith(".ttf"):
            try:
                return font.Font(font_name+".ttf", font_size)
            except IOError:
                pass
                
    # If that failed, try to find it in system fonts
    filename = font.match_font(font_name)
    if filename is not None:
        return font.Font(filename, font_size)
    else:
        # If all else fails, panic and use "Sans" as a last resort
        return font.SysFont("Sans", font_size)

# A bunch of default settings
# TODO: Replace with loading options from a config file
defaults = {
    "hr": 0,
    "min": 1,
    "sec": 0,
    "clockcolor": (255, 255, 255),
    "bgcolor": (255, 0, 255),
    "font": "Sans",
    "size": 256,
    "mask": True,
    "aot": False,
    "countup": False
}

if __name__ == '__main__':
    # Initialize pygame's font module
    font.init()

    # Stand up the wxPython app and display our control frame
    app = wx.App()
    control = ControlFrame()
    control.Show()
    app.MainLoop()
