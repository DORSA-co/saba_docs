from PySide6.QtCharts import QChart as sQChart
from PySide6.QtCharts import QChartView as sQChartView
from PySide6.QtCharts import QValueAxis as sQValueAxis
from PySide6.QtWidgets import QVBoxLayout as sQVBoxLayout
from PySide6 import QtCore as sQtCore
from PySide6.QtGui import QColor as sQColor
from PySide6.QtGui import QPainter as sQPainter
from PySide6.QtCharts import QBarSet as sQBarSet
from PySide6.QtCharts import QHorizontalStackedBarSeries as sQHorizontalStackedBarSeries
from PySide6.QtCharts import QBarCategoryAxis as sQBarCategoryAxis
from PySide6.QtCore import QMargins as sQMargins

from . import storage_funcs, colors_pallete


# ----------------------------------------------------------------------------------------------------------
# bar chart for dataset volume info
def create_drive_barchart_on_ui(ui_obj, frame_obj, chart_title='Chart'):
    """
    this function is used to create bar-chart on storage managment page

    :param ui_obj: (_type_) main ui object
    :param frame_obj: (_type_) ui frame name to create chart in
    :param chart_title: (str, optional) _description_. Defaults to 'Chart'.
    
    :returns: None
    """

    # create chart object
    ui_obj.barchart = sQChart()
    ui_obj.barchart.setMargins(sQMargins(0,0,0,0))
    #ui_obj.barchart.setTitle(chart_title)
    ui_obj.barchart.setAnimationOptions(sQChart.SeriesAnimations)

    # get number of available drives on system
    drives = storage_funcs.get_available_drives()

    # define sets
    ui_obj.used_space_set = sQBarSet(ui_obj.translate_headers_list(header_list=["Optimal Used Space"])[0])
    ui_obj.used_space_set.setColor(sQColor(colors_pallete.successfull_green))
    ui_obj.warn_used_space_set = sQBarSet(ui_obj.translate_headers_list(header_list=["Warning Used Space"])[0])
    ui_obj.warn_used_space_set.setColor(sQColor(colors_pallete.warning_yellow))
    ui_obj.crit_used_space_set = sQBarSet(ui_obj.translate_headers_list(header_list=["Critical Used Space"])[0])
    ui_obj.crit_used_space_set.setColor(sQColor(colors_pallete.failed_red))
    ui_obj.free_space_set = sQBarSet(ui_obj.translate_headers_list(header_list=["Free Space"])[0])
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
    ui_obj.barchart_axisX.setTitleText(ui_obj.translate_headers_list(header_list=['Space (Gigabyte)'])[0])
    ui_obj.barchart_axisX.setTickCount(21)
    ui_obj.barchart.addAxis(ui_obj.barchart_axisX, sQtCore.Qt.AlignBottom)
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
    """
    this function is used to update drive satues barchart on storage management page

    :param ui_obj: (_type_) main ui object
    :param drives_info: (_type_) statues of the drive (in dict)
    :param storage_thrs: (_type_) an int determining thrshold of storage using in bas statues(for chart colors)
    :param warn_storage_thrs: (_type_) an int determining thrshold of storage using in warning statues(for chart colors)

    :returns: None
    """

    max_total = 0
    if storage_thrs > 1:
        storage_thrs /= 100
    if warn_storage_thrs > 1:
        warn_storage_thrs /= 100

    #
    for i, d_info in enumerate(drives_info):

        if d_info['total'] > max_total:
            max_total = d_info['total']
        
        # critcal using
        if d_info['used'] / d_info['total'] >= storage_thrs:
            ui_obj.used_space_set.replace(i, 0)
            ui_obj.warn_used_space_set.replace(i, 0)
            ui_obj.crit_used_space_set.replace(i, d_info['used'])

        # warning using
        elif d_info['used'] / d_info['total'] >= (storage_thrs+warn_storage_thrs)/2:
            ui_obj.used_space_set.replace(i, 0)
            ui_obj.warn_used_space_set.replace(i, d_info['used'])
            ui_obj.crit_used_space_set.replace(i, 0)

        # good strage statues
        else:
            ui_obj.used_space_set.replace(i, d_info['used'])
            ui_obj.warn_used_space_set.replace(i, 0)
            ui_obj.crit_used_space_set.replace(i, 0)

        ui_obj.free_space_set.replace(i, d_info['total'])

    # set axis range
    ui_obj.barchart_axisX.setRange(0, max_total)
        



# # chart (must be add in main_ui.py)
# # chart ---------------------------------------------------------------------------------------------
# chart_funcs.create_train_chart_on_ui(ui_obj=self, frame_obj=self.frame_chart, hover_label_obj=self.label_chart, chart_postfix='accuracy', chart_title='chart', legend_train='legend1', legend_val='legend2',
#                     axisX_title='epoch', axisY_title='Accuracy', checkbox_obj=self.checkBox)

# self.pushButton.clicked.connect(partial(lambda: chart_funcs.update_chart(ui_obj=self, chart_postfix='accuracy')))

    

    
    

    
    

    

    

    

    
