"""
### Ascender Framework

A simple and powerful Web API framework for python. Developed by [Ascender](https://ascender.space)
"""
import os
from ascender.core.applications._create_internal import createInternalApplication


def _builtin_launcher():
    os.environ["CLI_MODE"] = "1"
    
    return createInternalApplication()()