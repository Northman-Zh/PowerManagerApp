import subprocess


def shutdown(minutes):
    seconds = minutes * 60

    subprocess.run(
        ["shutdown", "/s", "/t", str(seconds)],
        shell=True
    )


def restart(minutes):
    seconds = minutes * 60

    subprocess.run(
        ["shutdown", "/r", "/t", str(seconds)],
        shell=True
    )


def cancel_shutdown():
    subprocess.run(
        ["shutdown", "/a"],
        shell=True
    )