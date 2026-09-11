# ****************************************************************************
# @file MyProject - main class
# @author Valentin Schmidt
# @version 0.1
# ****************************************************************************

import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#from PyQt5 import uic

APP_NAME = 'QPyMovieDB'
APP_VERSION = 1

PATH = os.path.dirname(os.path.realpath(__file__))


########################################
#
########################################
class Main(QMainWindow):

    # @constructor
    def __init__(self):
        super().__init__()

        # load UI
#        QResource.registerResource(os.path.join(PATH, 'resources', 'main.rcc'))
#        uic.loadUi(os.path.join(PATH, 'resources', 'main.ui'), self)

#        # setup statusBar
#        self._statusInfo = QLabel(self)
#        self._statusInfo.linkActivated.connect(lambda u: QDesktopServices.openUrl(QUrl(u)))
#        self.statusBar.addPermanentWidget(self._statusInfo)
#
#        # restore saved state
#        self._state = QSettings('fx', APP_NAME)
#        val = self._state.value('MainWindow/Geometry')
#        if val is not None:
#            self.restoreGeometry(val)
#        val = self._state.value('MainWindow/State')
#        if val is not None:
#            self.restoreState(val)
#
#        val = self._state.value('MainWindow/SplitterHState')
#        if val is not None:
#            self.splitterH.restoreState(val)
#        else: self.splitterH.setSizes([800, 200])
#        val = self._state.value('MainWindow/SplitterVState')
#        if val is not None:
#            self.splitterV.restoreState(val)
#        else:
#            self.splitterV.setSizes([500, 500])

        self.show()

########################################
#
########################################
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
