"""
Diagnostics output for Confab settings.
"""
from collections import OrderedDict
from optparse import OptionParser
from string import capwords
from fabric.api import settings
from fabric.colors import red, green, blue, magenta, white, yellow

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


def make_conffile_description(conffile):
    """
    Generate an ordered dictionary describing this conffile.
    """
    row = OrderedDict()
    # order here determine row order of output
    row["hash"] = conffile.hexdigest()
    row["environment"] = conffile.environment
    row["host"] = conffile.host
    row["path"] = conffile.remote
    row["role"] = conffile.role
    row["component"] = conffile.component
    return row


def make_conffile_descriptions(settings_,
                               environment,
                               hosts,
                               roles):
    """
    Transform command line arguments into a list of rows.
    """
    rows = []
    for environmentdef in settings_.all():
        # match environment, if any
        if environment is not None and environment != environmentdef.name:
            continue

        # match hosts and roles, if any
        environmentdef = environmentdef.with_hosts(*hosts).with_roles(*roles)

        with settings(environmentdef=environmentdef):
            for conffiles in iter_conffiles(settings_.directory):
                for conffile in conffiles.conffiles:
                    rows.append(make_conffile_description(conffile))
    return rows


def print_conffiles(descriptions):
    """
    Print descriptions.

    :param descriptions: a list of descriptions
    """
    if not descriptions:
        return

    # Assign colors for each column
    colors = (red, magenta, blue, green, white, yellow)

    # Construct header
    header = OrderedDict()
    for key in descriptions[0].keys():
        header[key] = capwords(key)

    # Compute maximum width for each key (including header)
    make_lengths = lambda key: [len(description[key]) for description in [header] + descriptions]
    widths = dict([(key, max(make_lengths(key))) for key in descriptions[0].keys()])

    # Construct separator
    separator = OrderedDict()
    for key in descriptions[0].keys():
        separator[key] = "-" * widths[key]

    # Format descriptions using color and left justification
    def format_description(description):
        format_value = lambda color, key, value: color(" {}".format(value).ljust(1 + widths[key]))
        return " ".join([format_value(color, key, value) for color, (key, value) in zip(colors, description.items())])

    # Choose columns for sort order
    sort_key = lambda description: (description["environment"],
                                    description["host"],
                                    description["path"],
                                    description["role"],
                                    description["component"])

    print format_description(header)
    print format_description(separator)
    for description in sorted(descriptions, key=sort_key):
        print format_description(description)


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

    descriptions = make_conffile_descriptions(settings,
                                              options.environment,
                                              options.hosts.split(",") if options.hosts else [],
                                              options.roles.split(",") if options.roles else [])
    print_conffiles(descriptions)
