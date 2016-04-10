# -*- coding: utf-8 -*-

# This file is part of Argos.
#
# Argos is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Argos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Argos. If not, see <http://www.gnu.org/licenses/>.

""" Configuration Tree Items for use in PyQtGraph-based inspectors
"""
from __future__ import division, print_function

import logging
import numpy as np

from libargos.config.groupcti import GroupCti
from libargos.config.boolcti import BoolCti
from libargos.config.choicecti import ChoiceCti
from libargos.config.floatcti import SnFloatCti
from libargos.config.untypedcti import UntypedCti
from libargos.info import DEBUGGING
from libargos.utils.cls import check_class

logger = logging.getLogger(__name__)


class ViewBoxDebugCti(GroupCti): # TODO: somehow don't save the state for this class
    """ Read-only config tree for inspecting a PyQtGraph ViewBox
    """
    def __init__(self, nodeName, viewBox, expanded=False):

        super(ViewBoxDebugCti, self).__init__(nodeName, expanded=expanded)

        self.viewBox = viewBox

        self.insertChild(UntypedCti("targetRange", [[0,1], [0,1]],
            doc="Child coord. range visible [[xmin, xmax], [ymin, ymax]]"))

        self.insertChild(UntypedCti("viewRange", [[0,1], [0,1]],
            doc="Actual range viewed"))

        self.insertChild(UntypedCti("xInverted", None))
        self.insertChild(UntypedCti("yInverted", None))
        self.insertChild(UntypedCti("aspectLocked", False,
            doc="False if aspect is unlocked, otherwise float specifies the locked ratio."))
        self.insertChild(UntypedCti("autoRange", [True, True],
            doc="False if auto range is disabled, otherwise float gives the fraction of data that is visible"))
        self.insertChild(UntypedCti("autoPan", [False, False],
            doc="Whether to only pan (do not change scaling) when auto-range is enabled"))
        self.insertChild(UntypedCti("autoVisibleOnly", [False, False],
            doc="Whether to auto-range only to the visible portion of a plot"))
        self.insertChild(UntypedCti("linkedViews", [None, None],
            doc="may be None, 'viewName', or weakref.ref(view) a name string indicates that the view *should* link to another, but no view with that name exists yet."))
        self.insertChild(UntypedCti("mouseEnabled", [None, None]))
        self.insertChild(UntypedCti("mouseMode", None))
        self.insertChild(UntypedCti("enableMenu", None))
        self.insertChild(UntypedCti("wheelScaleFactor", None))
        self.insertChild(UntypedCti("background", None))

        self.limitsItem = self.insertChild(GroupCti("limits"))
        self.limitsItem.insertChild(UntypedCti("xLimits", [None, None],
            doc="Maximum and minimum visible X values "))
        self.limitsItem.insertChild(UntypedCti("yLimits", [None, None],
            doc="Maximum and minimum visible Y values"))
        self.limitsItem.insertChild(UntypedCti("xRange", [None, None],
            doc="Maximum and minimum X range"))
        self.limitsItem.insertChild(UntypedCti("yRange", [None, None],
            doc="Maximum and minimum Y range"))


    def _refreshNodeFromTarget(self):
        """ Updates the config settings
        """
        for key, value in self.viewBox.state.items():
            if key != "limits":
                childItem = self.childByNodeName(key)
                childItem.data = value
            else:
                # limits contains a dictionary as well
                for limitKey, limitValue in value.items():
                    limitChildItem = self.limitsItem.childByNodeName(limitKey)
                    limitChildItem.data = limitValue


#
# class PgAxisRangeCti(GroupCti):
#     """ Configuration tree item is linked to the axis range.
#         Can toggle the axis' auto-range property on/off by means of checkbox
#     """
#     def __init__(self, viewBox, axisNumber, nodeName='range'):
#         """ Constructor.
#             The monitored axis is specified by viewBox and axisNumber (0 for x-axis, 1 for y-axis)
#         """
#         super(PgAxisRangeCti, self).__init__(nodeName)
#         assert axisNumber in (0, 1), "axisNumber must be 0 or 1"
#         self.viewBox = viewBox
#         self.axisNumber = axisNumber
#
#         self.rangeMinItem = self.insertChild(SnFloatCti('min', 0.0))
#         self.rangeMaxItem = self.insertChild(SnFloatCti('max', 1.0))
#         self.autoRangeItem = self.insertChild(BoolCti("auto-range", True))
#
#
#     def _refreshNodeFromTarget(self):
#         """ Refreshes the config values from the axes' state
#         """
#         # Set the precision from by looking how many decimals are neede to show the difference
#         # between the minimum and maximum, given the maximum. E.g. if min = 0.04 and max = 0.07,
#         # we would only need zero decimals behind the point as we can write the range as
#         # [4e-2, 7e-2]. However if min = 1.04 and max = 1.07, we need 2 decimals behind the point.
#         # So while the range is the same size, we need more decimals because we are not zoomed in
#         # around zero.
#         rangeMin, rangeMax = self.viewBox.state['viewRange'][self.axisNumber]
#         maxOrder = int(np.log10(np.abs(max(rangeMax, rangeMin))))
#         diffOrder = int(np.log10(np.abs(rangeMax - rangeMin)))
#
#         extraDigits = 2 # add some extra digits to make each pan/zoom action show a difference.
#         precision = min(25, max(extraDigits + 1, abs(maxOrder - diffOrder) + extraDigits)) # clip
#         #logger.debug("maxOrder: {}, diffOrder: {}, precision: {}"
#         #             .format(maxOrder, diffOrder, precision))
#
#         self.rangeMinItem.precision = precision
#         self.rangeMaxItem.precision = precision
#
#         self.rangeMinItem.data, self.rangeMaxItem.data = rangeMin, rangeMax
#         autoRangeEnabled = bool(self.viewBox.autoRangeEnabled()[self.axisNumber])
#
#         #logger.debug("PgAxisRangeCti.refresh: axis {}, {}".format(self.axisNumber, autoRangeEnabled))
#         self.rangeMinItem.enabled = not autoRangeEnabled
#         self.rangeMaxItem.enabled = not autoRangeEnabled
#         #self.autoRangeItem.data = autoRangeEnabled
#
#         self.model.emitDataChanged(self)
#
#
#     def getRange(self):
#         """Returns a tuple with the min and max range
#         """
#         return (self.rangeMinItem.data, self.rangeMaxItem.data)
#
#
#     def _setAutoRange(self):
#         """ Sets the auto range
#         """
#         autoRange = self.autoRangeItem.configValue
#         logger.debug("enableAutoRange: axis {}, {}".format(self.axisNumber, autoRange))
#         #assert False, "stopped"
#
#         if autoRange:
#             self.viewBox.enableAutoRange(self.axisNumber, autoRange)
#         else:
#             if self.axisNumber == self.viewBox.XAxis:
#                 xRange, yRange = self.getRange(), None
#             else:
#                 xRange, yRange = None, self.getRange()
#
#             logger.debug("setRange: xRange={}, yRange={}".format(xRange, yRange))
#
#             # viewBox.setRange doesn't accept an axis number :-(
#             self.viewBox.setRange(xRange = xRange, yRange=yRange,
#                                   padding=0, update=False, disableAutoRange=True)
#
#
#     def _updateTargetFromNode(self):
#         """ Applies the configuration to the target axis it monitors.
#         """
#         self._setAutoRange()
#
#


class PgAxisLabelCti(ChoiceCti):
    """ Configuration tree item is linked to the axis label.
    """
    VALID_AXIS_POSITIONS =  ('left', 'right', 'bottom', 'top')

    def __init__(self, plotItem, axisPosition, collector,
                 nodeName='label', defaultData=0, configValues=None):
        """ Constructor
            :param plotItem:
            :param axisPosition: 'left', 'right', 'bottom', 'top'
            :param collector: needed to get the collector.getRtiInfo
            :param nodeName: the nod name of this config tree item (default = label
            :param defaultData:
            :param configValues:
        """
        super(PgAxisLabelCti, self).__init__(nodeName, editable=True,
                                             defaultData=defaultData, configValues=configValues)
        assert axisPosition in self.VALID_AXIS_POSITIONS, \
            "axisPosition must be in {}".format(self.VALID_AXIS_POSITIONS)
        self.collector = collector
        self.plotItem = plotItem
        self.axisPosition = axisPosition


    def _updateTargetFromNode(self):
        """ Applies the configuration to the target axis it monitors.
        """
        rtiInfo = self.collector.getRtiInfo()
        self.plotItem.setLabel(self.axisPosition, self.configValue.format(**rtiInfo))



class PgAxisRangeCti(GroupCti):
    """ Configuration tree item is linked to the axis range.
        Can toggle the axis' auto-range property on/off by means of checkbox
    """
    def __init__(self, plotItem, axisNumber, nodeName='range'):
        """ Constructor.
            The monitored axis is specified by viewBox and axisNumber (0 for x-axis, 1 for y-axis)
        """
        super(PgAxisRangeCti, self).__init__(nodeName)
        assert axisNumber in (0, 1), "axisNumber must be 0 or 1"
        self.plotItem = plotItem
        self.viewBox = plotItem.getViewBox()
        self.axisNumber = axisNumber

        self.rangeMinItem = self.insertChild(SnFloatCti('min', 0.0))
        self.rangeMaxItem = self.insertChild(SnFloatCti('max', 1.0))
        self.autoRangeItem = self.insertChild(BoolCti("auto-range", True))

        #logger.debug("Disconnecting: autoBtn.clicked(self.autoBtnClicked)")
        #self.plotItem.autoBtn.clicked.disconnect(self.plotItem.autoBtnClicked)

        # Connect signals
        self.plotItem.autoBtn.clicked.connect(self._turnAutoRangeOn)
        self.viewBox.sigRangeChangedManually.connect(self._setAutoRangeOff)


    def _closeResources(self):
        """ Disconnects signals.
            Is called by self.finalize when the cti is deleted.
        """
        self.plotItem.autoBtn.clicked.disconnect(self._turnAutoRangeOn)
        self.viewBox.sigRangeChangedManually.disconnect(self._setAutoRangeOff)


    def _refreshNodeFromTarget(self, *args, **kwargs):
        """ Refreshes the configuration from the target it monitors (if present).
            The default implementation does nothing; subclasses can override it.
            During updateTarget's execution refreshFromTarget is blocked to avoid loops.

            The *args and **kwargs arguments are ignored but make it possible to use this as a slot
            for signals with arguments.
        """
        logger.debug("  {}._refreshNodeFromTarget: {} {}".format(self.nodePath, args, kwargs))
        self._refreshAutoRange()
        self._refreshMinMax(self.viewBox, self.viewBox.state['viewRange'])


    def _refreshMinMax(self, viewBox, ranges):
        """ Refreshes the min max config values from the axes' state.

            ranges = [[xmin, xmax], [ymin, ymax]]
        """
        # Set the precision from by looking how many decimals are neede to show the difference
        # between the minimum and maximum, given the maximum. E.g. if min = 0.04 and max = 0.07,
        # we would only need zero decimals behind the point as we can write the range as
        # [4e-2, 7e-2]. However if min = 1.04 and max = 1.07, we need 2 decimals behind the point.
        # So while the range is the same size, we need more decimals because we are not zoomed in
        # around zero.
        assert viewBox == self.viewBox, \
            "sanity check failed: {} != {}".format(viewBox, self.viewBox)

        rangeMin, rangeMax = ranges[self.axisNumber]
        logger.debug("    _refreshMinMax: {}, {}".format(rangeMin, rangeMax))

        maxOrder = int(np.log10(np.abs(max(rangeMax, rangeMin))))
        diffOrder = int(np.log10(np.abs(rangeMax - rangeMin)))

        extraDigits = 2 # add some extra digits to make each pan/zoom action show a difference.
        precision = min(25, max(extraDigits + 1, abs(maxOrder - diffOrder) + extraDigits)) # clip
        #logger.debug("maxOrder: {}, diffOrder: {}, precision: {}"
        #             .format(maxOrder, diffOrder, precision))

        self.rangeMinItem.precision = precision
        self.rangeMaxItem.precision = precision
        self.rangeMinItem.data, self.rangeMaxItem.data = rangeMin, rangeMax

        # Update values in the tree
        self.model.emitDataChanged(self.rangeMinItem)
        self.model.emitDataChanged(self.rangeMaxItem)


    def _refreshAutoRange(self):
        """ The min and max config items will be disabled if auto range is on.
        """
        enabled = self.autoRangeItem.configValue
        logger.debug("    _refreshAutoRange: enabled={}".format(enabled))
        self.rangeMinItem.enabled = not enabled
        self.rangeMaxItem.enabled = not enabled
        self.model.emitDataChanged(self)


    def _turnAutoRangeOn(self):
        """ Turns on the auto range checkbox.
        """
        # We don't need to update the target. It is assumed that the the viewbox auto button is
        # still connected to viewBox.autoBtnClicked, which updates the range. # TODO: this is not yet True
        self.autoRangeItem.data = True
        self._refreshNodeFromTarget()


    def _setAutoRangeOff(self):
        """ Turns off the auto range checkbox.
        """
        self.autoRangeItem.data = False
        self._refreshNodeFromTarget()


    def getRange(self):
        """Returns a tuple with the min and max range
        """
        return (self.rangeMinItem.data, self.rangeMaxItem.data)


    def _updateTargetFromNode(self):
        """ Applies the configuration to the target axis it monitors.
        """
        autoRange = self.autoRangeItem.configValue
        logger.debug("enableAutoRange: axis {}, {}".format(self.axisNumber, autoRange))

        if autoRange:
            padding = None # PyQtGraph default: between 0.02 and 0.1 dep. on the size of the ViewBox
            rect = self.viewBox.childrenBoundingRect() # taken from viewBox.autoRange()
            if rect is not None:
                if self.axisNumber == self.viewBox.XAxis:
                    xRange, yRange = (rect.left(), rect.right()), None
                else:
                    xRange, yRange = None, (rect.bottom(), rect.top())
            else:
                logger.warn("No children bbox. Plot range not updated.") # does this happen?
                return
        else:
            padding = 0
            if self.axisNumber == self.viewBox.XAxis:
                xRange, yRange = self.getRange(), None
            else:
                xRange, yRange = None, self.getRange()

        # viewBox.setRange doesn't accept an axis number :-(
        logger.debug("setRange: xRange={}, yRange={}, padding={}".format(xRange, yRange, padding))
        self.viewBox.setRange(xRange = xRange, yRange=yRange, padding=padding,
                              update=False, disableAutoRange=True)



class PgAxisCti(GroupCti):
    """ Configuration tree item for a PyQtGraph plot axis.

        This CTI is intended to be used as a child of a PgPlotItemCti.
    """
    def __init__(self, nodeName, plotItem, axisNumber):
        """ Constructor
        """
        super(PgAxisCti, self).__init__(nodeName)

        assert axisNumber in (0, 1), "axisNumber must be 0 or 1"
        self.plotItem = plotItem
        self.axisNumber = axisNumber

        #self.insertChild(BoolCti("show", True)) # TODO:
        #self.insertChild(BoolCti('logarithmic', False))

        self.rangeItem = self.insertChild(PgAxisRangeCti(self.plotItem, self.axisNumber))



class PgPlotItemCti(GroupCti):
    """ Config tree item for manipulating a PyQtGraph.PlotItem
    """
    def __init__(self, plotItem, nodeName='axes', xAxisCti=None, yAxisCti=None):
        """ Constructor
        """
        super(PgPlotItemCti, self).__init__(nodeName)

        #check_class(plotItem, (PlotItem, SimplePlotItem) # TODO
        assert plotItem, "target plotItem is undefined"

        self.aspectItem = self.insertChild(BoolCti("lock aspect ratio", False))
        self.plotItem = plotItem
        viewBox = plotItem.getViewBox()

        # Keeping references to the axes CTIs because they need to be updated quickly when
        # the range changes; getting by path may be slow.)
        if xAxisCti is None:
            self.xAxisCti = self.insertChild(PgAxisCti('x-axis', plotItem, 0))
        else:
            check_class(xAxisCti, PgAxisCti)
            self.xAxisCti = self.insertChild(xAxisCti)

        if yAxisCti is None:
            self.yAxisCti = self.insertChild(PgAxisCti('y-axis', plotItem, 1))
        else:
            check_class(yAxisCti, PgAxisCti)
            self.yAxisCti = self.insertChild(yAxisCti)

        if DEBUGGING:
            self.stateItem = self.insertChild(ViewBoxDebugCti('viewbox state', viewBox))
        else:
            self.stateItem = None

        # Connect signals
        if DEBUGGING:
            viewBox = self.plotItem.getViewBox()
            viewBox.sigStateChanged.connect(self.vbStateChanged)
            viewBox.sigRangeChanged.connect(self.vbRangeChanged)
            viewBox.sigXRangeChanged.connect(self.vbXRangeChanged)
            viewBox.sigYRangeChanged.connect(self.vbYRangeChanged)
            viewBox.sigRangeChangedManually.connect(self.vbRangeChangedManually)

    def _closeResources(self):
        """ Disconnects signals.
            Is called by self.finalize when the cti is deleted.
        """
        if DEBUGGING:
            viewBox = self.plotItem.getViewBox()
            viewBox.sigStateChanged.disconnect(self.vbStateChanged)
            viewBox.sigRangeChanged.disconnect(self.vbRangeChanged)
            viewBox.sigXRangeChanged.disconnect(self.vbXRangeChanged)
            viewBox.sigYRangeChanged.disconnect(self.vbYRangeChanged)
            viewBox.sigRangeChangedManually.disconnect(self.vbRangeChangedManually)


    def vbStateChanged(self, *args, **kwargs):
        #logger.debug("viewBox state changed: {} {}".format(args, kwargs))
        pass

    def vbRangeChanged(self, *args, **kwargs):
        #logger.debug("viewBox range changed: {} {}".format(args, kwargs))
        pass

    def vbXRangeChanged(self, *args, **kwargs):
        #logger.debug("viewBox X-range changed: {} {}".format(args, kwargs))
        pass

    def vbYRangeChanged(self, *args, **kwargs):
        #logger.debug("viewBox Y-range changed: {} {}".format(args, kwargs))
        pass

    def vbRangeChangedManually(self, *args, **kwargs):
        #logger.debug("viewBox range changed manually: {} {}".format(args, kwargs))
        pass
