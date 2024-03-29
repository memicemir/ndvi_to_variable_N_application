# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NDVIandEVIindexCalculator
                                 A QGIS plugin
 This plugin calculates NDVI and EVI index from Sentinel 2 B02, B04 and B08 Bands.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-03-25
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Emir Memic
        email                : emir_memic@windowslive.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .ndvi_and_evi_index_calculator_dialog import NDVIandEVIindexCalculatorDialog
import os.path

# me
from qgis.utils import reloadPlugin
import processing
from osgeo import gdal
from qgis.core import *
from qgis.utils import *
import re
from datetime import datetime

from qgis.PyQt.QtWidgets import QMessageBox

from difflib import SequenceMatcher
from PyQt5.QtWidgets import *
#from PyQt5 import QtWidgets

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import *

class NDVIandEVIindexCalculator:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'NDVIandEVIindexCalculator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&NDVI and EVI Index Calculator')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('NDVIandEVIindexCalculator', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ndvi_and_evi_index_calculator/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'NDVI and EVI index calculator'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&NDVI and EVI Index Calculator'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = NDVIandEVIindexCalculatorDialog()

        #### me-start
        reloadPlugin('ndvi_and_evi_index_calculator')
        print ('run ndvi and evi calculator')

        self.dlg.progressBar.setValue(1)

        self.dlg.listWidget.clear()
        self.dlg.listWidget_2.clear()
        self.dlg.listWidget_3.clear()     
        
        # i dont know if this makes any sense ...
        self.dlg.checkBox.clicked.connect(self.run)        
        if self.dlg.checkBox.isChecked():
            self.dlg.lineEdit_2.textChanged.connect(self.run)
        
        self.dlg.pushButton.clicked.connect(self.guide_to_user)
        self.dlg.pushButton_4.clicked.connect(self.calculate_ndvi)
        self.dlg.pushButton_2.clicked.connect(self.calculate_evi)
        self.dlg.pushButton_3.clicked.connect(self.select_output_directory)
        self.dlg.listWidget.clicked.connect(self.select_file_and_dir)
        #self.dlg.listWidget.currentItemChanged.connect(self.select_file_and_dir)

        # add available layers into interface
        layers = self.iface.mapCanvas().layers()
        listOfLayersB08 = []
        listOfLayersB04 = []
        listOfLayersB02 = []

        for layer in layers:
            if 'B08' in str(layer.name()) or 'NIR' in str(layer.name()):
                listOfLayersB08.append(str(layer.name()))
            if 'B04' in str(layer.name()) or 'RED' in str(layer.name()):
                listOfLayersB04.append(str(layer.name()))              
            if 'B02' in str(layer.name()) or 'BLUE' in str(layer.name()):
                listOfLayersB02.append(str(layer.name()))
                
            QCoreApplication.processEvents()
        self.dlg.listWidget.addItems(listOfLayersB08)
        self.dlg.listWidget_2.addItems(listOfLayersB04)
        self.dlg.listWidget_3.addItems(listOfLayersB02)        

        countListWidget = len(listOfLayersB08)
        countListWidget_2 = len(listOfLayersB04)
        countListWidget_3 = len(listOfLayersB02)        
        print ('countListWidget', countListWidget)
        print ('countListWidget_2', countListWidget_2)
        print ('countListWidget_3', countListWidget_3)        

        # alphabetically sort qglistweidte elements to enable index based selection later
        self.dlg.listWidget.sortItems()
        self.dlg.listWidget_2.sortItems()
        self.dlg.listWidget_3.sortItems()  

        if int(countListWidget) != int(countListWidget_3) and self.dlg.checkBox.isChecked():
            
            newListWidget3List = []
            self.dlg.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.dlg.listWidget.selectAll()

            for selectedImage in self.dlg.listWidget.selectedItems():
                elementCheck = selectedImage.text()
                itemAddMe = 'Missing-B02'
                print (' add missing')
                for ii in range(0, int(countListWidget_3)):
                    elementCheckN = listOfLayersB02[ii]

                    checkSimilarity = SequenceMatcher(None, elementCheck, elementCheckN).ratio()
                    if float(checkSimilarity) > float(self.dlg.lineEdit_2.text()): #0.95:
                        print ('checkSimilarity', checkSimilarity)
                        itemAddMe = elementCheckN
                        
                newListWidget3List.append(str(itemAddMe))
            print ('newListWidget3List', newListWidget3List)
            self.dlg.listWidget_3.clear()
            self.dlg.listWidget_3.addItems(newListWidget3List)    
            self.dlg.listWidget.setSelectionMode(QAbstractItemView.SingleSelection)
            
        self.dlg.listWidget.setCurrentRow(0)
        self.dlg.listWidget_2.setCurrentRow(0)
        self.dlg.listWidget_3.setCurrentRow(0)

        if not self.dlg.checkBox.isChecked():        
            self.dlg.listWidget_3.clear()

        try:        
            selectedLayerB08 = str(self.dlg.listWidget.currentItem().text())            
            polygonLayerB08 = QgsProject.instance().mapLayersByName(selectedLayerB08)[0] 
            mePath = polygonLayerB08.dataProvider().dataSourceUri()
            mePath = mePath.strip('/vsizip/')
            mePath = os.path.normpath(mePath)
            mePath = os.path.dirname(os.path.dirname(mePath))
            print ('mePath', mePath)            
            try:
                os.mkdir(mePath + '\ProcessedOutputs')
            except:
                print ('dir exist')
            setPathMe = mePath + '\ProcessedOutputs'
            self.dlg.lineEdit.setText(setPathMe)
            print ('setPathMe input image', setPathMe)            
        except:
            QMessageBox.warning(None, 'Images not found in QGIS Layers window!', 'Add/drag images (e.g. .zip) to the QGIS Layers window. If the images are there but not recognised, contact the author of the QGIS plugin!')
        #self.dlg.listWidget.setCurrentRow(0)
        #self.dlg.listWidget_2.setCurrentRow(0)
        #self.dlg.listWidget_3.setCurrentRow(0)
            
        #### me-end

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def guide_to_user(self):
        QMessageBox.information(None, 'Guide to user!', 
        'Three input layer windows show uploaded Bands in this plugin: Input layer 1. (B08 - Near Infrared), Input layer 2. (B04 - Red) and Input layer 3. (B02 - Blue)\n\n'
        + 'If everything went well with upload, the selection (Mouse left click) of image band in Input layer 1. will automatically find matches in Input layer 2. and 3. windows (if PC or QGIS is slow, then wait until matchis in Input layer 2. and 3. are selected).\n\n'
        + 'Only layer selection in Input layer 1. window will automatically match pairs in Input layer 2. and 3. The user can manually select matches in Input layer 1., 2., and 3. (Mouse left click).\n\n'
        + 'One selection at the time should be used for calculating NDVI or EVI with calculate NDVI and EVI pushbutton.\n\n'        
        + 'Multi-selection based index calculation will be implemented in the next version, if requested.\n\n\n\n'        

        + 'To get images use your internet browser to access Coprnicus Browser and satellite images by following instructions:\n\n'
        + '1. Copernicus Browser - Create account and login.\n\n'
        + '2. In Coprenicus Browser toolbar (right side) - in the field "Create an area of intrest" -> deliniate polygon of area of interest.\n\n'
        + '3. In Coprenicus Browser toolbar (right side) - "Download image" -> Analytical:\n'
        + '     a) Image format: TIFF(32-bit float) \n'
        + '     b) Image resolution: HIGH\n'
        + '     c) Coordinate system: WGS84(EPSG:4326) (in my case)\n'
        + '     d) Clip extra bands -> uncheck this option!\n'
        + '     e) Layers -> Raw (check only -> B02, B04 and B08)\n'
        + '     d) Download (as zip file)\n\n'
        
        + 'After downloading images and loading them into QGIS Layers legend and restaring this QGIS plugin, the images will appear in QGIS plugin list widget for selection and NDVI, EVI calculations!'        
        )        

    def select_output_directory(self):
        ###### print 'find directroy'
        selectWorkingDir = QFileDialog.getExistingDirectory()
        selectWorkingDir = os.path.normpath(selectWorkingDir)
        print ('selected dir', selectWorkingDir)
        
        try:
            os.mkdir(selectWorkingDir + '\ProcessedOutputs')
        except:
            print ('dir exist')
            
        selectWorkingDir = selectWorkingDir + '\ProcessedOutputs'
    
        self.dlg.lineEdit.setText(selectWorkingDir)

    def select_file_and_dir(self):
        print ('calculate index')
  
        self.dlg.progressBar.setValue(1)
        selectedLayerB08 = str(self.dlg.listWidget.currentItem().text())            
        polygonLayerB08 = QgsProject.instance().mapLayersByName(selectedLayerB08)[0] 

        # mePath = polygonLayerB08.dataProvider().dataSourceUri()
        # mePath = mePath.strip('/vsizip/')
        # mePath = os.path.normpath(mePath)
        # mePath = os.path.dirname(os.path.dirname(mePath))
        # print ('mePath', mePath)
        self.dlg.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dlg.listWidget.selectAll()
        counterMe = 0 
        for selectedImage in self.dlg.listWidget.selectedItems():
            selectedLayer1 = selectedImage.text()
            print ('selectedLayer1', selectedLayer1)
            counterMe = counterMe + 1 
            if selectedLayerB08 == selectedLayer1:
                print ('index', counterMe)
                counterMeUse = counterMe
        counterMeUse = counterMeUse - 1
        print ('index to use:', counterMe) 
        self.dlg.listWidget.setSelectionMode(QAbstractItemView.SingleSelection)

        self.dlg.listWidget.clearSelection()
        self.dlg.listWidget.setCurrentRow(counterMeUse)
        self.dlg.listWidget_2.setCurrentRow(counterMeUse)
        self.dlg.listWidget_3.setCurrentRow(counterMeUse)        

        #selectedLayerB08 = str(self.dlg.listWidget.currentItem())
        #selectedLayerB04 = str(self.dlg.listWidget_2.currentItem())
        try:
            selectedLayerB02 = self.dlg.listWidget_3.currentItem().text()
        except:
            selectedLayerB02 = self.dlg.listWidget_3.currentItem()
        print ('selectedLayerB02', selectedLayerB02)
        if str(selectedLayerB02) == 'Missing-B02' or  selectedLayerB02 is None:
            print ('block acces to the evi')
            self.dlg.pushButton_2.setEnabled(False)
        else:
            self.dlg.pushButton_2.setEnabled(True)


    def calculate_ndvi(self):

        myfilepath = str(self.dlg.lineEdit.text()) 
        print ('myfilepath input image', myfilepath) 

        selectedLayerB08 = str(self.dlg.listWidget.currentItem().text())            
        polygonLayerB08 = QgsProject.instance().mapLayersByName(selectedLayerB08)[0] 
    
        selectedLayerB04 = str(self.dlg.listWidget_2.currentItem().text())            
        polygonLayerB04 = QgsProject.instance().mapLayersByName(selectedLayerB04)[0]  

        print ('polygonLayerB08', polygonLayerB08)
        print ('polygonLayerB04', polygonLayerB04)
        
        match = re.search(r'\d{4}-\d{2}-\d{2}', selectedLayerB08)
        date = datetime.strptime(match.group(), '%Y-%m-%d').date()
        print ('date', date)
        
        dateName = str(date).split('-')[1] + '-' + str(date).split('-')[2] + '-' + str(date).split('-')[0]
        print ('dateName', dateName)

################

        self.dlg.progressBar.setValue(1)
        progress = 0 
        self.dlg.progressBar.setMinimum(progress)
        self.dlg.progressBar.setMaximum(progress)
        self.dlg.progressBar.setValue(progress)
        
        def progress_changed(progress):
            print(progress)
            self.dlg.progressBar.setMaximum(100)
            self.dlg.progressBar.setValue(progress)
            #QCoreApplication.processEvents()

        f = QgsProcessingFeedback()
        f.progressChanged.connect(progress_changed)        
        
################

        processing.runAndLoadResults("gdal:rastercalculator", 
        {'INPUT_A': polygonLayerB08, 
         'BAND_A':1,
         'INPUT_B': polygonLayerB04,  
         'BAND_B':1,
         'FORMULA':'(A-B)/(A+B)',
         'NO_DATA':None,
         'RTYPE':5,
         'OPTIONS':'',
         'EXTRA':'',
         'OUTPUT':'{}/ndvi_{}.tiff'.format(myfilepath, dateName)
         }, feedback=f)   
        
         
    def calculate_evi(self):
        print ('calculate index')

        myfilepath = str(self.dlg.lineEdit.text()) 
        print ('myfilepath input image', myfilepath) 
        
        selectedLayerB08 = str(self.dlg.listWidget.currentItem().text())            
        polygonLayerB08 = QgsProject.instance().mapLayersByName(selectedLayerB08)[0] 

        selectedLayerB04 = str(self.dlg.listWidget_2.currentItem().text())            
        polygonLayerB04 = QgsProject.instance().mapLayersByName(selectedLayerB04)[0]  

        selectedLayerB02 = str(self.dlg.listWidget_3.currentItem().text())            
        polygonLayerB02 = QgsProject.instance().mapLayersByName(selectedLayerB02)[0]  

        print ('polygonLayerB08', polygonLayerB08)
        print ('polygonLayerB04', polygonLayerB04)
        
        match = re.search(r'\d{4}-\d{2}-\d{2}', selectedLayerB08)
        date = datetime.strptime(match.group(), '%Y-%m-%d').date()
        print ('date', date)
        
        dateName = str(date).split('-')[1] + '-' + str(date).split('-')[2] + '-' + str(date).split('-')[0]
        print ('dateName', dateName)

        
        ################

        self.dlg.progressBar.setValue(1)
        progress = 0 
        self.dlg.progressBar.setMinimum(progress)
        self.dlg.progressBar.setMaximum(progress)
        self.dlg.progressBar.setValue(progress)
        
        def progress_changed(progress):
            print(progress)
            self.dlg.progressBar.setMaximum(100)
            self.dlg.progressBar.setValue(progress)
            #QCoreApplication.processEvents()

        f = QgsProcessingFeedback()
        f.progressChanged.connect(progress_changed)        
        
################        

        processing.runAndLoadResults("gdal:rastercalculator", 
        {'INPUT_A': polygonLayerB08, 
         'BAND_A':1,
         'INPUT_B': polygonLayerB04, 
         'BAND_B':1,
         'INPUT_C': polygonLayerB02,  
         'BAND_C':1,         
         'FORMULA':'2.5*(A-B)/((A+6.0*B-7.5*C)+1.0)',
         'NO_DATA':None,
         'RTYPE':5,
         'OPTIONS':'',
         'EXTRA':'',
         'OUTPUT':'{}/evi_{}.tiff'.format(myfilepath, dateName)
         #'OUTPUT':outfile
         }, feedback=f) 
 