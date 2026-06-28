import screen_brightness_control as sbc


def get_monitors():
    return sbc.list_monitors_info()


def get_current_brightness():
    try:
        return sbc.get_brightness()
    except:
        return [50]


def set_all_brightness(value):
    sbc.set_brightness(value)


def set_monitor_brightness(value, monitor_index):
    sbc.set_brightness(
        value,
        display=monitor_index
    )