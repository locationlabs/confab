"""
Non-init module for doing convenient * imports from.
"""

# core
from confab.conffiles import ConfFiles

# settings
from confab.definitions import Settings

# environment tasks
from confab.autotasks import generate_tasks

# jinja2 environment loading
from confab.loaders import FileSystemEnvironmentLoader, PackageEnvironmentLoader

# data loading
from confab.data import DataLoader

# options
from confab.options import assume_yes, Options

# iterations
from confab.iter import iter_hosts_and_roles, iter_conffiles, make_conffiles

# fabric tasks
from confab.diff import diff
from confab.generate import generate
from confab.pull import pull
from confab.push import push

__ignore__ = [
    assume_yes,
    generate_tasks,
    ConfFiles,
    FileSystemEnvironmentLoader,
    PackageEnvironmentLoader,
    DataLoader,
    diff,
    generate,
    pull,
    push,
    Options,
    Settings,
    iter_hosts_and_roles,
    iter_conffiles,
    make_conffiles,
]
