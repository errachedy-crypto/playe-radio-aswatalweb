import logging
try:
    import nvdaControllerClient
except (ImportError, OSError):
    nvdaControllerClient = None

class ScreenReaderBridge:
    def __init__(self):
        self.enabled = False
        self.nvda_available = False
        if nvdaControllerClient:
            try:
                # Initialize the client
                nvdaControllerClient.initialize()
                self.nvda_available = True
                logging.info("NVDA controller client initialized successfully.")
            except Exception as e:
                logging.warning(f"Could not initialize NVDA controller: {e}. NVDA might not be running.")
        else:
            logging.warning("nvda-controller-client-python library not found. Screen reader support will be disabled.")

    def set_enabled(self, enabled):
        """Enable or disable screen reader announcements."""
        self.enabled = enabled
        logging.info(f"Screen reader announcements have been {'enabled' if enabled else 'disabled'}.")

    def speak(self, text):
        """
        Speak the given text using the screen reader.
        Returns True on success, False on failure.
        """
        if not self.enabled or not self.nvda_available:
            return False

        try:
            # Cancel any previous speech to avoid overlap
            nvdaControllerClient.cancel()
            nvdaControllerClient.speakText(text)
            logging.debug(f"Sent to screen reader: '{text}'")
            return True
        except Exception as e:
            logging.error(f"Failed to send text to screen reader: {e}")
            return False

    def __del__(self):
        # Uninitialize the client when the object is destroyed
        if self.nvda_available:
            try:
                nvdaControllerClient.terminate()
                logging.info("NVDA controller client terminated.")
            except Exception as e:
                logging.error(f"Error terminating NVDA controller: {e}")
