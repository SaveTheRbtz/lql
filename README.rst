ABOUT
=====
Yet another apache/nginx log parser with SQL flavour.
Quite a nice project for 1st April.

TODO
====
* Move file specification into LQL, e.g.::

    SELECT * FROM /var/log/httpd/access.log

* Add support for ``JOIN`` statement
* Add debian/spec files for .deb and .rpm package systems

HOWTO
=====
Please run::

    src/lql -h
