#!/usr/bin/python3
import configparser
import os
import re
from pathlib import Path
import shlex
import subprocess


def init_config():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.add_section('Layout')
    config.set('Layout', 'Row_1', '1')
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


def parse_layout_matrix(config):
    layout_options = config.options('Layout')
    rows = [option for option in layout_options if re.match(r'^Row_\d+$', option)]
    layout = [config.get('Layout', row) for row in rows]
    assert all(re.match(r'^[\d ]+$', row) for row in layout), 'Layout rows must be a list of numbers and spaces'
    layout = [list(map(int, row.split(' '))) for row in layout]
    row_numbers = [int(row.split('_')[-1]) for row in rows]
    matrix = list(zip(row_numbers, layout))
    matrix.sort(key=lambda x: x[0])
    return list(list(zip(*matrix))[1])


def parse_screens(config, screen_sections):
    screens = dict()
    for section in screen_sections:
        screen = dict()
        key = int(section.split('_')[-1])
        id = config.get(section, 'ScreenID')
        assert re.match(r'^\w+-\d+$', id), 'ScreenID must be a valid display ID, e.g. DP-0 or HDMI-2'
        screen['id'] = id
        screen['name'] = config.get(section, 'ScreenName')
        resolution = config.get(section, 'ScreenResolution')
        assert re.match(r'^\d+x\d+$', resolution), 'Screen resolution must be in the format WxH'
        screen['resolution'] = resolution
        screen['width'], screen['height'] = map(int, resolution.split('x'))
        screen['refresh_rate'] = int(config.get(section, 'ScreenRefreshRate'))
        screens[key] = screen
    return screens


def parse_user_config():
    config = get_user_config()
    sections = config.sections()
    if 'Layout' not in sections:
        raise RuntimeError('No Layout section found in config')
    layout = parse_layout_matrix(config)

    screen_sections = [section for section in sections if re.match(r'^Screen_\d+$', section)]
    if len(screen_sections) == 0:
        raise RuntimeError('Config must contain at least one screen section, e.g. Screen_1')
    screens = parse_screens(config, screen_sections)
    return layout, screens


def compute_screen_positions(layout, screens):
    offset = (0, 0)
    for row in layout:
        for index in row:
            if index not in screens:
                raise RuntimeError(f"Screen_{index} not found in config")
            screen = screens[index]
            screen['position'] = offset
            offset = (offset[0] + screen['width'], offset[1])
        offset = (0, offset[1] + max(screens[index]['height'] for index in row))


def screen_settings(screen):
    return f"{screen['id']}: {screen['resolution']}_{screen['refresh_rate']} +{screen['position'][0]}+{screen['position'][1]} {{ForceCompositionPipeline=On}}"


def nvidia_settings(screens):
    screens_settings = ', '.join(screen_settings(screen) for screen in screens.values() if 'position' in screen)
    cmd = f'nvidia-settings --assign CurrentMetaMode="{screens_settings}"'
    print(f"Running {cmd}")
    args = shlex.split(cmd)
    out = subprocess.check_output(args)
    print(f"##### Command output:")
    print(out.decode('utf-8'))
    print("##### Done")


def main():
    layout, screens = parse_user_config()
    compute_screen_positions(layout, screens)
    nvidia_settings(screens)


if __name__ == '__main__':
    main()
