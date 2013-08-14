"""
Diagnostics output for Confab settings.
"""
from optparse import OptionParser

from fabric.api import settings
from gusset.colortable import ColorTable
from gusset.output import configure_output

from confab.definitions import Settings
from confab.iter import iter_conffiles
from confab.main import add_core_options


def parse_options():
    """
    Parse command line options.
    """
    parser = OptionParser(usage="confab-show [options]")
    add_core_options(parser)

    opts, args = parser.parse_args()
    return parser, opts, args


def make_row(conffile):
    """
    Generate a dictionary describing this conffile.
    """
    return {
        "hash": conffile.hexdigest(),
        "environment": conffile.environment,
        "host": conffile.host,
        "path": conffile.remote,
        "role": conffile.role,
        "component": conffile.component,
    }


def make_table(settings_,
               environment,
               hosts,
               roles):
    """
    Transform command line arguments into a table.
    """
    sort_key = lambda description: (description["environment"],
                                    description["host"],
                                    description["path"],
                                    description["role"],
                                    description["component"])
    table = ColorTable("hash",
                       "environment",
                       "host",
                       "path",
                       "role",
                       "component",
                       sort_key=sort_key)

    for environmentdef in settings_.all():
        # match environment, if any
        if environment is not None and environment != environmentdef.name:
            continue

        # match hosts and roles, if any
        environmentdef = environmentdef.with_hosts(*hosts).with_roles(*roles)

        with settings(environmentdef=environmentdef):
            for conffiles in iter_conffiles(settings_.directory):
                for conffile in conffiles.conffiles:
                    row = make_row(conffile)
                    table.add(**row)
    return table


def main():
    """
    Diagnostics command line entry point.
    """
    try:
        # Parse and validate arguments
        parser, options, arguments = parse_options()

        configure_output(verbosity=options.verbosity, quiet=options.quiet)

        settings = Settings.load_from_module(options.directory)

    except Exception as e:
        parser.error(e)

    table = make_table(settings,
                       options.environment,
                       options.hosts.split(",") if options.hosts else [],
                       options.roles.split(",") if options.roles else [])
    print(table)
