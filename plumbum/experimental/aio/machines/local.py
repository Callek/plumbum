import os
import sys
import subprocess
import logging
import time
import platform
import re
from functools import partial
from plumbum.path.local import LocalPath, LocalWorkdir
from tempfile import mkdtemp
from contextlib import contextmanager
from asyncio.subprocess import Process
from asyncio.subprocess import create_subprocess_shell
from plumbum.path.remote import RemotePath
from plumbum.commands import CommandNotFound, ConcreteCommand
from plumbum.machines.session import ShellSession
from plumbum.lib import ProcInfo, IS_WIN32, six, StaticProperty
from plumbum.commands.daemons import win32_daemonize, posix_daemonize
from plumbum.commands.processes import iter_lines
from plumbum.machines.base import BaseMachine
from plumbum.experimental.aio.machines.base import PopenAddons
from plumbum.machines.env import BaseEnv

# python 3 has the new-and-improved subprocess module
from subprocess import Popen, PIPE
has_new_subprocess = True


class PlumbumLocalPopen(PopenAddons):
    iter_lines = iter_lines

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        if 'cmd' not in kwargs:
            cmd_args = args[0]
            cmd = " ".join(cmd_args)
            args = (cmd, *args[1:])
        else:
            cmd_args = kwargs['cmd']
            cmd = " ".join(cmd_args)
            kwargs['cmd'] = cmd
        self._proc_coro = create_subprocess_shell(*args, **kwargs)

    def __iter__(self):
        return self.iter_lines()

    async def __aenter__(self):
        self._proc = await self._proc_coro
        return self._proc

    async def __aexit__(self, *args, **kwargs):
        return self._proc.wait()

    def __getattr__(self, name):
        return getattr(self._proc, name)
