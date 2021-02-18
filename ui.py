import os
import subprocess
from clip import Clip
import configparser as cp
import wx
import main
from subprocess import PIPE, Popen
import asyncio

cfgFile = open('config.cfg', 'r')
config = cp.ConfigParser()
config.read_file(cfgFile)
cfgParams = config['Params']

class FrameWithForms(wx.Frame):
    '''The main window class'''
    def __init__(self, *args, **kwargs):
        super(FrameWithForms, self).__init__(*args, **kwargs)
        notebook = wx.Notebook(self)
        form = JumpCutCfgPanel(notebook)
        notebook.AddPage(form, 'Settings')

        self.SetClientSize(notebook.GetBestSize())

class JumpCutCfgPanel(wx.Panel):
    ''' The Form class is a wx.Panel that creates a bunch of controls
    and handlers for callbacks. Doing the layout of the controls is
    the responsibility of subclasses (by means of the doLayout()
    method). '''

    def __init__(self, *args, **kwargs):
        super(JumpCutCfgPanel, self).__init__(*args, **kwargs)
        self.createControls()
        self.bindEvents()
        self.doLayout()

    def createControls(self):
        '''create controls'''
        self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.lineDivider = wx.StaticLine(self, -1, size=(10, 2), style=wx.LI_HORIZONTAL)

        self.inputPathLabel = wx.StaticText(self, label="Input Path:")
        self.inputPathFilePickerCtrl = wx.FilePickerCtrl(self, message="Select Input Video", wildcard='*.mp4', path=cfgParams['inputpath'],style=wx.FLP_OPEN|wx.FLP_FILE_MUST_EXIST|wx.FLP_USE_TEXTCTRL)

        self.outputPathLabel = wx.StaticText(self, label="Output Path:")
        self.outputPathFilePickerCtrl = wx.FilePickerCtrl(self, message="Select Output Video", path=cfgParams['outputpath'], style=wx.FLP_SAVE|wx.FLP_OVERWRITE_PROMPT|wx.FLP_USE_TEXTCTRL)

        self.magnitudeThresholdRatioLabel = wx.StaticText(self, label="magnitude-threshold-ratio:")
        self.magnitudeThresholdRatioSpinCtrl = wx.SpinCtrlDouble(self, value=cfgParams['magnitude-threshold-ratio'], inc = 0.01)

        self.processButton = wx.Button(self, label="Jump Cut!")

    def bindEvents(self):
        '''bind controls to events to fuctions'''
        for control, event, handler in \
            [(self.processButton, wx.EVT_BUTTON, self.onSave),
            ]: control.Bind(event, handler)

    def doLayout(self):
        ''' Layout the controls by means of sizers. '''

        # A horizontal BoxSizer will contain the GridSizers (on the Top)
        # and the logger text control (on the bottom):
        boxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        # A GridSizer will contain the other controls:

        gridSizerPaths = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        gridSizerLine = wx.FlexGridSizer(rows=1, cols=1, vgap=20, hgap=10)

        gridSizerArguments = wx.FlexGridSizer(rows=7, cols=3, vgap=10, hgap=10)
        

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND, proportion=1)
        textOptions = dict(flag=wx.ALIGN_RIGHT)
        emptySpace = ((0, 0), textOptions)

        # Add the controls to the sizers:
        # - Paths:
        for control, options in \
                [(self.inputPathLabel, textOptions),
                 (self.inputPathFilePickerCtrl, expandOption),
                 (self.outputPathLabel, textOptions),
                 (self.outputPathFilePickerCtrl, expandOption)]:
            gridSizerPaths.Add(control, **options)

        gridSizerPaths.SetFlexibleDirection(0)
        gridSizerPaths.SetNonFlexibleGrowMode(1)
        gridSizerPaths.AddGrowableCol(1, proportion=0)

        # - divider line
        for control, options in \
            [(self.lineDivider, expandOption),
            ]:
            gridSizerLine.Add(control, **options)
        gridSizerLine.SetFlexibleDirection(0)
        gridSizerLine.SetNonFlexibleGrowMode(1)
        gridSizerLine.AddGrowableCol(0, proportion=0)

        # paramaters
        for control, options in \
                [(self.magnitudeThresholdRatioLabel, textOptions),
                 (self.magnitudeThresholdRatioSpinCtrl, expandOption)]:
            gridSizerArguments.Add(control, **options)

        gridSizerArguments.SetFlexibleDirection(0)
        gridSizerArguments.SetNonFlexibleGrowMode(1)
        gridSizerArguments.AddGrowableCol(1, proportion=0)

        ##Box Sizer
        for control, options in \
                [(gridSizerPaths, dict(border=5, flag=wx.ALL|wx.EXPAND, proportion=0)),
                 (gridSizerLine, dict(border=5, flag=wx.ALL|wx.EXPAND, proportion=0)),
                 (gridSizerArguments, dict(border=5, flag=wx.ALL|wx.EXPAND, proportion=0)),
                 (gridSizerLine, dict(border=5, flag=wx.ALL|wx.EXPAND, proportion=0)),
                 (self.processButton, dict(border=5, flag=wx.ALL|wx.EXPAND, proportion=0)),
                 (self.logger, dict(border=5, flag=wx.ALL|wx.EXPAND, proportion=1))
                ]:
            boxSizer.Add(control, **options)

        self.SetSizerAndFit(boxSizer)

    # Callback methods:

    def onSave(self, event):
        '''saves settings to the config file'''
        #check if paths have changed then save.
        self.processButton.Disable();

        self.__log('Saving Settings...')
        
        #('option', self.element.Get()),
        for item, val in \
                [('inputpath', self.inputPathFilePickerCtrl.GetPath()),
                 ('outputpath', self.outputPathFilePickerCtrl.GetPath()),
                 ('magnitude-threshold-ratio', str(self.magnitudeThresholdRatioSpinCtrl.GetValue()))
                ]:
            config['Params'][item] = val

        config.write(open('config.cfg', 'w+'))
        self.__log('Settings Saved')
        self.__log('Processing Video')
        
        #os.system('python main.py --input ' + str(self.inputPathFilePickerCtrl.GetPath()) +
        #    ' --output ' + str(self.outputPathFilePickerCtrl.GetPath()) + 
        #    ' --magnitude-threshold-ratio ' + str(self.magnitudeThresholdRatioSpinCtrl.GetValue()))

        process = subprocess.Popen(["python", "-u", "main.py", "--input", str(self.inputPathFilePickerCtrl.GetPath()),
                        "--output", str(self.outputPathFilePickerCtrl.GetPath()),
                        "--magnitude-threshold-ratio", str(self.magnitudeThresholdRatioSpinCtrl.GetValue())
         ], stdout=PIPE)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                self.__log('Breack')
                break
            if output:
                self.__log( str(output.strip()) )
            asyncio.sleep(5)
        
        self.__log('Video Done!')
        self.processButton.Enable();

    # Helper method(s):

    def __log(self, message):
        ''' Private method to append a string to the logger text
            control. '''
        self.logger.AppendText('%s\n'%message)

if __name__ == '__main__':
    app = wx.App(0)
    frame = FrameWithForms(None, title='Auto Jump Cut Panel')
    frame.Show()
    app.MainLoop()