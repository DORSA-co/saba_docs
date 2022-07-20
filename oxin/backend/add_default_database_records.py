from . import user_management_funcs, texts, date_funcs


# default username info
default_username = 'Dorsa_Admin'
default_password = 'Dorsa1400@'

# defeault defect
default_defect_name = 'No Defect'
default_defect_shortname = 'No Defect'
default_defect_id = '0'

# default dfect-group
default_defectgroup_name = 'No Defect'
default_defectgroup_id = '0'


def create_default_records(ui_obj, api_obj):
    """
    this function is used to create default records in database, if not exist

    :param ui_obj: (_type_) main ui object
    :param api_obj: (_type_) main api object
    """
    # add default user
    ui_obj.logger.create_new_log(message=texts.MESSEGES['adding_defalt_user']['en'], level=1)
    user_info = {}
    user_info['user_name'] = default_username
    user_info['password'] = default_password
    user_info['re_password'] = default_password
    user_info['role'] = user_management_funcs.default_user_roles[0]
    user_info['date_created'] = date_funcs.get_date()
    #
    api_obj.add_user(default_user=user_info)

    # add default defect
    ui_obj.logger.create_new_log(message=texts.MESSEGES['adding_defalt_defect']['en'], level=1)
    defect_info = {}
    defect_info['name'] = default_defect_name
    defect_info['short_name'] = default_defect_shortname
    defect_info['defect_ID'] = default_defect_id
    defect_info['is_defect'] = 'no'
    defect_info['groupp'] = default_defectgroup_id
    defect_info['level'] = 0
    defect_info['color'] = '#FFFFFF'
    defect_info['date'] = date_funcs.get_date()
    #
    api_obj.add_defect(default_defect=defect_info)

    # add defeault defect group
    ui_obj.logger.create_new_log(message=texts.MESSEGES['adding_defalt_defectgroup']['en'], level=1)
    defect_group_info = {}
    defect_group_info['defect_group_name'] = default_defectgroup_name
    defect_group_info['defect_group_id'] = default_defectgroup_id
    defect_group_info['is_defect'] = 'no'
    defect_group_info['date_created'] = date_funcs.get_date()
    #
    api_obj.add_defect_group(default_defectgroup=defect_group_info)
