"""Beacon CLI commands package"""

from beacon.commands.run import app as run
from beacon.commands.doctor import app as doctor
from beacon.commands.gate import app as gate
from beacon.commands.init import app as init
from beacon.commands.status import app as status
from beacon.commands.report import app as report
from beacon.commands.debug import app as debug
from beacon.commands.feedback import app as feedback
from beacon.commands.resume import app as resume

__all__ = [
    "run",
    "doctor",
    "gate",
    "init",
    "status",
    "report",
    "debug",
    "feedback",
    "resume",
]
