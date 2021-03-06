.. Mixing iPOPO and Qt

Mixing iPOPO and PyQt
#####################

.. important:: This tutorial is based on PyQt4, tested with PyQt 4.9.1.

   * To install PyQt4 from the sources, take a look at:
     `Installing PyQt4 <http://pyqt.sourceforge.net/Docs/PyQt4/installation.html>`_
   * For Windows or MacOS, see
     `PyQt Downloads <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_
   * On Linux, your distribution might have a ``python-qt4`` or a ``PyQt4`` package
   
   

Description
***********

This tutorial shows how to run a PyQt application based on Pelix.

The difficulty is that UI operations **must** be executed in the main thread
of the application.

The solution is to:

* Write a PyQt bridge, with a method to execute code in the main thread
* Setup PyQt in the main thread on the application
* Start a Pelix framework in a new thread
* Register the PyQt bridge as a service

The PyQt bridge
***************

The *qt_bridge* **module** imports the PyQt modules and defines a QtLoader class.
This class has the following methods:

+------------------------+---------------------------------------------------+
| Method                 | Description                                       |
+========================+===================================================+
| setup(argv)            | Creates a QApplication object and sets up signals |
+------------------------+---------------------------------------------------+
| loop()                 | The blocking event loop (QApplication.exec_())    |
+------------------------+---------------------------------------------------+
| stop()                 | Closes the windows and stops the application loop |
+------------------------+---------------------------------------------------+
| get_application()      | Retrieves the QApplication object                 |
+------------------------+---------------------------------------------------+
| run_on_ui(method, ...) | Executes the given method in the main/UI thread   |
+------------------------+---------------------------------------------------+

The thread that loaded this file is considered as the UI thread.
In most operating systems, it **must** be the application main thread.

The full code is available here: `qt_bridge.py <../_static/pyqt/qt_bridge.py>`_.

.. note:: The PyQt bridge is a Python module, and does not need to be installed
   as a Pelix bundle. It will be used to setup the application before the
   creation of a framework.

run_on_ui(...)
==============

The trick to execute code in the main thread is to use Qt signals and a Queue.
A signal can be emitted from any thread, but it is always handled in the UI
thread.

When ``run_on_ui`` is called, the given method and arguments are stored in a
queue.
A ``threading.Event`` object is also created and added to the queue.
Then, a Qt signal is emitted and the caller is waiting on the Event object
created just before.

.. literalinclude:: /_static/pyqt/qt_bridge.py
   :language: python
   :lines: 93-113


The Qt signal is then handled in the UI thread, by a slot method in the same
object.
This method will get the next waiting method in the queue, execute it and
finally update the associated Event object.

.. literalinclude:: /_static/pyqt/qt_bridge.py
   :language: python
   :lines: 65-83


Start the application
*********************

Starting the is quite straight forward:

.. literalinclude:: /_static/pyqt/main.py
   :language: python


Sample UI
*********

This is a really simple demonstration:

* a ``frame`` bundle automatically instantiates a component that depends on
  the Qt bridge.
  It aggregates services implementing a *qt.widget* specification, with the
  property *placement* set to *main* and show them in QTabWidget.

* a ``widget`` bundle that defines a component implementing the *qt.widget*
  specification. It instantiate a demonstration component that can be
  instantiated multiple times.

The *qt.widget* specification consists in two methods:

+--------------------+-----------------------------------------------+
| Method             | Description                                   |
+====================+===============================================+
| get_name()         | Name to use in the tab bar                    |
+--------------------+-----------------------------------------------+
| get_widget(parent) | Must return the widget to use in the UI       |
+--------------------+-----------------------------------------------+
| clean(parent)      | Called when the widget is removed from the UI |
+--------------------+-----------------------------------------------+

Frame
=====

The frame bundle defines a class extending ``QMainWindow``, that will
represent the main frame, and a component ``MainFrame`` that will be the bridge
between Pelix services and the main frame.

The ``_QtMainFrame`` class, extending ``QMainWindow``, simply load a .ui file
and connects some basic signals.

The ``MainFrame`` component creates the ``_QtMainFrame`` object when it is
validated and destroys it when it is invalidated.
When a ``qt.widget`` service is bound, it creates a new tab in the main frame
containing the result of ``service.get_widget()``.


Widget
======

The widget is a very simple iPOPO component that provides a ``qt.widget``
service.
It creates a ``QLabel`` object when the ``get_widget()`` method is first called
and destroys it when the ``clean()`` method is called.


Shell session
=============

Here is a small shell session that shows how the application reacts:

.. code-block:: console

   ** Pelix Shell prompt **
   $ ipopo.instances
   +----------------------+------------------------------+-------+
   |         Name         |           Factory            | State |
   +======================+==============================+=======+
   | MainFrame            | MainFrameFactory             | VALID |
   +----------------------+------------------------------+-------+
   | ipopo-shell-commands | ipopo-shell-commands-factory | VALID |
   +----------------------+------------------------------+-------+
   | widget-0             | widget-factory               | VALID |
   +----------------------+------------------------------+-------+
   $ ipopo.instantiate widget-factory widget-1
   Component 'widget-1' instantiated.
   $ ipopo.kill widget-1
   Component 'widget-1' killed.
   $ ipopo.kill widget-0
   Component 'widget-0' killed.
   $ ipopo.instantiate widget-factory widget-1
   Component 'widget-1' instantiated.
   $ exit
   Bye !


Source code
===========

The source code of this demonstration is available here:

* `main.py <../_static/pyqt/main.py>`_: The application bootstrap.
  Loads the PyQt bridge and the framework.
* `qt_bridge.py <../_static/pyqt/qt_bridge.py>`_: The PyQt bridge module
* `frame.py <../_static/pyqt/frame.py>`_: The main frame bundle

  * `main.ui <../_static/pyqt/main.ui>`_: The main frame UI
    made with Qt Designer

* `widget.py <../_static/pyqt/widget.py>`_: The simple widget bundle


