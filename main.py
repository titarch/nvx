#!/usr/bin/python3
import configparser
import os
from pathlib import Path


def init_config():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.add_section('Settings')
    config.add_section('Screen_1')
    config.set('Screen_1', 'ScreenID', 'DP-0')
    config.set('Screen_1', 'ScreenName', 'Screen 1')
    config.set('Screen_1', 'ScreenResolution', '1920x1080')
    config.set('Screen_1', 'ScreenRefreshRate', '60')
    return config


def get_user_config():
    config_path = Path.home() / '.config' / 'nvx' / 'nvx.conf'
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        default_config = init_config()
        with open(config_path, 'w') as configfile:
            default_config.write(configfile)
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(config_path)
    return config


def main():
    print(get_user_config())


if __name__ == '__main__':
    main()
