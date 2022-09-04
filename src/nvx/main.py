#!/usr/bin/python3
import argparse
import configparser
import os
import re
import shlex
import subprocess
from pathlib import Path


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
    if not config_path.exists():
        print("No config file found.")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        default_config = init_config()
        with open(config_path, 'w') as configfile:
            default_config.write(configfile)
        print(f"A new config file using default configuration was created under '{config_path}'.\n"
              "Make sure to properly change the config according to your screen setup before running this command again"
              "to avoid getting a black screen.\n"
              "Run `xrandr' to have information on your screen ids, supported resolutions and refresh rates.")
        exit(2)
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


def parse_user_config(override_layout=None, wrap=None):
    config = get_user_config()
    sections = config.sections()
    if override_layout is not None and len(override_layout) > 0:
        if wrap is not None:
            assert wrap > 0, 'Wrap must be a positive integer'
            layout = [override_layout[i:i + wrap] for i in range(0, len(override_layout), wrap)]
        else:
            layout = [override_layout]
    else:
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
    screens_settings = ', '.join(
        screen_settings(screen) for screen in screens.values() if
        'position' in screen and not re.match(r"DUMMY-\d", screen['id']))
    cmd = f'nvidia-settings --assign CurrentMetaMode="{screens_settings}"'
    print(f"Running {cmd}")
    args = shlex.split(cmd)
    out = subprocess.check_output(args)
    print(f"##### Command output:")
    print(out.decode('utf-8'))
    print("##### Done")


def main():
    parser = argparse.ArgumentParser(description='Configure nvidia-settings for multiple screens')
    parser.add_argument('layout', nargs='*', type=int, help='Screen layout, e.g. 1 2 3, defaults to config file')
    parser.add_argument(
        '-w', '--wrap', type=int,
        help='Number of screens per row, e.g. 2 with 4 screens will result in 2x2 layout, infinite if not set'
    )
    args = parser.parse_args()
    if args.wrap and len(args.layout) == 0:
        raise RuntimeError('Layout must be specified when using wrap')
    layout, screens = parse_user_config(args.layout, args.wrap)
    compute_screen_positions(layout, screens)
    nvidia_settings(screens)


if __name__ == '__main__':
    main()
