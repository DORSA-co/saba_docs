from PySide6.QtWidgets import QHeaderView as sQHeaderView
from PySide6.QtWidgets import QTableWidgetItem as sQTableWidgetItem
from PySide6.QtGui import QStandardItem as sQStandardItem
from PySide6.QtGui import QColor as sQColor
from PySide6.QtWidgets import QLabel as sQlabel
from PySide6 import QtCore as sQtCore
import numpy as np
import colorsys
from persiantools.jdatetime import JalaliDate
from pyparsing import col

from . import mainsetting_funcs, colors_pallete, texts


# users table number of rows and cols
defect_table_ncols = 8
defect_table_nrows = 20
headers = ['Defect Name', 'Defect Short-Name', 'Defect ID', 'Is Defect', 'Defect-Group', 'Defect Level', 'Defect Color Label', 'Created Date']
defect_group_table_ncols = 4
defect_group_table_nrows = 20
headers_defect_groups = ['Defect-Group Name', 'Defect-Group ID', 'Is Defect', 'Created Date']

#---------------------------------------------------------------------------------------------------------------------------

# update combobox visual properties
def update_combo_color(ui_obj):
    current_color = ui_obj.defect_color_comboBox.currentText()
    if current_color == 'No Color':
        current_color = '#949494'
    ui_obj.defect_color_comboBox.setStyleSheet('background:%s' % current_color)


# get users from database
def get_defects_from_db(db_obj, defect_groups=False):
    if not defect_groups:
        defects_list = db_obj.load_defects()
        return defects_list
    else:
        defect_groups_list = db_obj.load_defect_groups()
        return defect_groups_list


# get users from database
def get_filtered_defects_from_db(db_obj, filter_params, defect_groups=False):
    # input parameters and column names in database
    params = []
    cols = ''
    # add parameters and col names to build the input sql query
    if not defect_groups:
        if filter_params['name'] != '':
            params.append(filter_params['name'])
            cols += ',name'
        if filter_params['is_defect'] != 'all':
            params.append(filter_params['is_defect'])
            cols += ',is_defect'
        if filter_params['groupp'] != 'all':
            params.append(filter_params['groupp'])
            cols += ',groupp'
        if filter_params['level'] != 'all':
            params.append(filter_params['level'])
            cols += ',level'
    else:
        if filter_params['defect_group_name'] != '':
            params.append(filter_params['defect_group_name'])
            cols += ',defect_group_name'
        if filter_params['is_defect'] != 'all':
            params.append(filter_params['is_defect'])
            cols += ',is_defect'
    # build col names sql query
    if len(cols) > 0:
        if cols[0] == ',':
            cols = cols[1:]
        if cols[-1] == ',':
            cols = cols[:-1]
        cols = '(' + cols + ')'
    #
    if len(params) == 0 or len(cols) == 0:
        return 'all', []
    try:
        if not defect_groups:
            defects_list = db_obj.search_defect_by_filter(params, cols)
            return 'filtered', defects_list
        else:
            defect_groups_list = db_obj.search_defect_group_by_filter(params, cols)
            return 'filtered', defect_groups_list
    except:
        return []


# change defect group-id to name
def change_defect_group_id_to_name(db_obj, defects_list, reverse=False, single=False):
    if not reverse:
        if not single:
            for i in range(len(defects_list)):
                defect_group_name = db_obj.search_defect_group_by_id(defects_list[i]['groupp'])
                if len(defect_group_name) != 0:
                    defects_list[i]['groupp'] = defect_group_name['defect_group_name']
        else:
            defect_group_name = db_obj.search_defect_group_by_id(defects_list['groupp'])
            if len(defect_group_name) != 0:
                defects_list['groupp'] = defect_group_name['defect_group_name']
    # reverse
    else:
        defect_group_id = db_obj.search_defect_by_name(defects_list['groupp'])
        if len(defect_group_id) != 0:
            defects_list['groupp'] = defect_group_id['defect_group_id']

    return defects_list


# remove users from database
def remove_defects_from_db(db_obj, defects_list, defect_group=False, defect_group_id=False):
    if not defect_group:
        if not defect_group_id:
            res = db_obj.remove_defects(defects_list)
            return res
        else:
            res = db_obj.remove_defects_by_group_id(defects_list)
            return res
            
    # defect-group
    else:
        res = db_obj.remove_defect_groups(defects_list)
        return res


# remove users from database
def update_defects_to_db(db_obj, defects_list, defect_group=False):
    if not defect_group:
        res = db_obj.update_defect(defects_list)
        return res
    # defect-group
    else:
        res = db_obj.update_defect_group(defects_list)
        return res


# load selected user from database to UI
def load_defects_from_db(db_obj, defect_id, defect_group=False, defect_group_id=False):
    if not defect_group:
        if not defect_group_id:
            defect_info = db_obj.search_defect_by_id(defect_id[0])
            return defect_info
        else:
            defect_info = db_obj.search_defect_by_group_id(defect_id[0])
            return defect_info
    # defect-group
    else:
        defect_info = db_obj.search_defect_group_by_id(defect_id[0])
        return defect_info


# laod editable defect info to UI
def set_defect_info_on_ui(ui_obj, db_obj, defect_info):
    ui_obj.defect_name_lineedit.setText(defect_info['name'])
    ui_obj.defect_shortname_lineedit.setText(defect_info['short_name'])
    ui_obj.defect_id_lineedit.setText(defect_info['defect_ID'])
    # if defect_info['is_defect'] == 'yes':
    #     ui_obj.defect_isdefect_spinbox.setChecked(True)
    #     ui_obj.defect_notdefect_spinbox.setChecked(False) 
    # elif defect_info['is_defect'] == 'no':
    #     ui_obj.defect_isdefect_spinbox.setChecked(False)
    #     ui_obj.defect_notdefect_spinbox.setChecked(True) 
    #ui_obj.defect_group_lineedit.setText(defect_info['groupp'])
    index = ui_obj.defect_level_comboBox.findText(defect_info['level'], sQtCore.Qt.MatchFixedString)
    if index >= 0:
         ui_obj.defect_level_comboBox.setCurrentIndex(index)
    index = ui_obj.defect_group_combo.findText(change_defect_group_id_to_name(db_obj=db_obj, defects_list=defect_info, reverse=False, single=True)['groupp'], sQtCore.Qt.MatchFixedString)
    if index >= 0:
        ui_obj.defect_group_combo.setCurrentIndex(index)
    # color combo
    assign_existing_defect_colors_to_ui(ui_obj=ui_obj, db_obj=db_obj, current=defect_info['defect_ID'])


# laod editable defect info to UI
def set_defect_group_info_on_ui(ui_obj, defect_group_info):
    ui_obj.defect_group_name_lineedit.setText(defect_group_info['defect_group_name'])
    ui_obj.defect_group_id_lineedit.setText(defect_group_info['defect_group_id'])
    if defect_group_info['is_defect'] == 'yes':
        ui_obj.defect_isdefectgroup_spinbox.setChecked(True)
        ui_obj.defect_notdefectgroup_spinbox.setChecked(False) 
    elif defect_group_info['is_defect'] == 'no':
        ui_obj.defect_isdefectgroup_spinbox.setChecked(False)
        ui_obj.defect_notdefectgroup_spinbox.setChecked(True) 


# add user to database
def add_new_defect_to_db(db_obj, new_defect_info, defect_group=False):
    if not defect_group:
        res = db_obj.add_defect(new_defect_info)
        return res
    # defect-group
    else:
        res = db_obj.add_defect_group(new_defect_info)
        return res
        

# show/set user infoes to UI
def set_defects_on_ui(ui_obj, defects_list, defect_group_name='None'):
    # definr table parameters
    #print('a2',defects_list)
    ui_obj.tableWidget_defects.resizeColumnsToContents()
    ui_obj.tableWidget_defects.setColumnCount(defect_table_ncols)
    if len(defects_list) != 0:
        ui_obj.tableWidget_defects.setRowCount(defect_table_nrows)
    else:
        ui_obj.tableWidget_defects.setRowCount(0)
    ui_obj.tableWidget_defects.verticalHeader().setVisible(True)
    ui_obj.tableWidget_defects.horizontalHeader().setSectionResizeMode(sQHeaderView.Stretch)
    ui_obj.tableWidget_defects.setHorizontalHeaderLabels(headers)
    # add users to table
    for i, defect in enumerate(defects_list):
        # text color
        text_color = colors_pallete.failed_red if defect['groupp'] == defect_group_name else colors_pallete.black
        # set name
        table_item = sQTableWidgetItem(str(defect['name']))
        table_item.setFlags(sQtCore.Qt.ItemFlag.ItemIsUserCheckable | sQtCore.Qt.ItemFlag.ItemIsEnabled)
        table_item.setCheckState(sQtCore.Qt.CheckState.Unchecked)
        table_item.setForeground(sQColor(text_color))
        ui_obj.tableWidget_defects.setItem(i, 0, table_item)
        # set short name
        table_item = sQTableWidgetItem(str(defect['short_name']))
        table_item.setForeground(sQColor(text_color))
        ui_obj.tableWidget_defects.setItem(i, 1, table_item)
        # set defect_ID
        table_item = sQTableWidgetItem(str(defect['defect_ID']))
        table_item.setForeground(sQColor(text_color))
        ui_obj.tableWidget_defects.setItem(i, 2, table_item)
        # set is_defect
        table_item = sQTableWidgetItem(str(defect['is_defect']))
        table_item.setForeground(sQColor(text_color))
        ui_obj.tableWidget_defects.setItem(i, 3, table_item)
        # set group
        table_item = sQTableWidgetItem(str(defect['groupp']))
        table_item.setForeground(sQColor(text_color))
        ui_obj.tableWidget_defects.setItem(i, 4, table_item)
        # set level
        table_item = sQTableWidgetItem(str(defect['level']))
        table_item.setForeground(sQColor(text_color))
        ui_obj.tableWidget_defects.setItem(i, 5, table_item)
        # set color
        table_item = sQTableWidgetItem(str(defect['color']))
        icon = sQlabel('')
        icon.setStyleSheet("background-color: %s; margin-left:50px; margin-top:5px; margin-bottom:5px;" % str(defect['color']))
        ui_obj.tableWidget_defects.setCellWidget(i, 6, icon)
        table_item.setForeground(sQColor(text_color))
        ui_obj.tableWidget_defects.setItem(i, 6, table_item)
        #ui_obj.tableWidget_defects.item(i, 6).setBackground(sQColor('#E22B2B'))
        # set date
        table_item = sQTableWidgetItem(str(defect['date']))
        table_item.setForeground(sQColor(text_color))
        ui_obj.tableWidget_defects.setItem(i, 7, table_item)
    try:
        ui_obj.tableWidget_defects.setRowCount(i+1)
    except:
        return


# set defect-groups on UI combo box in add defect
def set_defect_groups_on_combo(ui_obj, defect_groups_list):
    ui_obj.defect_group_combo.clear()
    ui_obj.defect_search_group_combo.clear()
    item2 = sQStandardItem('All')
    ui_obj.defect_search_group_combo.model().appendRow(item2)
    for defect_group in defect_groups_list:
        item = sQStandardItem(defect_group['defect_group_name'])
        ui_obj.defect_group_combo.model().appendRow(item)
        item2 = sQStandardItem(defect_group['defect_group_name'])
        ui_obj.defect_search_group_combo.model().appendRow(item2)


# assign 
def assign_existing_defect_colors_to_ui(ui_obj, db_obj, current='None'):
    # clear all items in combo
    ui_obj.defect_color_comboBox.clear()
    # assign no serial label
    item = sQStandardItem('No Color')
    item.setBackground(sQColor('#FFFFFF'))
    ui_obj.defect_color_comboBox.model().appendRow(item)
    current_color = 'None'
    #
    for color in defect_colors:
        # validating serial to be not used by another camera
        color_info = db_obj.search_defect_by_color(color)
        if len(color_info) == 0 or color_info['defect_ID']==current or color == '#FFFFFF':
            item = sQStandardItem(color)
            item.setBackground(sQColor(color))
            ui_obj.defect_color_comboBox.model().appendRow(item)
        if len(color_info) != 0 and color_info['defect_ID']==current:
            current_color = color
    if current_color != 'None':
        #print(current_color)
        ui_obj.defect_color_comboBox.setCurrentText(current_color)
    # get n-used colors in defects
    defects_list = get_defects_from_db(db_obj=db_obj)
    n_used_colors = 0
    for defect in defects_list:
        if defect['color'] != '#FFFFFF':
            n_used_colors += 1
    ui_obj.defect_colors_number_spin.setMinimum(np.ceil(n_used_colors/3) * 3)


# show/set user infoes to UI
def set_defect_groups_on_ui(ui_obj, defect_groups_list):
    # definr table parameters
    ui_obj.tableWidget_defectgroups.resizeColumnsToContents()
    ui_obj.tableWidget_defectgroups.setColumnCount(defect_group_table_ncols)
    if len(defect_groups_list) != 0:
        ui_obj.tableWidget_defectgroups.setRowCount(defect_group_table_nrows)
    else:
        ui_obj.tableWidget_defectgroups.setRowCount(0)
    ui_obj.tableWidget_defectgroups.verticalHeader().setVisible(True)
    ui_obj.tableWidget_defectgroups.horizontalHeader().setSectionResizeMode(sQHeaderView.Stretch)
    ui_obj.tableWidget_defectgroups.setHorizontalHeaderLabels(headers_defect_groups)
    # add users to table
    for i, defect in enumerate(defect_groups_list):
        # set name
        table_item = sQTableWidgetItem(str(defect['defect_group_name']))
        table_item.setFlags(sQtCore.Qt.ItemFlag.ItemIsUserCheckable | sQtCore.Qt.ItemFlag.ItemIsEnabled)
        table_item.setCheckState(sQtCore.Qt.CheckState.Unchecked)
        ui_obj.tableWidget_defectgroups.setItem(i, 0, table_item)
        # set defect_ID
        table_item = sQTableWidgetItem(str(defect['defect_group_id']))
        ui_obj.tableWidget_defectgroups.setItem(i, 1, table_item)
        # set is_defect
        table_item = sQTableWidgetItem(str(defect['is_defect']))
        ui_obj.tableWidget_defectgroups.setItem(i, 2, table_item)
        # set date
        table_item = sQTableWidgetItem(str(defect['date_created']))
        ui_obj.tableWidget_defectgroups.setItem(i, 3, table_item)
    try:
        ui_obj.tableWidget_defectgroups.setRowCount(i+1)
    except:
        return


# get selected users from user table in UI
def get_selected_defects(ui_obj, defects_list):
    list = []
    for i in range(ui_obj.tableWidget_defects.rowCount()):    
        if ui_obj.tableWidget_defects.item(i, 0).checkState() == sQtCore.Qt.Checked:
            list.append(ui_obj.tableWidget_defects.item(i, 2).text())
    # selected_defects = []
    # for i in range (len(list)):
    #     selected_defects.append(defects_list[list[i]]['defect_ID'])
    # return selected_defects
    return list


# get selected users from user table in UI
def get_selected_defect_groups(ui_obj, defect_groups_list):
    list = []
    for i in range(ui_obj.tableWidget_defectgroups.rowCount()):    
        if ui_obj.tableWidget_defectgroups.item(i, 0).checkState() == sQtCore.Qt.Checked:
            list.append(ui_obj.tableWidget_defectgroups.item(i, 1).text())
    # selected_defect_groups = []
    # for i in range (len(list)):
    #     selected_defect_groups.append(defect_groups_list[list[i]]['defect_group_id'])
    # return selected_defect_groups
    return list


# get new user information from window (add user)
def get_defect_info_from_ui(ui_obj, db_obj, defect_group=False, is_filter=False):
    try:
        if not is_filter:
            if not defect_group:
                # get user-infoes from UI
                defect_info = {}
                defect_info['name'] = ui_obj.defect_name_lineedit.text().lower()
                defect_info['short_name'] = ui_obj.defect_shortname_lineedit.text().lower()
                defect_info['defect_ID'] = ui_obj.defect_id_lineedit.text()
                # is-defect
                defect_info['is_defect'] = db_obj.search_defect_group_by_name(input_defect_group_name=ui_obj.defect_group_combo.currentText())['is_defect']
                defect_info['groupp'] = db_obj.search_defect_group_by_name(input_defect_group_name=ui_obj.defect_group_combo.currentText())['defect_group_id']
                defect_info['level'] = ui_obj.defect_level_comboBox.currentText()
                defect_info['color'] = ui_obj.defect_color_comboBox.currentText()
                defect_info['date'] = '%s/%s/%s' % (JalaliDate.today().day, JalaliDate.today().month, JalaliDate.today().year)
                if defect_info['date'][1] == '/':
                    defect_info['date'] = '0' + defect_info['date']
                if defect_info['date'][4] == '/':
                    defect_info['date'] = defect_info['date'][:3] + '0' + defect_info['date'][3:]
                return defect_info
            # defect-group
            else:
                # get user-infoes from UI
                defect_group_info = {}
                defect_group_info['defect_group_name'] = ui_obj.defect_group_name_lineedit.text().lower()
                defect_group_info['defect_group_id'] = ui_obj.defect_group_id_lineedit.text()
                if ui_obj.defect_isdefectgroup_spinbox.isChecked() and not ui_obj.defect_notdefectgroup_spinbox.isChecked():
                    defect_group_info['is_defect'] = 'yes'
                elif not ui_obj.defect_isdefectgroup_spinbox.isChecked() and ui_obj.defect_notdefectgroup_spinbox.isChecked():
                    defect_group_info['is_defect'] = 'no'
                else:
                    defect_group_info['is_defect'] = ''
                defect_group_info['date_created'] = '%s/%s/%s' % (JalaliDate.today().day, JalaliDate.today().month, JalaliDate.today().year)
                if defect_group_info['date_created'][1] == '/':
                    defect_group_info['date_created'] = '0' + defect_group_info['date_created']
                if defect_group_info['date_created'][4] == '/':
                    defect_group_info['date_created'] = defect_group_info['date_created'][:3] + '0' + defect_group_info['date_created'][3:]
                return defect_group_info

        # fliter mode
        else:
            if not defect_group:
                # get user-infoes from UI
                defect_info = {}
                defect_info['name'] = ui_obj.defect_search_name_lineedie.text().lower()
                defect_info['is_defect'] = ui_obj.defect_search_isdefect_combo.currentText().lower()
                if ui_obj.defect_search_group_combo.currentText() != 'All':
                    defect_info['groupp'] = db_obj.search_defect_group_by_name(input_defect_group_name=ui_obj.defect_search_group_combo.currentText())['defect_group_id']
                else:
                    defect_info['groupp'] = 'all'
                defect_info['level'] = ui_obj.defect_search_level_comboBox.currentText().lower()
                return defect_info
            # defect-group
            else:
                # get user-infoes from UI
                defect_group_info = {}
                defect_group_info['defect_group_name'] = ui_obj.defectgroup_search_name_lineedie.text().lower()
                defect_group_info['is_defect'] = ui_obj.defectgroup_search_isdefect_combo.currentText().lower()
                return defect_group_info
    except:
        return []


# validate new user username
def new_defect_info_validation(ui_obj, db_obj, defect_info, on_edit=False, defect_group=False):
    if not defect_group:
        # check fields to not empty
        if defect_info['name'] == '' or defect_info['short_name'] == '' or defect_info['defect_ID'] == '' or defect_info['color'] == '':
            return texts.WARNINGS['fields_empty'][ui_obj.language], 1

        # check id contains only letters
        if not defect_info['defect_ID'].isdigit():
            return texts.WARNINGS['defect_id_only_numbers'][ui_obj.language], 1
        else:
            defect_info['defect_ID'] = str(int(defect_info['defect_ID']))

        # check color
        if defect_info['color'] == 'No Color':
            return texts.WARNINGS['no_defect_color_selected'][ui_obj.language], 1
        if defect_info['is_defect'] == 'no' and defect_info['color'] != '#FFFFFF':
            return texts.WARNINGS['defect_color_only_white'][ui_obj.language], 1
        if defect_info['is_defect'] == 'yes' and defect_info['color'] == '#FFFFFF':
            return texts.WARNINGS['defect_color_not_white'][ui_obj.language], 1

        # check level:
        if defect_info['is_defect'] == 'no' and int(defect_info['level']) != 0:
            return texts.WARNINGS['defect_level_only_zero'][ui_obj.language], 1
        if defect_info['is_defect'] == 'yes' and int(defect_info['level']) == 0:
            return texts.WARNINGS['defect_level_not_zero'][ui_obj.language], 1

        # check id to be unique
        res_id = db_obj.search_defect_by_id(defect_info['defect_ID'])
        # check name to be unique
        res_name = db_obj.search_defect_by_name(defect_info['name'])
        # check short-name to be unique
        red_short_name = db_obj.search_defect_by_short_name(defect_info['short_name'])

        if len(res_id) == 0 or on_edit:
            if len(res_name) == 0 or (on_edit and defect_info['name']==res_id['name']):
                if len(red_short_name) == 0 or (on_edit and defect_info['short_name']==res_id['short_name']):
                    return 'True', 0
                else:
                    return texts.ERRORS['defect_shortname_invalid'][ui_obj.language], 2
            else:
                return texts.ERRORS['defect_name_invalid'][ui_obj.language], 2
        else:
            return texts.ERRORS['defect_id_invalid'][ui_obj.language], 2

    # defect-group
    else:
        # check fields to not empty
        if defect_info['defect_group_name'] == '' or defect_info['defect_group_id'] == '' or defect_info['is_defect'] == '':
            return texts.WARNINGS['fields_empty'][ui_obj.language], 1

        # check id contains only letters
        if not defect_info['defect_group_id'].isdigit():
            return texts.WARNINGS['defect_group_id_only_numbers'][ui_obj.language], 1
        else:
            defect_info['defect_group_id'] = str(int(defect_info['defect_group_id']))

        # check id to be unique
        res_id = db_obj.search_defect_group_by_id(defect_info['defect_group_id'])
        # check name to be unique
        res_name = db_obj.search_defect_group_by_name(defect_info['defect_group_name'])

        if len(res_id) == 0 or on_edit:
            if len(res_name) == 0 or (on_edit and defect_info['defect_group_name']==res_id['defect_group_name']):
                return 'True', 0
            else:
                return texts.ERRORS['defect_group_name_invalid'][ui_obj.language], 2
        else:
            return texts.ERRORS['defect_group_id_invalid'][ui_obj.language], 2


# defect colors
defect_colors = []
def generate_defect_colors(db_obj):
    # get num colors from db
    n_colors = mainsetting_funcs.get_mainsetting_params_from_db(db_obj=db_obj)[0]['n_defect_colors']//3
    defect_colors.clear()
    defect_colors.append('#FFFFFF')
    for i in np.arange(0., 360., 360. / n_colors):
        hue = i/360.
        for j in range(80,200,50):
            lightness = (50 + 0.5 * 10)/j
            saturation = (90 + 0.5 * 10)/100
        
            color = colorsys.hls_to_rgb(hue, lightness, saturation)
            html_code = f'#{int(round(color[0]*255)):02x}{int(round(color[1]*255)):02x}{int(round(color[2]*255)):02x}'
            defect_colors.append(html_code)


# show defects summary info on dashboard
def show_defects_summary_info(ui_obj, db_obj):
    # get defects-list from database
    defects_list = get_defects_from_db(db_obj)
    ui_obj.available_defects.setText(str(len(defects_list)))
    # get defectgroups-list from database
    defects_list = get_defects_from_db(db_obj, defect_groups=True)
    ui_obj.available_defectgroups.setText(str(len(defects_list)))


