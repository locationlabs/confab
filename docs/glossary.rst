.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   host
     Hosts are physical or virtual machines accessible via ssh.

     Confab will normally identify hosts by their fully qualified domain name
     (FQDN), so hostnames matter.

   environment
     Environments are groups of :term:`hosts<host>` that work together for a
     single purpose.

     It's common to have one environment for development, one for staging, one
     for production and so forth.

   component
     Components are slices of configuration files.

     The configuration files that Confab manages are controlled by which
     components are selected.

   role
     Roles are groups of zero or more :term:`components<component>` that
     achieve a common purpose.

     In the degenerate case where a role has no components, the role
     itself is  taken to be a component.
