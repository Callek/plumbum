from plumbum.commands.processes import CommandNotFound
from plumbum.commands.processes import ProcessExecutionError
from plumbum.commands.processes import ProcessTimedOut


class PopenAddons(object):
    """This adds a verify to popen objects to that the correct command is attributed when
    an error is thrown."""

    def verify(self, retcode, timeout, stdout, stderr):
        """This verifies that the correct command is attributed."""
        if getattr(self, "_timed_out", False):
            raise ProcessTimedOut(
                "Process did not terminate within %s seconds" % (timeout, ),
                getattr(self, "argv", None))

        if retcode is not None:
            if hasattr(retcode, "__contains__"):
                if self.returncode not in retcode:
                    raise ProcessExecutionError(
                        getattr(self, "argv", None), self.returncode, stdout,
                        stderr)
            elif self.returncode != retcode:
                raise ProcessExecutionError(
                    getattr(self, "argv", None), self.returncode, stdout,
                    stderr)
