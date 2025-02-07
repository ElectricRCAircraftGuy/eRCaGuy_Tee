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


class Tee:
    def __init__(self, *paths, immediately_flush=False, redirect_stderr=False):
        """
        Create a Tee object that writes to multiple files, as specified by the paths passed in.

        Args:
        - paths: one or more paths to write to
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

        self.paths = paths
        self.immediately_flush = immediately_flush
        self.redirect_stderr = redirect_stderr

    def begin(self):
        """
        Begin tee-ing stdout to the console and to one or more log files.
        """
        # Open all the files for writing
        self.logfiles = []
        for path in self.paths:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.logfiles.append(open(path, "w"))

        # Save the original stdout, and replace it with the Tee object
        self.stdout_bak = sys.stdout
        sys.stdout = self

        if self.redirect_stderr:
            # Save the original stderr, and replace it with the Tee object
            self.stderr_bak = sys.stderr
            sys.stderr = self

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
    logpath = os.path.join(SCRIPT_DIRECTORY, "temp", "tee.log")
    tee = Tee(logpath)

    tee.begin()

    # Example usage
    print("This will be printed to the console and written to the file.")
    print("Another line of output.")
    colors.print_red("This will be printed to the console and written to the file. It is red.")

    tee.end()


if __name__ == "__main__":
    main()


"""
Example output:
- this output goes to both the console **and** to the log file at ""


eRCaGuy_PathShortener$ ./tee.py 
This will be printed to the console and written to the file.
Another line of output.
This will be printed to the console and written to the file. It is red.
"""
