.. _tasks:

Tasks
=====

Confab provides four default tasks:

 1. Generate configuration files from templates. (**generate**)

 2. Pull configuration files from a remote host. (**pull**)

 3. Show differences between generated and remote configuration files. (**diff**)

 4. Interactively push generated configuration files to a remote host. (**push**)

The default tasks all expect a series of directories as inputs:

 -  **templates_dir** is the root directory for loading templates.

 -  **data_dir** is the root directory for loading configuration data.

 -  **generated_dir** is the root directory where generated configuration files
    will be written.

 -  **remotes\_dir** is the root directory where remote configuration files are
    saved.

When run from within a *fabfile*, these directories must be specified on the
command line. The *confab* console script assumes that all directories are
defined relative to another root directory specified on the command line.
