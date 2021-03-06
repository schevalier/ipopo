Release notes
#############

iPOPO 0.5.4
***********

Additions
=========

Global
------

* Global speedup replacing ``list.append()`` by ``bisect.insort()``.
* Optimizations in handling services, components and LDAP filters.
* Some classes of Pelix framework and iPOPO core modules extracted to new
  modules.

iPOPO
-----

* ``@Requires`` accepts only one specification
* Added a context ``use_ipopo(bundle_context)``, to simplify the usage of the
  iPOPO service, using the keyword ``with``.
* ``get_factory_details(name)`` method now also returns the ID of the bundle
  provided the component factory, and the component instance properties.

Shell
-----

* The help command now uses the *inspect* module to list the required and
  optional parameters.
* ``IOHandler`` now has a ``prompt()`` method to ask the user to enter a line.
  It replaces the ``read()`` method, which was to buggy.

Bugs fixed
==========

Global
------

* Fixed support of Python 2.6.
* Replaced Python 3 imports conditions by ``try-except`` blocks.

iPOPO
-----

* Protection of the unregistration of factories, as a component can kill
  another one of the factory during its invalidation.

Remote Services
---------------

* Protection of the unregistration loop during the invalidation of JSON-RPC and
  XML-RPC exporters.
* The *Dispatcher Servlet* now handles the *discovered* part of the discovery
  process. This simplifies the Multicast Discovery component and suppresses a
  socket bug/feature on BSD (including Mac OS).

Shell
-----

* The ``make_table()`` method now accepts generators as parameters.
* Remote commands handling removed: ``get_methods_names()`` is not used anymore.


iPOPO 0.5.3
***********

Additions
=========

iPOPO
-----

* New ``get_factory_details(name)`` method in the iPOPO service, acting like
  ``get_instance_details(name)`` but for factories.
  It returns a dictionary describing the given factory.

* New ``factory`` shell command, which describes a component factory:
  properties, requirements, provided services, ...

HTTP Service
------------

* Servlet exceptions are now both sent to the client and logged locally

Bugs fixed
==========

Remote Services
---------------

* Data read from the servlets or sockets are now properly converted from bytes
  to string before being parsed (Python 3 compatibility).

Shell
-----

* Exceptions are now printed using ``str(ex)`` instead of ``ex.message``
  (Python 3 compatibility).

* The shell output is now flushed, both by the shell I/O handler and the
  text console. The remote console was already flushing its output.
  This allows to run the Pelix shell correctly inside Eclipse.


iPOPO 0.5.2
***********

Additions
=========

iPOPO Decorators
----------------

* An error is now logged if a class is manipulated twice. Decorators executed
  after the first manipulation, i.e. upon ``@ComponentFactory()``, are ignored.


HTTP Service
------------

* New servlet binding parameters:

  * http.name : Name of HTTP service. The name of component instance in the case
    of the basic implementation.

  * http.extra : Extra properties of the HTTP service. In the basic
    implementation, this the content of the *http.extra* property of the
    HTTP server component

* New method ``accept_binding(path, params)`` in servlets.
  This allows to refuse the binding with a server before to test the
  availability of the registration path, thus to avoid raising a meaningless
  exception.


Remote Services
---------------

* End points are stored according to their framework

* Added a method ``lost_framework(uid)`` in the registry of imported services,
  which unregisters all the services provided by the given framework.


Shell
-----

* Shell *help* command now accepts a command name to print a specific
  documentation


Bugs fixed
==========

iPOPO Decorators
----------------

* Better handling of inherited and overridden methods: a decorated method can
  now be overridden in a child class, with the name, without warnings.

* Better error logs, with indication of the error source file and line


iPOPO 0.5.1
***********

Additions
=========

Shell
-----

* The remote shell now provides a service, ``pelix.shell.remote``, with a
  ``get_access()`` method that returns the *(host, port)* tuple where the
  remote shell is waiting for clients.


HTTP Service
------------

* The HTTP service now supports the update of servlet services properties.
  A servlet service can now update its registration path property after having
  been bound to a HTTP service.
* A *500 server error* page containing an exception trace is now generated when
  a servlet fails.


Bugs fixed
==========

Framework
---------

* Bundle.update() now logs the SyntaxError exception that be raised in Python 3.

Shell
-----

* Fixed the ``threads`` command that wasn't working on Python 3.


HTTP Service
------------

* The ``bound_to()`` method of a servlet is called only after the HTTP service
  is ready to accept clients.

iPOPO 0.5
*********

API Changes
===========

Framework
---------

* ``BundleContext.install_bundle()`` now returns the ``Bundle`` object instead
  of the bundle ID.
  ``BundleContext.get_bundle()`` has been updated to accept both IDs and
  ``Bundle`` objects in order to keep a bit of compatibility

* ``Framework.get_symbolic_name()`` now returns *pelix.framework* instead of
  *org.psem2m.pelix*

* ``ServiceEvent.get_type()`` is renamed ``get_kind()``. The other name is
  still available but is declared deprecated (a warning is logged on its first
  use).


Shell
-----

* Shell command methods now take an ``IOHandler`` object in parameter instead
  of input and output file-like streams.
  This hides the compatibility tricks between Python 2 and 3 and simplifies the
  output formatting.


Additions
=========

Project
-------

* Added this "release notes" page to the web site

Framework
---------

* ``BundleContext.install_visiting(path, visitor)``:

  * Visits the given path and installs the found modules if the visitor accepts
    them

* ``BundleContext.install_package(path)`` (*experimental*):

  * Installs all the modules found in the package at the given path
  * Based on ``install_visiting()``


iPOPO
-----

* Components with a ``pelix.ipopo.auto_restart`` property set to *True* are
  automatically re-instantiated after their bundle has been updated.


Services
--------

* Remote Services: use services of a distant Pelix instance

  * Multicast discovery
  * XML-RPC transport (not fully usable)
  * JSON-RPC transport (based on a patched version of jsonrpclib)

* EventAdmin: send events (a)synchronously

iPOPO 0.4
*********

Version 0.4 fixes many bugs and provides new features:

Pelix
=====

* ``create_framework()`` utility method
* The framework has been refactored, allowing more efficient services and
  events handling

iPOPO
=====

* A component can provide multiple services
* A service controller can be injected for each provided service, to
  activate or deactivate its registration
* Dependency injection and service providing mechanisms have been refactored,
  using a basic handler concept.

Services
========

* Added a HTTP service component, using the concept of *servlet*
* Added an extensible shell, interactive and remote, simplifying the usage
  of a framework instance

iPOPO 0.3
*********

Packages have been renamed. As the project goes public, it may not have
relations to isandlaTech projects anymore.

+------------------------+------------------+
| Previous name          | New name         |
+========================+==================+
| psem2m                 | pelix            |
+------------------------+------------------+
| psem2m.service.pelix   | pelix.framework  |
+------------------------+------------------+
| psem2m.component       | pelix.ipopo      |
+------------------------+------------------+
| psem2m.component.ipopo | pelix.ipopo.core |
+------------------------+------------------+

iPOPO 0.2
*********

Version 0.2 is the first public release, under GPLv3 license (see LICENSE).
