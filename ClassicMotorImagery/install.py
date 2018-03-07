import pip

_all_ = [
    "pygame",
    "screeninfo",
    "pylsl",
    "scipy",
    "pyqtgraph"
]

windows = [
    "pypiwin32"
]


def install(packages):
    for package in packages:
        pip.main(['install', package])


if __name__ == '__main__':
    import os

    install(_all_)
    if os.name == 'nt':
        install(windows)
