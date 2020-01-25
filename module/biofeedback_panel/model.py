#!/usr/bin/env python3

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty
from pyqtgraph import LinearRegionItem
import FieldTrip
import time


class Model(QObject):
    
    # Costum signals.
    psd_changed = pyqtSignal(object)
    biofeedback_changed = pyqtSignal(object)

    # The following model attributes are set by the controller.
    ###########################################################
    
    @property
    def psd(self):
        return self._psd
    
    @psd.setter
    def psd(self, value):
        self._psd = value
        self.psd_changed.emit(value)
    
    @property
    def freqs(self):
        return self._freqs
    
    @freqs.setter
    def freqs(self, value):
        self._freqs = value
        
    @property
    def rewardratio(self):
        return self._rewardratio
    
    @rewardratio.setter
    def rewardratio(self, value):
        self._rewardratio = value
        
    @property
    def biofeedback(self):
        return self._biofeedback
    
    @biofeedback.setter
    def biofeedback(self, value):
        self._biofeedback = value
        # Emit both the x-coordinate (rewardratio) and y-coordinate
        # (biofeedback) for the view's biofeedback plot.
        self.biofeedback_changed.emit([self._rewardratio, value])
        
    # The following model attributes are set directly by the view.
    ##############################################################    
       
    @pyqtProperty(float)
    def biofeedbacktarget(self):
        return self._biofeedbacktarget
    
    @pyqtSlot(float)
    def set_biofeedbacktarget(self, value):
        self._biofeedbacktarget = value
        
    @pyqtProperty(str)
    def biofeedbackmapping(self):
        return self._biofeedbackmapping
    
    @pyqtSlot(str)
    def set_biofeedbackmapping(self, value):
        self._biofeedbackmapping = value
        
    @pyqtProperty(object)
    def lowreward(self):
        return self._lowreward
    
    @pyqtSlot(object)
    def set_lowreward(self, value):
        if isinstance(value, type(LinearRegionItem())):
            value = value.getRegion()[0]
            if value != self._lowreward:
                self._lowreward = value
        else:
            self._lowreward = value
        
    @pyqtProperty(object)
    def upreward(self):
        return self._upreward
    
    @pyqtSlot(object)
    def set_upreward(self, value):
        if isinstance(value, type(LinearRegionItem())):
            value = value.getRegion()[1]
            if value != self._upreward:
                self._upreward = value
        else:
            self._upreward = value
        
    @pyqtProperty(object)
    def lowtotal(self):
        return self._lowtotal
    
    @pyqtSlot(object)
    def set_lowtotal(self, value):
        self._lowtotal = value
        
    @pyqtProperty(object)
    def uptotal(self):
        return self._uptotal
    
    @pyqtSlot(object)
    def set_uptotal(self, value):
        self._uptotal = value
        
    @pyqtProperty(int)
    def window(self):
        return self._window
    
    @pyqtSlot(int)
    def set_window(self, value):
        self._window = value
        
    @pyqtProperty(int)
    def channel(self):
        return self._channel
    
    @pyqtSlot(int)
    def set_channel(self, value):
        self._channel = value
    
    @pyqtProperty(str)
    def fthost(self):
        return self._fthost
    
    @pyqtSlot(str)
    def set_fthost(self, value):
        self._fthost = value
        
    @pyqtProperty(int)
    def ftport(self):
        return self._ftport
    
    @pyqtSlot(int)
    def set_ftport(self, value):
        self._ftport = value
        
        
    def __init__(self):
        
        super().__init__()
        
        self._window = 30
        self._channel = 0
        self._fthost = "localhost"
        self._ftport = 1972
        self._psd = None
        self._freqs = None
        self._biofeedback = None
        self._biofeedbackmapping = "exponential"
        self._biofeedbacktarget = 3
        self._rewardratio = None
        self._lowreward = 0.06
        self._upreward = 0.14
        self._lowtotal = 0
        self._uptotal = 0.5
        
        # Instantiate FieldTrip client.
        # Check if the buffer is running.
        try:
            self.ftc = FieldTrip.Client()
            self.ftc.connect(self._fthost, self._ftport)
        except ConnectionRefusedError:
            raise RuntimeError(f"Make sure that a FieldTrip buffer is running "
                               f"on \"{self._fthost}:{self._ftport}\"")
        # Wait until there is enough data in the buffer (note that this blocks
        # the event loop on purpose).
        hdr = self.ftc.getHeader()
        while hdr is None:
            time.sleep(1)
            print("Waiting for header.")
            hdr = self.ftc.getHeader()
        while hdr.nSamples < hdr.fSample * self._window:
            time.sleep(1)
            print("Waiting for sufficient amount of samples.")
            hdr = self.ftc.getHeader()
            