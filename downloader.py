import logging
import requests
import threading
import wx

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Downloader(threading.Thread):
    """
    A Thread worker for handling file downloads in the background for wxPython.
    Communicates back to the main thread using wx.CallAfter.
    """
    def __init__(self, parent_window, url, save_path):
        """
        Initializes the downloader thread.

        Args:
            parent_window: The wx.Frame to send events back to.
            url (str): The URL of the file to download.
            save_path (str): The local path to save the file to.
        """
        super().__init__()
        self.parent_window = parent_window
        self.url = url
        self.save_path = save_path

    def run(self):
        """The main logic of the thread."""
        try:
            if not self.url:
                raise ValueError("Download URL is missing.")

            logging.info(f"Starting download from {self.url} to {self.save_path}")

            with requests.Session() as s:
                response = s.get(self.url, stream=True, timeout=20)
                response.raise_for_status()

                with open(self.save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            logging.info(f"Download finished successfully: {self.save_path}")
            message = f"Episode saved successfully to:\n{self.save_path}"
            wx.CallAfter(self.parent_window.on_download_finished, message, "success")

        except requests.RequestException as e:
            logging.error(f"Download failed for {self.url}: {e}")
            message = f"Download failed: {e}"
            wx.CallAfter(self.parent_window.on_download_finished, message, "error")
        except Exception as e:
            logging.error(f"An unexpected error occurred during download of {self.url}: {e}")
            message = f"An unexpected error occurred: {e}"
            wx.CallAfter(self.parent_window.on_download_finished, message, "error")
