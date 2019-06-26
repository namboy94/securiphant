"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import os
import json
from typing import Dict


def load_config() -> Dict[str, str]:
    """
    Loads the config for securiphant
    :return: The configuration data
    """
    config_file = os.path.join(
        os.path.expanduser("~"),
        ".config/securiphant/config.json"
    )
    with open(config_file, "r") as f:
        return json.load(f)
