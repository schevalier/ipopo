#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Simple bundle with an activator (no service registered).

:author: Thomas Calmant
"""
from pelix.framework import BundleContext, FrameworkException

__version__ = (1, 0, 0)

started = False
stopped = False
raiser = False
fw_raiser = False
fw_raiser_stop = False

class ActivatorTest:
    """
    Test activator
    """

    def __init__(self):
        """
        Constructor
        """
        self.context = None


    def start(self, context):
        """
        Bundle started
        """
        assert isinstance(context, BundleContext)
        self.context = context

        if fw_raiser:
            raise FrameworkException("Framework Exception", fw_raiser_stop)

        if raiser:
            raise Exception("Some exception")

        global started
        started = True


    def stop(self, context):
        """
        Bundle stopped
        """
        assert isinstance(context, BundleContext)
        assert self.context is context

        if fw_raiser:
            raise FrameworkException("Framework Exception", fw_raiser_stop)

        if raiser:
            raise Exception("Some exception")

        global stopped
        stopped = True

# Prepare the activator
activator = ActivatorTest()
