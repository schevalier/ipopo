.. Tutorial iPOPO

iPOPO: the component framework
##############################

This tutorial shows how to work with the iPOPO framework.


Concepts
********

iPOPO is a service-oriented component model.

A component is an object with a life-cycle, requiring services and providing
ones, and associated to properties.
The code of a component is reduced to its functional purpose: life-cycle,
dependencies, etc, are handled by iPOPO.

In iPOPO, a component is an instance of component factory, i.e. a Python class
manipulated with the iPOPO decorators.
The usage of decorators is described in :ref:`decorators`.
The manipulation process is explained in :ref:`manipulation`.

.. important:: Due to the use of Python properties, all component factories
   must be new-style classes. It is the case of all Python 3 classes, but
   Python 2.x classes must explicitly extend ``object``.


Component life cycle
====================

The component life cycle is handled by an instance manager created by the iPOPO
service.

This instance manager will inject control methods, inject dependencies,
register the component services.
All changes will be notified to the component using the callback methods it
declared.


.. figure:: /_static/component_lifecycle.png
   :scale: 40%
   :alt: Component life cycle
   :align: center
   
   Component life cycle

+--------------+---------------------------------------------------------------+
| State        | Description                                                   |
+==============+===============================================================+
| INSTANTIATED | The component has been instantiated.                          |
|              | Its constructor has been called.                              |
+--------------+---------------------------------------------------------------+
| VALIDATED    | All required dependencies have been injected.                 |
|              | All services provided by the component will be registered     |
|              | right after this method returned.                             |
+--------------+---------------------------------------------------------------+
| KILLED       | The component has been invalidated and won't be usable again. |
+--------------+---------------------------------------------------------------+


Callback methods
================

A component can define callback methods, by sing decorators.
The name of the methods can be anything but a *private* method (prefixed with
two underscores ``__``)

+--------------+------------------------------------------------------+----------------------------------------------------------------------------+
| Decorator    | Signature                                            | Description                                                                |
+==============+======================================================+============================================================================+
| @Validate    | ``def validate(self, context)``                      | The component is validating: all its dependencies have been injected.      |
|              |                                                      | The component will go in VALIDATED state if this method doesn't raise an   |
|              |                                                      | exception.                                                                 |
+--------------+------------------------------------------------------+----------------------------------------------------------------------------+
| @Invalidate  | ``def invalidate(self, context)``                    | The component is invalidating: its services are still there.               |
|              |                                                      | The component will go in INVALIDATED state even if an exception is raised. |
+--------------+------------------------------------------------------+----------------------------------------------------------------------------+
| @Bind        | ``def bind(self, service, reference)``               | This method is called after a dependency has been injected.                |
+--------------+------------------------------------------------------+----------------------------------------------------------------------------+
| @Update      | ``def update(self, service, reference)``             | This method is called after the properties of a dependency have changed.   |
+--------------+------------------------------------------------------+----------------------------------------------------------------------------+
| @Unbind      | ``def unbind(self, service, reference)``             | This method is called before a dependency is removed.                      |
+--------------+------------------------------------------------------+----------------------------------------------------------------------------+
| @BindField   | ``def bindfield(self, field, service, reference)``   | This method is called after a dependency has been injected in the          |
|              |                                                      | given field.                                                               |
+--------------+------------------------------------------------------+----------------------------------------------------------------------------+
| @UpdateField | ``def updatefield(self, field, service, reference)`` | This method is called after the properties of a dependency injected in     |
|              |                                                      | the given field have changed.                                              |
+--------------+------------------------------------------------------+----------------------------------------------------------------------------+
| @UnbindField | ``def unbindfield(self, field, service, reference)`` | This method is called before a dependency injected in the given field      |
|              |                                                      | is removed.                                                                |
+--------------+------------------------------------------------------+----------------------------------------------------------------------------+


Install the iPOPO bundle
************************

iPOPO is a bundle, named ``pelix.ipopo.core``.
It needs to be installed in a Pelix framework instance, like any bundle.

.. code-block:: python
   :linenos:

   # Import the Pelix module
   import pelix.framework
   
   # Start the framework
   framework = pelix.framework.FrameworkFactory.get_framework()
   framework.start()   
   
   # Get the bundle context
   context = framework.get_bundle_context()
   
   # Install and iPOPO the bundle
   bundle = context.install_bundle("pelix.ipopo.core")
   bundle.start()


Get the iPOPO service
*********************

.. note:: If you use the ``@Instantiate`` decorator to start all your
   components, you might not need to use the iPOPO service itself.

There are two equivalent ways to retrieve the iPOPO service:

* the standard Pelix way:

  .. code-block:: python
     :linenos:

     # Get the iPOPO service specification
     from pelix.ipopo.constants import IPOPO_SERVICE_SPECIFICATION

     # Find the service (context is a BundleContext)
     ipopo_ref = context.get_service_reference(IPOPO_SERVICE_SPECIFICATION)
     if ipopo_ref is None:
          print("iPOPO service not present")
          return

     try:
          # Use it
          ipopo = context.get_service(ipopo_ref)

     except pelix.framework.BundleException as ex:
          print("Error retrieving the iPOPO service: {0}".format(ex))
          return


* with the iPOPO utility method, which wraps the Pelix way:

  .. code-block:: python
     :linenos:

     # Get the iPOPO utility method
     from pelix.ipopo.constants import get_ipopo_svc_ref

     # Get the service (context is a BundleContext)
     ref_svc = get_ipopo_svc_ref(context)
     if ref_svc is None:
          print("iPOPO service not found")

     else:
          ipopo_ref, ipopo = ref_svc

As always, do not forget to call the ``BundleContext.unget_service()`` method
when you don't need the service anymore.


.. _decorators:

Write a component factory
*************************

The principle of iPOPO is to handle the life cycle of components which are
instances of factory classes.

.. important:: Due to the use of Python properties, all component factories
   must be new-style classes. It is the case of all Python 3 classes, but
   Python 2.x classes must explicitly extend ``object``.

Here is a sample factory class:

.. code-block:: python
   :linenos:
   
   from pelix.ipopo.decorators import *
   import pelix.ipopo.constants as constants

   # The component manipulator
   @ComponentFactory("MyIncrementerFactory")
   # Tell we want an instance of this factory
   @Instantiate("MyIncrementer")
   # Injects the component instance name in the "name" field
   @Property("_name", constants.IPOPO_INSTANCE_NAME)
   # Component specific, with a default value
   @Property("_thread_safe", "thread.safe", False)
   @Property("_flag", "usable", True)
   @Provides("my.incrementer")
   class ComponentIncrementer(object):
       """
       Sample Incrementer
       """
       def change(self, flag):
           """
           Changes the "usable" property
           """
           self._flag = flag 

       def increment(self):
           """
           Service implementation
           """
           self._count += 1
           return self._count
       
       @Validate
       def validate(self, context):
           """
           Component validated
           """
           self._count = 0
           print("%s: Ready..." % self._name)
         
       @Invalidate
       def invalidate(self, context):
           """
           Component invalidated
           """
           self._count = 0
           print("%s: Gone." % self._name)


* Lines 5-13: the decorators manipulates the class

  +-------------------+---------------------------------------------------+
  | Decorator         | Description                                       |
  +===================+===================================================+
  | @ComponentFactory | Finalizes the manipulation. It **must** be the    |
  |                   | top-level decorator                               |
  +-------------------+---------------------------------------------------+
  | @Instantiate      | Tells iPOPO to instantiate the component          |
  |                   | "MyIncrementer" as soon as the factory is loaded  |
  +-------------------+---------------------------------------------------+
  | @Property         | Defines the properties of the component and their |
  |                   | associated field                                  |
  +-------------------+---------------------------------------------------+
  | @Provides         | Defines the service provided by the component     |
  +-------------------+---------------------------------------------------+

* Lines 14-30: Implementation of the methods corresponding to the specification

* Lines 31-45: Definition of callback methods, called when iPOPO validates or
  invalidates the component


When the bundle containing this class will be started, its factories will be
loaded and the indicated component will be instantiated, if possible.

.. code-block:: python
   :linenos:
   
   >>> bundle = context.install_bundle("test_ipopo")
   >>> bundle.start()
   MyIncrementer: Ready...


Use the iPOPO service
*********************

The iPOPO service provides four important methods:

* ``register_factory(context, factory_class)``: registers the given
  **manipulated** class as a factory. The name of the factory is found in
  the manipulation attributes.
  If the class has not been manipulated or if the factory name has already
  been used, an error is raised.
  The given bundle context will be used for services registration and retrieval.

* ``unregister_factory(factory_name)``: unregisters the factory of the given
  name.

* ``instantiate(factory_name, name, properties)``: starts a new component using
  the given factory, with the given name and properties.
  The instantiation fails if a component with the same name already exists.

  .. code-block:: python
     :linenos:

     >>> # Starts a new incrementer
     >>> compo = ipopo.instantiate("MyIncrementerFactory", "incr2",
                                   {"usable": False})
     MyIncrementer: Ready...
     >>> # Check the "usable" property value, injected in the '_flag' field
     >>> compo._flag
     False
     >>> compo.increment()
     1

* ``kill(name)``: destroys the component with the given name.
  The component is invalidated then removed from the iPOPO registry.

  .. code-block:: python
     :linenos:

     >>> # Invalidates the started incrementer
     >>> ipopo.kill("incr2")
     MyIncrementer: Gone.


Component dependencies
**********************

Component dependencies is based on services, provided by ones and consumed by
others.

Validation and invalidation
===========================

A component is validated when all of its required dependencies have been
injected, and is invalidated when one of its required dependencies is gone.

Both methods take only one parameter: the context of the bundle that
registered the component.

In the following example, the consumer requires an incrementer:

.. code-block:: python
   :linenos:

   @ComponentFactory("ConsumerFactory")
   @Requires("svc", "my.incrementer", spec_filter="(usable=True)")
   class ConsumerFactory(object):
   
      @Validate
      def validate(self, context):
          print "Start:", self.svc.increment()
      
      @Invalidate
      def invalidate(self, context):
          print "Stopped:", self.svc.increment()
      

The service is injected before the component is validated and after it is
invalidated. That way, it can be used by the consumer can use it a last time
when the service or the consumer is invalidated.

A sample run, considering all bundles are started:

.. code-block:: python
   :linenos:

   >>> # Remember, a component named "MyIncrementer" has automatically been
   ... # started by iPOPO (@Instantiate decorator on the factory)
   >>> consumer = ipopo.instantiate("ConsumerFactory", "consumer")
   Start: 1
   
   >>> # Start the second incrementer
   >>> incr2 = ipopo.instantiate("MyIncrementerFactory", "incr2",
                                 {"usable": True})
   incr2: Ready...
   
   >>> # Set the first incrementer unusable: the injection will be updated.
   ... # As the injection is not optional, the consumer will be invalidated
   ... # during the re-injection
   >>> consumer.svc.change(False)
   Stopped: 2
   Start: 1
   
   >>> # Set the second incrementer unusable, it will invalidate the consumer
   >>> incr2.change(False)
   Stopped: 2
   
   >>> # Set the second incrementer usable again
   >>> incr2.change(True)
   Start: 3


Bind  and unbind
================

Additionally, a component can be notified when a dependency (required or not)
has been injected, using a bind method, or removed, using an unbind method.

Both methods take two parameters:

* the injected service object, to work directly with it
* the ServiceReference object for the injected service, to have access to the
  service information, properties, etc.

If the injection allows to validate the component, the bind method is called
before the validation one.
Conversely, if the injection implies to invalidate the component, the unbind
method is called after the invalidation one.

If the requirement is an aggregation, the bind and unbind methods are called
for each injected service.

Here is the previous service consumer, printing a line each time a service is
bound or unbound:

.. code-block:: python
   :linenos:
   
   from pelix.ipopo.decorators import *

   @ComponentFactory("ConsumerFactory")
   @Requires("svc", "my.incrementer", spec_filter="(usable=True)")
   class ConsumerFactory(object):
   
      @Validate
      def validate(self, context):
          print("Start: %d" % self.svc.increment())
      
      @Invalidate
      def invalidate(self, context):
          print("Stopped: %d" % self.svc.increment())
      
      @Bind
      def bind(self, service, reference):
          print("Bound to: %s" % reference.get_property("instance.name"))
      
      @Update
      def update(self, service, reference, old_properties):
          print("Updated: %s" % reference.get_property("instance.name"))
      
      @Unbind
      def unbind(self, service, reference):
          print("Component lost: %s" % reference.get_property("instance.name"))
      
      @BindField('svc')
      def bindfield(self, field, service, reference):
          print("%s injected into %s" % (reference.get_property("instance.name"), field))
      
      @UpdateField('svc')
      def updatefield(self, field, service, reference, old_properties):
          print("%s updated in %s" % (reference.get_property("instance.name"), field))
      
      @UnbindField('svc')
      def unbindfield(self, field, service, reference):
          print("%s removed from %s" % (reference.get_property("instance.name"), field))

          
Provided service
****************

A component can provide one or more services, with one or more specifications
each.
All component properties and all property changes are propagated to the
properties of the provided services.

.. note:: All services provided by iPOPO components have an **instance.name**
   property that contains the name of their provider.

iPOPO also allows to control if a service must be provided or not using a
boolean controller field, which can be different or shared for every provided
service.


As always, a snippet is better than a long description:

.. code-block:: python
   :linenos:
   
   @ComponentFactory(name="MyFactory")
   @Property("_property_field", "some.property", 42)
   @Provides(specifications="service.test_1")
   @Provides(specifications="service.test_2", controller="_test_ctrl")
   class Component(object):
    """
    Sample Component A
    """
    def __init__(self):
       """
       Constructor
       """
       # This code is for out-of-iPOPO instantiations
       self._property_field = 10
    
    def change_property(self, value):
       """
       Changes the value of the service property
       """
       self._property_field = value
       
    def change_controller(self, value):
       """
       Change the controller value

       If value is False, then the *service.test_2* will be unregistered
       """
       self._test_ctrl = value


This component has one property, ``some.property``, associated to the component
field ``_property_field``.
It also provides two distinct services, with one specification each.
The service ``service.test_2`` has a controller, which can be toggled using
the ``change_controller()`` method of the component.


Live test
*********

This section is a succession of commands ran in Python 2.6.5, with ``importlib``
installed, on an Ubuntu 10.04, using iPOPO 0.4.

It summarizes everything that have been told in the Pelix and iPOPO tutorials.

.. code-block:: python
   :linenos:
   
   # Prepare the component class
   >>> from pelix.ipopo.decorators import ComponentFactory, Property, Provides
   >>> @ComponentFactory(name="MyFactory")
   ... @Property("_property_field", "some.property", 42)
   ... @Provides(specifications="service.test_1")
   ... @Provides(specifications="service.test_2", controller="_test_ctrl")
   ... class Component(object):
   ...  """
   ...  Sample Component A
   ...  """
   ...  def __init__(self):
   ...     """
   ...     Constructor
   ...     """
   ...     # This code is for out-of-iPOPO instantiations
   ...     self._property_field = 10
   ...  def change_property(self, value):
   ...     """
   ...     Changes the value of the service property
   ...     """
   ...     self._property_field = value
   ...  def change_controller(self, value):
   ...     """
   ...     Change the controller value
   ...     
   ...     If value is False, then the *service.test_2* will be unregistered
   ...     """
   ...     self._test_ctrl = value
   ...
   
   # Start a framework
   >>> import pelix.framework
   >>> framework = pelix.framework.FrameworkFactory.get_framework()
   >>> context = framework.get_bundle_context()
   
   # Install the iPOPO bundle: it will be started with the framework
   >>> context.install_bundle('pelix.ipopo.core')
   1

   # Start the framework
   >>> framework.start()
   True

   # Get the iPOPO service
   >>> from pelix.ipopo.constants import get_ipopo_svc_ref
   >>> ipopo = get_ipopo_svc_ref(context)[1]

   # Register the factory
   >>> ipopo.register_factory(context, Component)
   True

   # Instantiate the component
   >>> instance = ipopo.instantiate('MyFactory', 'MyInstance')
   
   # Test services presence: we have two different services (different IDs)
   >>> [str(ref) for ref in context.get_all_service_references('service.test_1', None)]
   ["ServiceReference(ID=3, Bundle=0, Specs=['service.test_1'])"]
   >>> [str(ref) for ref in context.get_all_service_references('service.test_2', None)]
   ["ServiceReference(ID=2, Bundle=0, Specs=['service.test_2'])"]
   
   # Show service properties
   >>> ref_1 = context.get_all_service_references('service.test_1', None)[0]
   >>> ref_2 = context.get_all_service_references('service.test_2', None)[0]
   >>> print ref_1.get_properties()
   {'some.property': 42, 'instance.name': 'MyInstance', 'service.id': 3, 'objectClass': ['service.test_1']}
   >>> print ref_2.get_properties()
   {'some.property': 42, 'instance.name': 'MyInstance', 'service.id': 2, 'objectClass': ['service.test_2']}
   
   # Get the services
   >>> svc_1 = context.get_service(ref_1)
   >>> svc_2 = context.get_service(ref_2)
   
   # The component instance provides both services:
   # we can use either instance, svc_1 or svc_2 to access the same object
   >>> instance is svc_1 and instance is svc_2 and svc_1 is svc_2
   True

   # Change component property
   >>> svc_1.change_property(128)
   >>> print ref_1.get_properties()
   {'some.property': 128, 'instance.name': 'MyInstance', 'service.id': 3, 'objectClass': ['service.test_1']}
   >>> print ref_2.get_properties()
   {'some.property': 128, 'instance.name': 'MyInstance', 'service.id': 2, 'objectClass': ['service.test_2']}
   
   # Change controller value
   >>> instance.change_controller(False)
   >>> [str(ref) for ref in context.get_all_service_references('service.test_1', None)]
   ["ServiceReference(ID=3, Bundle=0, Specs=['service.test_1'])"]
   >>> context.get_all_service_references('service.test_2', None)
   >>> # No match found: get_all_service_references returns None
   
   # Reset controller value
   >>> instance.change_controller(True)
   >>> [str(ref) for ref in context.get_all_service_references('service.test_1', None)]
   ["ServiceReference(ID=3, Bundle=0, Specs=['service.test_1'])"]
   >>> context.get_all_service_references('service.test_2', None)
   [<pelix.framework.ServiceReference object at 0x21721d0>]
   >>> [str(ref) for ref in context.get_all_service_references('service.test_2', None)]
   ["ServiceReference(ID=4, Bundle=0, Specs=['service.test_2'])"]
   >>> # Service came back
   
   # WARNING: the service has been registered a second time, which means it
   # will have a different reference:
   >>> ref_3 = context.get_all_service_references('service.test_2', None)[0]
   >>> ref_3 is ref_2
   False
   
   # Unget the services
   >>> context.unget_service(ref_1)
   True
   
   # Unget service never raises exceptions, even when using old references
   >>> context.unget_service(ref_2)
   False
   
   # Stop the framework
   # It will stop the iPOPO bundle which will kill the component instance
   # and unregister its factory.
   >>> framework.stop()
   True
   
   # Delete it
   >>> pelix.framework.FrameworkFactory.delete_framework(framework)
   True
   
   # Don't forget to clean up variables references
   >>> instance = svc_1 = svc_2 = None
   >>> ref_1 = ref_2 = ref_3 = None
   >>> framework = None
   # Python interpreter is clean


Now you known how to run a Pelix framework, how to use the iPOPO service and
how to write iPOPO components.

You can go further by reading the next section, explaining how the class
manipulation works.
