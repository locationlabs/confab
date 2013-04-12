"""
Diagnostics output for Confab settings.
"""
from collections import OrderedDict
from os.path import join
from optparse import OptionParser
from string import capwords
from fabric.colors import red, green, blue, magenta, white

from confab.definitions import Settings
from confab.conffiles import iterconffiles
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
    row = OrderedDict()
    # order here determine row order of output
    row["hash"] = conffile.hexdigest()
    row["environment"] = conffile.environment
    row["host"] = conffile.host
    row["path"] = conffile.remote
    row["role"] = conffile.role
    return row


def make_rows(settings,
              environment,
              hosts,
              roles,
              template_dir,
              data_dir):
    """
    Transform command line arguments into a list of rows.
    """
    rows = []
    for environmentdef in settings.iterall():
        # match environment, if any
        if environment is not None and environment != environmentdef.name:
            continue

        # match hosts and roles, if any
        environmentdef = environmentdef.with_hosts(*hosts).with_roles(*roles)

        for conffiles in iterconffiles(environmentdef, template_dir, data_dir):
            for conffile in conffiles.conffiles:
                rows.append(make_row(conffile))
    return rows


def print_rows(rows):
    """
    Print rows.

    :param rows: a list of rows
    """
    if not rows:
        return

    # Assign colors for each column
    colors = (red, magenta, blue, green, white)

    # Construct header
    header = OrderedDict()
    for key in rows[0].keys():
        header[key] = capwords(key)

    # Compute maximum width for each key (including header)
    widths = dict([(key, max([len(row[key]) for row in [header] + rows])) for key in rows[0].keys()])

    # Construct separator
    separator = OrderedDict()
    for key in rows[0].keys():
        separator[key] = "-" * widths[key]

    # Format rows using color and left justification
    def format_row(row):
        format_value = lambda color, key, value: color(" {}".format(value).ljust(1 + widths[key]))
        return " ".join([format_value(color, key, value) for color, (key, value) in zip(colors, row.items())])

    # Choose columns for sort order
    sort_key = lambda row: (row["environment"], row["host"], row["path"])

    print format_row(header)
    print format_row(separator)
    for row in sorted(rows, key=sort_key):
        print format_row(row)


def main():
    """
    Diagnostics command line entry point.
    """
    try:
        # Parse and validate arguments
        parser, options, arguments = parse_options()

        settings = Settings.load_from_module(options.directory)

    except Exception as e:
        parser.error(e)

    rows = make_rows(settings,
                     options.environment,
                     options.hosts.split(",") if options.hosts else [],
                     options.roles.split(",") if options.roles else [],
                     join(options.directory, "templates"),
                     join(options.directory, "data"))

    print_rows(rows)
