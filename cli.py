import os
from ascender.start import _builtin_launcher

if __name__ == "__main__":
    os.environ["CLI_MODE"] = "1"
    _builtin_launcher()