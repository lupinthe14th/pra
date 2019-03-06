#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from distutils.util import strtobool

ENDPOINT = os.environ.get("ENDPOINT")
APIKEY = os.environ.get("APIKEY")
VERIFY = strtobool(os.environ.get("VERIFY", "True"))

# vim: set fileencoding=utf-8 :
