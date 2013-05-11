.. _todo:

Future Work
===========

1.  Confab needs a better **push** command line interface, and the following is
    a possible option::

      The following configuration files have changed for localhost:

         no | filename                                          | changed
         ---+---------------------------------------------------+--------
         1  | /etc/iptables.rules                               | new
         2  | /etc/iptables.rules.services                      | yes
         3  | /opt/wm/etc/sprint_sms_gateway/gateway.properties | no

      Select files to push? [all/None/..1,2..] 1,3

2.  Similarly **diff** should offer a similar option to select files to show
    diffs::

      The following configuration files have changed for localhost:

         no | filename                                          | changed
         ---+---------------------------------------------------+--------
         1  | /etc/iptables.rules                               | new
         2  | /etc/iptables.rules.services                      | yes
         3  | /opt/wm/etc/sprint_sms_gateway/gateway.properties | no

      See changes for file(s)? [all/..1,2..] 1,3
