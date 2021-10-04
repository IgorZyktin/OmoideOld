# -*- coding: utf-8 -*-
"""Server status object.
"""
from pydantic import BaseModel

STATUS_INIT = 'active'
STATUS_ACTIVE = 'active'
STATUS_RELOADING = 'reloading'
STATUS_FAILED = 'failed'


class Status(BaseModel):
    """Description of the server status."""
