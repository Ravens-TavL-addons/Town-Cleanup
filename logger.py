# ===================================
# Logger for the Town Cleanup addon
# ===================================


import os
import threading


class TownCleanupLogger:
    
    def __init__(self):
        self.init()

    def init(self):
        self._log_file = "Town_Cleanup.log"
        self._log_lock = threading.Lock()
        self.path = self.set_path()

        ## clear the log file on startup
        with self._log_lock:
            with open(self.path, "w", encoding="utf-8") as log_file:
                pass  # Just open and close to clear the file

        self._log("Town Cleanup Logger initialized.")


        

    def _log(self,message):
        with self._log_lock:
            with open(self.path, "a", encoding="utf-8") as log_file:
                log_file.write(f"{message}\n")

    def _new_line(self):
        with self._log_lock:
            with open(self.path, "a", encoding="utf-8") as log_file:
                log_file.write("==================================\n")

    def set_path(self):
        base = os.environ.get("APPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Roaming"))
        path = os.path.join(base, "TheModdingTavern")
        try:
            os.makedirs(path, exist_ok=True)
        except Exception:
            pass
        return os.path.join(path,self._log_file)
    

    
