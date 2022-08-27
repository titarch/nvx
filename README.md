# nvx
Simple script running nvidia-settings (with anti-tearing) based on your configured layout

## Configuration

The configuration is stored in the file `~/.config/nvx/nvx.conf`.
It is a simple INI file, which contains the following sections:
- Layout: defines the layout matrix using the screen indices and can
have multiple rows.
- Screens: must be called Screen_\<screen index\> and defines the screen properties.

### Example

```

```ini
# $HOME/.config/nvx/nvx.conf
[Layout]
Row_1 = 0 4 0
Row_2 = 1 2 3

[Screen_0]
ScreenID = DUMMY-0
ScreenName = Dummy 0
ScreenResolution = 2560x1440
ScreenRefreshRate = 0

[Screen_1]
ScreenID = DP-4
ScreenName = Left Screen
ScreenResolution = 2560x1440
ScreenRefreshRate = 144

[Screen_2]
ScreenID = DP-0
ScreenName = Center Screen
ScreenResolution = 2560x1440
ScreenRefreshRate = 144

[Screen_3]
ScreenID = DP-2
ScreenName = Right Screen
ScreenResolution = 2560x1440
ScreenRefreshRate = 144

[Screen_4]
ScreenID = DP-3
ScreenName = Top Screen
ScreenResolution = 2560x1440
ScreenRefreshRate = 144
```

Notes:
- A dummy screen maybe used for offsetting the screens, you must call is DUMMY-\<index\>

## Installation
### Using pip

```shell
pip3 install nvx
```

## Running
> :warning: Running `nvx` for the first time without prior configuration will write the default config.
> Make sure to properly edit the generated configuration before running nvx again
> (you can use the output from `xrandr` to figure out the screen properties). Improperly configured
> screens could result in a black screen when running the script.

```bash
$ nvx # runs using the default configuration
$ nvx -l "1 2 3" # overrides the layout
```
