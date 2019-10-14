#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .linux_job import LinuxJob
from .windows_job import WindowsJob


def get_class_name():
    import platform
    if platform.system() == "Windows":
        return WindowsJob
    elif platform.system() == "Linux":
        return LinuxJob
    else:
        return None
