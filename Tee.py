#!/usr/bin/env python3

"""
Tee all stdout messages to the console and to a log file. 

Gabriel Staples
20 Sep. 2024

Prompt to GitHub Copilot to help: 
> python: tee all stdout output to a file

"""

import os
import sys

# See my answer: https://stackoverflow.com/a/74800814/4561887
FULL_PATH_TO_SCRIPT = os.path.abspath(__file__)
SCRIPT_DIRECTORY = str(os.path.dirname(FULL_PATH_TO_SCRIPT))
# Allow imports from the current directory
sys.path.insert(0, f"{SCRIPT_DIRECTORY}")


# local imports
import eRCaGuy_PyColors.ansi_colors as colors

# 3rd party imports
# NA

# other standard library imports
# NA

def MiB_to_bytes(MiB):
    """
    Convert Mebibytes to bytes.
    """
    bytes = MiB * 1024 * 1024
    return bytes

def bytes_to_MiB(bytes):
    """
    Convert bytes to Mebibytes.
    """
    MiB = bytes / 1024 / 1024
    return MiB

# Constants
MAX_LOGFILE_SIZE_BYTES = MiB_to_bytes(25)

class Tee:
    def __init__(self, *paths, append_lognum=True, immediately_flush=False, redirect_stderr=True,
                 max_logfile_size_bytes=MAX_LOGFILE_SIZE_BYTES):
        """
        Create a Tee object that writes to multiple files, as specified by the paths passed in.

        Args:
        - paths: one or more paths to write to, as an `os.path` path object or string.
        - append_lognum: if True, append a log number to the end of the file name, just before the 
          extension, starting at 1, and incrementing by 1 each time a new file is created by 
          a manual call to `next_logfiles()`. 
            So, if you use `append_lognum=True`, then the log file names as they increment will be
            like this:
            - `my_log_1.log`
            - `my_log_2.log`
            - `my_log_3.log`
            If you use `append_lognum=False`, then the log file names will be like this:
            - `my_log.log`
            - `my_log_1.log`
            - `my_log_2.log`
        - immediately_flush: if True, flush the output to the file immediately after each write
            CAUTION: 
            - Setting `immediately_flush=True` can cause your flash memory to wear faster because of
              how often it has to rewrite the entire file to disk. It is recommended to leave this
              set to its default value of `False` unless you really need to see all data show up in
              the file immediately after each write. 
            - If you leave `immediately_flush=False`, the file still auto-flushes every so often.
              Testing shows it's about every 1m44sec or 8044 bytes written--I'm not sure which
              triggers the auto-flush exactly, as I only tested it briefly to ensure it auto-flushed
              at all, which it **does**. 
                - UPDATE 26 JAN 2025: 
                    1. It appears to be a **byte-triggered** line-buffered auto-flush, triggered
                       every **~8 kB** written.
                    2. Even with `immediately_flush=False`, no data is EVER lost so long as you
                       properly close the file at the end of your program, because then any cached
                       and unwritten data is flushed to disk at that time.
        - redirect_stderr: if True, also redirect stderr to stdout and log stderr to the file(s);
          therefore, you'll be writing both stdout and stderr to the file(s) **and** to the
          console's **stdout**. If False, only stdout is written to the file(s), and stderr keeps
          the default behavior of being written to the console's stderr.
        """

        self.PATHS = paths
        self.append_lognum = append_lognum
        self.immediately_flush = immediately_flush
        self.redirect_stderr = redirect_stderr
        self.max_logfile_size_bytes = max_logfile_size_bytes

    def _get_numbered_path(self, path_original, logfile_number):
        """
        Create a new path from this original path, with this logfile number appended to the end 
        just before the file extension.
        """
        root, ext = os.path.splitext(path_original)
        new_path = f"{root}_{logfile_number}{ext}"
        return new_path

    def begin(self):
        """
        Begin tee-ing stdout to the console and to one or more log files.
        """
        STARTING_LOGNUMBER = 1
    
        # list of all the active log files
        self.logfiles = [None]*len(self.PATHS)
        # list of the current log numbers for each log file
        self.logfile_numbers = [STARTING_LOGNUMBER - 1]*len(self.PATHS)

        # Open all the files for writing
        for i, path in enumerate(self.PATHS):
            if self.append_lognum:
                path = self._get_numbered_path(path, STARTING_LOGNUMBER)
                self.logfile_numbers[i] = STARTING_LOGNUMBER

            os.makedirs(os.path.dirname(path), exist_ok=True)

            logfile = open(path, "w")
            self.logfiles[i] = logfile

        # Save the original stdout, and replace it with the Tee object
        self.stdout_bak = sys.stdout
        sys.stdout = self

        if self.redirect_stderr:
            # Save the original stderr, and replace it with the Tee object
            self.stderr_bak = sys.stderr
            sys.stderr = self

    def next_logfiles(self):
        """
        Check all open log files, and if any are larger than `self.max_logfile_size_bytes`, close
        them and open new log files with incremented log numbers. 
        """
        for i, f in enumerate(self.logfiles):
            # See: https://stackoverflow.com/a/283719/4561887
            file_size_bytes = f.tell()

            if file_size_bytes >= self.max_logfile_size_bytes:
                f.close()

                # Open a new file with the next log number
                self.logfile_numbers[i] += 1
                new_path = self._get_numbered_path(self.PATHS[i], self.logfile_numbers[i])
                self.logfiles[i] = open(new_path, "w")
                
                print(f"Opened new log file at: {new_path}")

    def get_logfile_names(self):
        """
        Get the names of all the log files.
        """
        logfile_names_list = [f.name for f in self.logfiles]
        return logfile_names_list

    def end(self):
        """
        End tee-ing stdout to the console and to one or more log files.
        """
        # Close all the files
        for f in self.logfiles:
            f.close()

        # Restore sys.stdout
        sys.stdout = self.stdout_bak

        if self.redirect_stderr:
            # Restore sys.stderr
            sys.stderr = self.stderr_bak

    def write(self, obj):
        """
        Write to the original stdout 
        - NB: if `self.redirect_stderr` is True, then this will also write/redirect stderr to the
          console's stdout. 
        """

        self.stdout_bak.write(obj)

        # Write to all the log files
        for f in self.logfiles:
            f.write(obj)
            if self.immediately_flush:
                f.flush() # Ensure the output is written immediately

    def flush(self):
        """
        This must be defined or else you get this error:
        ```
        Exception ignored in: <__main__.Tee object at 0x7fbeb88cfb20>
        AttributeError: 'Tee' object has no attribute 'flush'
        ```
        """
        for f in self.logfiles:
            f.flush()

def main():
    MAX_SIZE_BYTES = 10

    logpath = os.path.join(SCRIPT_DIRECTORY, "temp", "tee.log")
    tee = Tee(logpath)                         # default 
    # tee = Tee(logpath, append_lognum=False)  # alternative

    tee.begin()

    logfile_names = tee.get_logfile_names()
    print(f"logfile_names: {logfile_names}")

    # Example usage
    print()
    print("This will be printed to the console and written to the file.")
    print("Another line of output.")
    colors.print_red("This will be printed to the console and written to the file. It is red.")
    print()

    tee.next_logfiles(MAX_SIZE_BYTES)
    logfile_names = tee.get_logfile_names()
    print(f"logfile_names: {logfile_names}")

    tee.next_logfiles(MAX_SIZE_BYTES)
    logfile_names = tee.get_logfile_names()
    print(f"logfile_names: {logfile_names}")

    tee.end()

if __name__ == "__main__":
    main()


"""
Example output:
- this output goes to both the console **and** to the log files



eRCaGuy_Tee$ ./Tee.py 
logfile_names: ['/home/gabrielstaples/GS-p/dev-p/trade_me/trade_me_dev/eRCaGuy_Tee/temp/tee_1.log']

This will be printed to the console and written to the file.
Another line of output.
This will be printed to the console and written to the file. It is red.

logfile_names: ['/home/gabrielstaples/GS-p/dev-p/trade_me/trade_me_dev/eRCaGuy_Tee/temp/tee_2.log']
logfile_names: ['/home/gabrielstaples/GS-p/dev-p/trade_me/trade_me_dev/eRCaGuy_Tee/temp/tee_3.log']
"""
