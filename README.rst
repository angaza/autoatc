#######
autoatc
#######

Provide simple tool(s) for interacting with `Augmented Traffic Control (ATC)
<http://facebook.github.io/augmented-traffic-control/>`_.

Written as a basic, inelegant way to provide a default shaping profile for all
clients.

Installation
============

Install it from PyPI:

.. code-block:: console

   $ pip install autoatc

Here's a simple usage example:

.. code-block:: console

   $ autoatc-ensure localhost:8000 profiles/2G-DevelopingUrban.json 192.168.1.100 192.168.1.200

License
=======

This project is released under the standard MIT license. See the `LICENSE` file
for details.
