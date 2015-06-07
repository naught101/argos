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

""" Base class for inspectors
"""
import logging
from libargos.info import DEBUGGING
from libargos.qt import QtGui, QtSlot
from libargos.utils.cls import type_name
from libargos.widgets.constants import DOCK_SPACING, DOCK_MARGIN
from libargos.widgets.display import MessageDisplay

logger = logging.getLogger(__name__)



class AbstractInspector(QtGui.QStackedWidget):
    """ Abstract base class for inspectors.
        An inspector is a stacked widget; it has a contents page and and error page.
    """
    _fullName = "base" # see the fullName() class method for explanation
    ERROR_PAGE_IDX = 0
    CONTENTS_PAGE_IDX = 1
    
    def __init__(self, collector, parent=None):
        """ Constructor
            :param collector: the data collector from where this inspector gets its data
            :param parent: parent widget.
        """
        
        super(AbstractInspector, self).__init__(parent)
        
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        
        self._collector = collector
        
        self.errorWidget = MessageDisplay()
        self.addWidget(self.errorWidget)

        self.contentsWidget = QtGui.QWidget()
        self.addWidget(self.contentsWidget)

        self.contentsLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom)
        self.contentsLayout.setSpacing(DOCK_SPACING)
        self.contentsLayout.setContentsMargins(DOCK_MARGIN, DOCK_MARGIN, DOCK_MARGIN, DOCK_MARGIN)        
        self.contentsWidget.setLayout(self.contentsLayout)
        
        self.setCurrentIndex(self.CONTENTS_PAGE_IDX)

    def finalize(self):
        """ Is called before destruction. Can be used to clean-up resources
        """
        logger.debug("Finalizing: {}".format(self))

    
    @classmethod
    def descriptionHtml(cls):
        """ A long description that will be displayed as help in the inspector-open dialog box.
        """
        return ""    
    
    @classmethod
    def axesNames(cls):
        """ The names of the axes that this inspector visualizes.    
            
            This determines the dimensionality of the inspector (e.g. an inspector that shows
            an image, and has axes names 'X' and 'Y', is 2-dimensional.
            
            The names should not include the string "Axis"; the fullAxesNames returns that.
            The fullAxesNames are used by the data collector to create its combo boxes. 
        """
        return tuple()
    
    @classmethod
    def fullAxesNames(cls):
        """ The full names of the axes that this inspector visualizes.  
            
            This is the axis name plus the literal string '-Axis'. 
            
            Descendants do not need to override this method but should override axesNames instead.
            See also the axesNames documentation.
        """
        return tuple(axisName + '-Axis' for axisName in cls.axesNames())
    
    @property
    def collector(self):
        """ The data collector from where this inspector gets its data
        """
        return self._collector
        
    
    @QtSlot()
    def draw(self):
        """ Tries to draw the widget contents. 
            Shows the error page in case an exception is raised while drawing the contents.
        """
        logger.debug("Drawing inspector: {}".format(self))
        try:
            self.setCurrentIndex(self.CONTENTS_PAGE_IDX)
            self._drawContents()
        except Exception as ex:
            logger.error("Error while drawing the inspector: {}".format(ex))
            #logger.execption(ex)
            self.setCurrentIndex(self.ERROR_PAGE_IDX)
            self._drawError(msg=str(ex), title=type_name(ex))
            if DEBUGGING:
                raise
            
    
    def _drawContents(self):
        """ Draws the inspector widget contents.
            The default implementation shows an empty page (no widgets). Descendants should 
            override this.
        """
        raise NotImplementedError()
        

    def _drawError(self, msg="", title="Error"):
        """ Shows and error message.
        """
        self.errorWidget.setError(msg=msg, title=title)
        