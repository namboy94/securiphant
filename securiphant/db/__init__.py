"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import os
from sqlalchemy.ext.declarative import declarative_base
from securiphant.config import config_dir


Base = declarative_base()
"""
The base database table class
"""

uri = "sqlite:///" + os.path.join(config_dir, "db.sqlite")
"""
The database URI
"""
