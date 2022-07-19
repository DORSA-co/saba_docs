from PySide6.QtCharts import QChart as sQChart
from PySide6.QtCharts import QChartView as sQChartView
from PySide6.QtCharts import QLineSeries as sQLineSeries
from PySide6.QtCharts import QScatterSeries as sQScatterSeries
from PySide6.QtCharts import QValueAxis as sQValueAxis
from PySide6.QtCore import QPointF as sQPointF
from PySide6.QtWidgets import QVBoxLayout as sQVBoxLayout
from PySide6.QtWidgets import QScrollBar as sQScrollBar
from PySide6 import QtCore as sQtCore
from PySide6.QtGui import QBrush as sQBrush
from PySide6.QtGui import QColor as sQColor
from PySide6.QtGui import QPen as sQPen
from PySide6.QtGui import QPainter as sQPainter
from PySide6.QtGui import QCursor as sQCursor
from PySide6.QtCharts import QBarSet as sQBarSet
from PySide6.QtCharts import QHorizontalStackedBarSeries as sQHorizontalStackedBarSeries
from PySide6.QtCharts import QBarCategoryAxis as sQBarCategoryAxis
from PySide6.QtCore import QMargins as sQMargins


import cv2
import numpy as np
import random
#import pyautogui

from . import storage_funcs, colors_pallete


# chart colors and appearance
train_color = '#1564FF'
val_color = '#FF0000'
pen_width = 4
marker_size = 12
animation_duration = 1000
axisX_range = 10
axisY_range = 100
# for test
global numepoch
numepoch = 30
global epochitr
epochitr = 0
load = np.arange(numepoch)
eff_train = [random.randint(0, 100) for _ in range(numepoch)]
eff_val = [random.randint(0, 100) for _ in range(numepoch)]


def create_train_chart_on_ui(ui_obj, frame_obj, hover_label_obj, checkbox_obj, chart_postfix, chart_title='chart', legend_train='legend1', legend_val='legend2',
                            axisX_title='epoch', axisY_title='Accuracy'):
    # horizintal scrollbar
    scrollbar = sQScrollBar(sQtCore.Qt.Horizontal, minimum=0, maximum=0, value=0, pageStep=1)
    # set scrollbar to ui
    eval("exec('ui_obj.scrollbar_%s = scrollbar')" % chart_postfix)
    # define chart
    chart = sQChart()
    chart.setTitle(chart_title)
    chart.legend().setVisible(True)
    chart.setBackgroundBrush(sQBrush(sQColor(255, 255, 255)))
    chart.setAnimationOptions(sQChart.AnimationOption.SeriesAnimations)
    chart.setAnimationDuration(animation_duration)
    chart.createDefaultAxes()
    # set chart to ui
    eval("exec('ui_obj.chart_%s = chart')" % chart_postfix)
    # ---------------------------------------------------------------------------
    # define training series
    #self.series = sQLineSeries()
    train_line_series = sQLineSeries()
    train_line_series.setName(legend_train)
    pen = sQPen()
    pen.setStyle(sQtCore.Qt.SolidLine)
    pen.setWidth(pen_width)
    pen.setColor(sQColor(train_color))
    train_line_series.setPen(pen)
    # scatterseries (for data points)
    train_scatter_series_1 = sQScatterSeries()
    train_scatter_series_1.setMarkerShape(sQScatterSeries.MarkerShapeCircle) #Circular point
    train_scatter_series_1.setBorderColor(sQColor(train_color)) #Discrete point border color
    train_scatter_series_1.setBrush(sQBrush(sQColor(train_color))) # Discrete point background color
    train_scatter_series_1.setMarkerSize(marker_size) # Discrete point size
    # scatterseries (for center of data points)
    train_scatter_series_2 = sQScatterSeries()
    train_scatter_series_2.setMarkerShape(sQScatterSeries.MarkerShapeCircle) # Circular point
    train_scatter_series_2.setBorderColor(sQColor(255, 255, 255)) # Border color
    train_scatter_series_2.setBrush(sQBrush(sQColor(255, 255, 255))) # background color 
    train_scatter_series_2.setMarkerSize(marker_size//2) # Point size
    # set series to ui
    eval("exec('ui_obj.train_line_series_%s = train_line_series')" % chart_postfix)
    eval("exec('ui_obj.train_scatter_series_1_%s = train_scatter_series_1')" % chart_postfix)
    eval("exec('ui_obj.train_scatter_series_2_%s = train_scatter_series_2')" % chart_postfix)
    # ---------------------------------------------------------------------------------
    # define validation series
    #self.series = sQLineSeries()
    val_line_series = sQLineSeries()
    val_line_series.setName(legend_val)
    pen = sQPen()
    pen.setStyle(sQtCore.Qt.SolidLine)
    pen.setWidth(pen_width)
    pen.setColor(sQColor(val_color))
    val_line_series.setPen(pen)
    # scatterseries (for data points)
    val_scatter_series_1 = sQScatterSeries()
    val_scatter_series_1.setMarkerShape(sQScatterSeries.MarkerShapeCircle) #Circular point
    val_scatter_series_1.setBorderColor(sQColor(val_color)) #Discrete point border color
    val_scatter_series_1.setBrush(sQBrush(sQColor(val_color))) # Discrete point background color
    val_scatter_series_1.setMarkerSize(marker_size) # Discrete point size
    # scatterseries (for center of data points)
    val_scatter_series_2 = sQScatterSeries()
    val_scatter_series_2.setMarkerShape(sQScatterSeries.MarkerShapeCircle) # Circular point
    val_scatter_series_2.setBorderColor(sQColor(255, 255, 255)) # Border color
    val_scatter_series_2.setBrush(sQBrush(sQColor(255, 255, 255))) # background color 
    val_scatter_series_2.setMarkerSize(marker_size//2) # Point size
    # set series to ui
    eval("exec('ui_obj.val_line_series_%s = val_line_series')" % chart_postfix)
    eval("exec('ui_obj.val_scatter_series_1_%s = val_scatter_series_1')" % chart_postfix)
    eval("exec('ui_obj.val_scatter_series_2_%s = val_scatter_series_2')" % chart_postfix)
    # --------------------------------------------------------------------------------------
    # define axis
    # X
    axisX = sQValueAxis()
    axisX.setRange(0, axisX_range)
    axisX.setLabelFormat("%.1f")
    axisX.setTickCount(axisX_range+1)
    axisX.setTitleText(axisX_title)
    eval("exec('ui_obj.axisX_%s = axisX')" % chart_postfix)
    # Y
    axisY = sQValueAxis()
    axisY.setRange(0, axisY_range)
    axisY.setLabelFormat("%d")
    axisY.setTickCount(axisY_range//10+1)
    axisY.setTitleText(axisY_title)
    eval("exec('ui_obj.axisY_%s = axisY')" % chart_postfix)
    # add axis to chart
    eval('ui_obj.chart_%s' % chart_postfix).addAxis(eval('ui_obj.axisX_%s' % chart_postfix), sQtCore.Qt.AlignBottom)
    eval('ui_obj.chart_%s' % chart_postfix).addAxis(eval('ui_obj.axisY_%s' % chart_postfix), sQtCore.Qt.AlignLeft)
    # --------------------------------------------------------------------------------------------------
    # define chartview
    chartview = sQChartView(eval('ui_obj.chart_%s' % chart_postfix))
    chartview.setRenderHint(sQPainter.Antialiasing)
    # -------------------------------------------------------------------------------------------------
    # add series to chart
    eval('ui_obj.chart_%s' % chart_postfix).addSeries(eval('ui_obj.train_line_series_%s' % chart_postfix))
    eval('ui_obj.chart_%s' % chart_postfix).addSeries(eval('ui_obj.train_scatter_series_1_%s' % chart_postfix))
    eval('ui_obj.chart_%s' % chart_postfix).addSeries(eval('ui_obj.train_scatter_series_2_%s' % chart_postfix))
    eval('ui_obj.chart_%s' % chart_postfix).addSeries(eval('ui_obj.val_line_series_%s' % chart_postfix))
    eval('ui_obj.chart_%s' % chart_postfix).addSeries(eval('ui_obj.val_scatter_series_1_%s' % chart_postfix))
    eval('ui_obj.chart_%s' % chart_postfix).addSeries(eval('ui_obj.val_scatter_series_2_%s' % chart_postfix))
    # attach axis
    eval('ui_obj.train_line_series_%s' % chart_postfix).attachAxis(eval('ui_obj.axisX_%s' % chart_postfix))
    eval('ui_obj.train_line_series_%s' % chart_postfix).attachAxis(eval('ui_obj.axisY_%s' % chart_postfix))
    eval('ui_obj.train_scatter_series_1_%s' % chart_postfix).attachAxis(eval('ui_obj.axisX_%s' % chart_postfix))
    eval('ui_obj.train_scatter_series_1_%s' % chart_postfix).attachAxis(eval('ui_obj.axisY_%s' % chart_postfix))
    eval('ui_obj.train_scatter_series_2_%s' % chart_postfix).attachAxis(eval('ui_obj.axisX_%s' % chart_postfix))
    eval('ui_obj.train_scatter_series_2_%s' % chart_postfix).attachAxis(eval('ui_obj.axisY_%s' % chart_postfix))
    eval('ui_obj.val_line_series_%s' % chart_postfix).attachAxis(eval('ui_obj.axisX_%s' % chart_postfix))
    eval('ui_obj.val_line_series_%s' % chart_postfix).attachAxis(eval('ui_obj.axisY_%s' % chart_postfix))
    eval('ui_obj.val_scatter_series_1_%s' % chart_postfix).attachAxis(eval('ui_obj.axisX_%s' % chart_postfix))
    eval('ui_obj.val_scatter_series_1_%s' % chart_postfix).attachAxis(eval('ui_obj.axisY_%s' % chart_postfix))
    eval('ui_obj.val_scatter_series_2_%s' % chart_postfix).attachAxis(eval('ui_obj.axisX_%s' % chart_postfix))
    eval('ui_obj.val_scatter_series_2_%s' % chart_postfix).attachAxis(eval('ui_obj.axisY_%s' % chart_postfix))
    # --------------------------------------------------------------------------------------------------------
    # hide legends of scatter series
    eval('ui_obj.chart_%s' % chart_postfix).legend().markers(eval('ui_obj.train_scatter_series_1_%s' % chart_postfix))[0].setVisible(False)
    eval('ui_obj.chart_%s' % chart_postfix).legend().markers(eval('ui_obj.train_scatter_series_2_%s' % chart_postfix))[0].setVisible(False)
    eval('ui_obj.chart_%s' % chart_postfix).legend().markers(eval('ui_obj.val_scatter_series_1_%s' % chart_postfix))[0].setVisible(False)
    eval('ui_obj.chart_%s' % chart_postfix).legend().markers(eval('ui_obj.val_scatter_series_2_%s' % chart_postfix))[0].setVisible(False)
    # ----------------------------------------------------------------------------------------------------------
    # define hbox layout
    hbox = sQVBoxLayout()
    hbox.addWidget(chartview)
    hbox.addWidget(eval('ui_obj.scrollbar_%s' % chart_postfix))
    # add to frame
    frame_obj.setLayout(hbox)
    # -------------------------------------------------------------------------------------------------------------
    # define actions
    # eval('ui_obj.train_scatter_series_2_%s' % chart_postfix).hovered.connect(lambda: slotPointHoverd(hover_label_obj=hover_label_obj))
    # eval('ui_obj.val_scatter_series_2_%s' % chart_postfix).hovered.connect(lambda: slotPointHoverd(hover_label_obj=hover_label_obj))
    
    eval('ui_obj.scrollbar_%s' % chart_postfix).valueChanged.connect(lambda: recalculate_range(ui_obj=ui_obj, chart_postfix=chart_postfix))
                                                                    
    checkbox_obj.stateChanged.connect(lambda: state_changed(checkbox_obj=checkbox_obj, ui_obj=ui_obj,
                                        scrolbaer_obj=eval('ui_obj.scrollbar_%s' % chart_postfix), axisX_obj=eval('ui_obj.axisX_%s' % chart_postfix)))
        

# chart hover show detail
# def slotPointHoverd(hover_label_obj):
#     print(pyautogui.position())
#     # if state:
#     #     hover_label_obj.setStyleSheet('background-color:rgba(255, 255, 255, 1); color:rgba(0, 0, 0, 1); border:Transparent; border-radius:7px; font-weight: bold')
#     #     hover_label_obj.setText('Epoch: {epoch:.0f} , Value: {accuracy:.2f}'.format(epoch=point.x(), accuracy=point.y()))
#     #     curPos =  sQPointF(sQCursor.pos())
#     #     hover_label_obj.move(curPos.x()-120, curPos.y()-250) # // Move value
#     #     hover_label_obj.show() #// Show
#     # else:
#     #     hover_label_obj.hide() #// Hide


# reset axisX range
def recalculate_range(ui_obj, chart_postfix):
    scrollbar_obj = eval('ui_obj.scrollbar_%s' % chart_postfix)
    axisX_obj = eval('ui_obj.axisX_%s' % chart_postfix)
    xmin = scrollbar_obj.value()
    xmax = scrollbar_obj.value() + axisX_range
    axisX_obj.setRange(xmin, xmax)


# append new data to chart
def append_data_to_chart(ui_obj, chart_postfix, train_x_series, train_y_series, val_x_series, val_y_series):
    # append the last comming history (data) to chart
    eval('ui_obj.train_line_series_%s' % chart_postfix).append(sQPointF(float(train_x_series), float(train_y_series)))
    eval('ui_obj.train_scatter_series_1_%s' % chart_postfix).append(sQPointF(float(train_x_series), float(train_y_series)))
    eval('ui_obj.train_scatter_series_2_%s' % chart_postfix).append(sQPointF(float(train_x_series), float(train_y_series)))
    eval('ui_obj.val_line_series_%s' % chart_postfix).append(sQPointF(float(val_x_series), float(val_y_series)))
    eval('ui_obj.val_scatter_series_1_%s' % chart_postfix).append(sQPointF(float(val_x_series), float(val_y_series)))
    eval('ui_obj.val_scatter_series_2_%s' % chart_postfix).append(sQPointF(float(val_x_series), float(val_y_series)))

# function to change chart view
def state_changed(ui_obj, checkbox_obj, scrolbaer_obj, axisX_obj):
    nepoch, last_epoch = get_nepochs_and_lastepoch()
    if checkbox_obj.isChecked():
        scrolbaer_obj.setMaximum(0)
        scrolbaer_obj.setValue(0)
        #self.ui.checkBox.setText("CHECKED!")
        axisX_obj.setRange(0, nepoch)
        axisX_obj.setTickCount(axisX_range+1)
    else:
        #self.ui.checkBox.setText("UNCHECKED!")
        axisX_obj.setRange(0, axisX_range)
        axisX_obj.setTickCount(axisX_range+1)
        if (last_epoch//axisX_range - 1)*axisX_range + (last_epoch%axisX_range) >= 0:
            scrolbaer_obj.setMaximum((last_epoch//axisX_range - 1)*axisX_range + (last_epoch%axisX_range))
            scrolbaer_obj.setValue((last_epoch//axisX_range - 1)*axisX_range + (last_epoch%axisX_range))
        else:
            scrolbaer_obj.setMaximum(0)
            scrolbaer_obj.setValue(0)


def get_nepochs_and_lastepoch():
    return numepoch, epochitr


def update_chart(ui_obj, chart_postfix):
    nepoch, last_epoch = get_nepochs_and_lastepoch()
    while last_epoch <= nepoch-1:
        #
        if last_epoch >= axisX_range and not ui_obj.checkBox.isChecked(): 
            eval('ui_obj.scrollbar_%s' % chart_postfix).setMaximum(((last_epoch+1)//axisX_range - 1)*axisX_range + ((last_epoch+1)%axisX_range))
            eval('ui_obj.scrollbar_%s' % chart_postfix).setValue(((last_epoch+1)//axisX_range - 1)*axisX_range + ((last_epoch+1)%axisX_range))
        #
        cv2.waitKey(500)
        append_data_to_chart(ui_obj=ui_obj, chart_postfix=chart_postfix, train_x_series=load[last_epoch], train_y_series=eff_train[last_epoch],
                                val_x_series=load[last_epoch], val_y_series=eff_val[last_epoch])
        #
        global epochitr
        epochitr += 1
        nepoch, last_epoch = get_nepochs_and_lastepoch()



# ----------------------------------------------------------------------------------------------------------


# bar chart for dataset volume info
def create_drive_barchart_on_ui(ui_obj, frame_obj, chart_title='Chart'):
    # chart
    ui_obj.barchart = sQChart()
    ui_obj.barchart.setMargins(sQMargins(0,0,0,0))
    #ui_obj.barchart.setTitle(chart_title)
    ui_obj.barchart.setAnimationOptions(sQChart.SeriesAnimations)

    # get number of available drives on system
    drives = storage_funcs.get_available_drives()

    # define sets
    ui_obj.used_space_set = sQBarSet("Optimal Used Space")
    ui_obj.used_space_set.setColor(sQColor(colors_pallete.successfull_green))
    ui_obj.warn_used_space_set = sQBarSet("Warning Used Space")
    ui_obj.warn_used_space_set.setColor(sQColor(colors_pallete.warning_yellow))
    ui_obj.crit_used_space_set = sQBarSet("Critical Used Space")
    ui_obj.crit_used_space_set.setColor(sQColor(colors_pallete.failed_red))
    ui_obj.free_space_set = sQBarSet("Free Space")
    ui_obj.free_space_set.setColor(sQColor(colors_pallete.blue0))
    #
    for i in range(len(drives)):
        ui_obj.used_space_set.append(0)
        ui_obj.warn_used_space_set.append(0)
        ui_obj.crit_used_space_set.append(0)
        ui_obj.free_space_set.append(0)

    # define bar series
    ui_obj.barseries = sQHorizontalStackedBarSeries()
    ui_obj.barseries.setLabelsVisible(True)
    ui_obj.barseries.append(ui_obj.used_space_set)
    ui_obj.barseries.append(ui_obj.warn_used_space_set)
    ui_obj.barseries.append(ui_obj.crit_used_space_set)
    ui_obj.barseries.append(ui_obj.free_space_set)
    # add series to chart
    
    ui_obj.barchart.addSeries(ui_obj.barseries)
    
    # chart axis
    # y
    ui_obj.barchart_ytitles = []
    ui_obj.barchart_axisY = sQBarCategoryAxis()
    ui_obj.barchart_axisY.append(drives)
    ui_obj.barchart_axisY.append(ui_obj.barchart_ytitles)
    ui_obj.barchart.addAxis(ui_obj.barchart_axisY, sQtCore.Qt.AlignLeft)
    ui_obj.barseries.attachAxis(ui_obj.barchart_axisY)
    # x
    ui_obj.barchart_axisX = sQValueAxis()
    ui_obj.barchart_axisX.setTitleText('Space (Gb)')
    ui_obj.barchart_axisX.setTickCount(21)
    ui_obj.barchart.addAxis(ui_obj.barchart_axisX, sQtCore.Qt.AlignBottom);
    ui_obj.barseries.attachAxis(ui_obj.barchart_axisX)
    # assign to UI
    #
    ui_obj.barchartView = sQChartView(ui_obj.barchart)
    ui_obj.barchartView.setContentsMargins(0,0,0,0)
    ui_obj.barchartView.setRenderHint(sQPainter.Antialiasing)
    #
    barvbox = sQVBoxLayout()
    barvbox.setContentsMargins(0, 0, 0, 0)
    barvbox.addWidget(ui_obj.barchartView)
    #
    frame_obj.setLayout(barvbox)
    frame_obj.layout().setContentsMargins(0, 0, 0, 0)


def update_drive_barchart(ui_obj, drives_info, storage_thrs, warn_storage_thrs):
    max_total = 0
    if storage_thrs > 1:
        storage_thrs /= 100
    if warn_storage_thrs > 1:
        warn_storage_thrs /= 100
    #
    for i, d_info in enumerate(drives_info):

        if d_info['total'] > max_total:
            max_total = d_info['total']
        
        # 
        if d_info['used'] / d_info['total'] >= storage_thrs:
            ui_obj.used_space_set.replace(i, 0)
            ui_obj.warn_used_space_set.replace(i, 0)
            ui_obj.crit_used_space_set.replace(i, d_info['used'])
        # warn
        elif d_info['used'] / d_info['total'] >= (storage_thrs+warn_storage_thrs)/2:
            ui_obj.used_space_set.replace(i, 0)
            ui_obj.warn_used_space_set.replace(i, d_info['used'])
            ui_obj.crit_used_space_set.replace(i, 0)
        # critical storage
        else:
            ui_obj.used_space_set.replace(i, d_info['used'])
            ui_obj.warn_used_space_set.replace(i, 0)
            ui_obj.crit_used_space_set.replace(i, 0)

        ui_obj.free_space_set.replace(i, d_info['total'])

    # axis range
    ui_obj.barchart_axisX.setRange(0, max_total)
        



# # chart (must be add in main_ui.py)
# # chart ---------------------------------------------------------------------------------------------
# chart_funcs.create_train_chart_on_ui(ui_obj=self, frame_obj=self.frame_chart, hover_label_obj=self.label_chart, chart_postfix='accuracy', chart_title='chart', legend_train='legend1', legend_val='legend2',
#                     axisX_title='epoch', axisY_title='Accuracy', checkbox_obj=self.checkBox)

# self.pushButton.clicked.connect(partial(lambda: chart_funcs.update_chart(ui_obj=self, chart_postfix='accuracy')))

    

    
    

    
    

    

    

    

    
