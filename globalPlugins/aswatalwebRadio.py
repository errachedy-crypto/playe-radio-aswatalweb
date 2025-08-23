# -*- coding: utf-8 -*-

import os
import globalPluginHandler
import scriptHandler
import ui
import addonHandler
from . import pybass

# Initialize addon translations
addonHandler.initTranslation()

# Radio stream URL provided by the user
STREAM_URL = "https://live.aswatalweb.com/listen/live/radio.mp3"

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    """
    A global plugin to play and stop the aswatalweb radio stream.
    """
    # Class variable to hold the BASS handle for the stream. 0 means stopped.
    stream = 0

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        # Attempt to load and initialize the BASS audio library.
        addon_dir = os.path.abspath(os.path.dirname(__file__))
        bass_dll_path = os.path.join(addon_dir, "bass.dll")

        if not os.path.exists(bass_dll_path):
            # Translators: Error message if the bass.dll file is not found.
            ui.message(_("BASS library (bass.dll) not found."))
            return

        try:
            pybass.init(bass_dll_path)
            # Initialize BASS audio output device. -1 means default device.
            if not pybass.BASS_Init(-1, 44100, 0, 0, 0):
                # Translators: Error message when the BASS audio library fails to initialize.
                ui.message(_("Error initializing BASS audio library."))
        except Exception as e:
            # Translators: A generic error message when loading the BASS library fails.
            ui.message(_("Failed to load BASS library."))

    def terminate(self):
        """
        Called when NVDA is exiting. Cleans up BASS resources.
        """
        self.stop() # Ensure the stream is stopped
        pybass.BASS_Free() # Free all BASS resources
        super(GlobalPlugin, self).terminate()

    def play(self):
        """
        Starts playing the radio stream.
        """
        # If a stream handle exists, free it before creating a new one.
        if self.stream != 0:
            pybass.BASS_StreamFree(self.stream)
            self.stream = 0

        # Create a new stream from the URL
        # The URL must be bytes, so we encode it.
        self.stream = pybass.BASS_StreamCreateURL(STREAM_URL.encode('utf-8'), 0, 0, 0, 0)

        if self.stream != 0:
            # Play the stream
            pybass.BASS_ChannelPlay(self.stream, False)
            # Translators: Message announced when the radio starts playing.
            ui.message(_("Radio playing"))
        else:
            # Translators: Error message when the radio stream fails to open.
            ui.message(_("Error opening radio stream"))

    def stop(self):
        """
        Stops the radio stream.
        """
        if self.stream != 0:
            pybass.BASS_StreamFree(self.stream)
            self.stream = 0
            # Translators: Message announced when the radio stops playing.
            ui.message(_("Radio stopped"))

    @scriptHandler.script(
        description=_("Toggles aswatalweb radio playback on and off."),
        # Translators: The name of the script as it appears in the Input Gestures dialog.
        displayName=_("Toggle aswatalweb radio"),
        gesture="kb:control+alt+r"
    )
    def script_toggleRadio(self, gesture):
        """
        This script is bound to a keyboard gesture and toggles the radio on or off.
        """
        if self.stream == 0:
            # Stream is not active, so start it.
            self.play()
        else:
            # Stream exists, check its state.
            state = pybass.BASS_ChannelIsActive(self.stream)
            if state == pybass.BASS_ACTIVE_PLAYING or state == pybass.BASS_ACTIVE_STALLED:
                # It's playing or trying to play (stalled), so stop it.
                self.stop()
            else:
                # It's stopped, paused, or in an error state, so try to (re)start it.
                self.play()
