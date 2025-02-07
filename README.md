

# eRCaGuy_Tee

A Python `tee` program to easily tee all print statements both to stdout **and** to a log file. 


# Clone and run

```bash
# clone the repo
git clone https://github.com/ElectricRCAircraftGuy/eRCaGuy_Tee.git

# cd into the repo
cd eRCaGuy_Tee

# clone all submodules
git submodule update --init --recursive

# run demo
./Tee.py

# view the log file created
cat temp/tee.log
```

For help on submodules, see my tutorial here: [GabrielStaples.com: `git submodule` “Quick Start” guide](https://gabrielstaples.com/git-submodule-guide/#gsc.tab=0)


# Example

It's like the Unix `tee` command, but for Python print statements. 

In Bash, you do this to tee the output of a command to both stdout and to a file:
```bash
some_command | tee some_file.txt
```

In Python, with this module, you can now do this to tee all `print()` statements (actually: all data which goes to `stderr` or to `stdout`), to both stdout and to a file:

```python
import eRCaGuy_Tee.Tee as Tee
import eRCaGuy_Tee.eRCaGuy_PyColors.ansi_colors as colors
import sys

logpath = "my_log.txt"
tee = Tee.Tee(logpath, redirect_stderr=True)
tee.begin()  # start redirecting stdout and stderr to the file

# Example usage
print("This will be printed to the console and written to the file.")
print("Another line of output.")
colors.print_red("This will be printed to the console and written to the file. It is red.")

# Since we set `redirect_stderr=True`, this will be written both to the console and to 
# the file too.
print("This is stderr output.", file=sys.stderr)

tee.end()  # close the file and stop redirecting stdout and stderr to it
```
