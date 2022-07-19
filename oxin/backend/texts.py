# this file containes dictionary of all texts and sentences used in app and ui, in english and farsi


ERRORS={

        'database_get_drive_infoes_failed': {'fa': 'خطای دریافت اطلاعات درایو از دیتابیس',
                 'en': 'Failed to get drive infoes from database.'},

        'initialize_login_ui_failed': {'fa': 'خطای ساخت کلاس واسط کاربری کاربران',
                 'en': 'Failed to initialize login UI object.'},

        'initialize_confirm_ui_failed': {'fa': 'خطای ساخت کلاس واسط کاربری تایید',
                 'en': 'Failed to initialize confirmaton UI object.'},

        'initialize_notif_ui_failed': {'fa': 'خطای ساخت کلاس واسط کاربری اعلانات',
                 'en': 'Failed to initialize notification UI object.'},

        'initialize_login_api_failed': {'fa': 'خطای ساخت کلاس ای پی آی کاربران',
                 'en': 'Failed to initialize login API object.'},

        'initialize_database_object_failed': {'fa': 'خطای ساخت کلاس دیتابیس',
                 'en': 'Failed to initialize database object object.'},

        'initialize_buttons_failed': {'fa': 'خطای اتصال دکمه های واسط کاربری',
                 'en': 'Failed to initialize/connect UI botttons events.'},

        'initialize_objects_failed': {'fa': 'خطای ساخت کلاس های اولیه موردنیاز برای نرم افزار',
                 'en': 'Failed to setup initial objects for setting app.'},

        'database_get_mainsettings_failed': {'fa': 'خطای دریافت اطلاعات ظاهری یا تنظیمات کلی نرما افزار از دیتابیس',
                 'en': 'Failed to load UI apearance params or main-settings page params from database.'},

        'create_charts_failed': {'fa': 'خطای ساخت نمودارهای نرم افزار',
                 'en': 'Failed to create chart(s) on UI.'},

        'camera_connection_api_failed': {'fa': 'خطای اتصال به ای پی آی دسترسی به دوربین ها',
                 'en': 'Failed to run camera-connecton API.'},

        'database_camera_serials_update_failed': {'fa': 'خطای آپدیت اطلاعات سریال دوربین ها در دیتابیس',
                 'en': 'Failed to update camera serials on database given the current available cameras.'},

        'initialize_storage_check_timer_failed': {'fa': 'خطای ساخت تایمر بازرسی وضعیت حافظه',
                 'en': 'Failed to initialize timer for checking storage'},

        'initialize_dashboard_refresh_timer_failed': {'fa': 'خطای ساخت تایمر نوسازی داشبورد',
                 'en': 'Failed to initialize timer for refreshing dashboard'},

        'database_login_failed': {'fa': 'خطای ورود/دریافت اطلاعات کاربر از دیتابیس',
                 'en': 'Failed to login/get login info from database.'},

        'storage_clear_check_failed': {'fa': 'خطای چگ گردن یا پاکسازی درایو',
                 'en': 'Failed to check storage statues/clear storage'},

        'database_camera_live_drive_params_appliy_failed': {'fa': 'خطای آپدیت تنظیمات درایو در دیتابیس',
                 'en': 'Failed to update drive settings in database'},

        'mainsetting_apply_failed': {'fa': 'خطای اعمال تنظیمات در دیتابیس',
                 'en': 'Failed to apply settings in database'},

        'database_laod_users_list_failed': {'fa': 'خطای دریافت لیست کاربران از دیتابیس',
                 'en': 'Failed to load users list from database'},

        'username_invalid': {'fa': 'نام کاربری واردشده تکراری یا غیر قابل قبول است',
                 'en': 'Invalid/duplicate Username'},

        'new_user_create_faled': {'fa': 'خطای ایجاد کاربر جدید',
                 'en': 'Failed to create new user'},

        'new_user_validate_faled': {'fa': 'خطای اعتبارسنجی ایجاد کاربر جدید',
                 'en': 'Failed to validiate new user'},

        'user_remove_faled': {'fa': 'خطای حذف کاربران',
                 'en': 'Failed to remove users'},

        'database_load_defects_failed': {'fa': 'خطای دریافت لیست عیوب از دیتابیس',
                 'en': 'Failed to load defects from database'},

        'database_load_defect_groups_failed': {'fa': 'خطای دریافت لیست گروه عیوب از دیتابیس',
                 'en': 'Failed to load defect groups from database'},

        'change_defect_id_to_name': {'fa': 'خطای تغییر آی دی عیوب به نام عیوب',
                 'en': 'Failed to change defect-ids to name'},

        'ui_get_new_defect_info_failed': {'fa': 'خطای دریافت اطلاعات عیب جدید از کاربر',
                 'en': 'Failed to get new defect info from UI'},

        'ui_get_new_defect_group_info_failed': {'fa': 'خطای دریافت اطلاعات گروه عیب جدید از کاربر',
                 'en': 'Failed to get new defect group info from UI'},

        'ui_get_new_defect_group_info': {'fa': 'خطای دریافت اطلاعات گروه عیب جدید از کاربر',
                 'en': 'Failed to get new defect group info from UI'},
        
        'defect_shortname_invalid': {'fa':'این نام کوتاه تکراری و نامتبر است',
            'en':'Invalid/duplicate defect-shortname'},

        'defect_name_invalid': {'fa':'این نام عیب تکراری و نامتبر است',
            'en':'Invalid/duplicate defect-name'},

        'defect_group_name_invalid': {'fa':'این نام گروه عیب تکراری و نامتبر است',
            'en':'Invalid/duplicate defect-group-name'},

        'defect_id_invalid': {'fa':'این آی دی عیب تکراری و نامتبر است',
            'en':'Invalid/duplicate defect-ID'},

        'defect_group_id_invalid': {'fa':'این آی دی گروه عیب تکراری و نامتبر است',
            'en':'Invalid/duplicate defect group-ID'},

        'crate_new_defect_failed': {'fa': 'خطا در ایجاد عیب جدید',
                 'en': 'Failed to create new defect'},

        'crate_new_defect_group_failed': {'fa': 'خطا در ایجاد گروه عیب جدید',
                 'en': 'Failed to create new defect group'},

        'edit_defect_failed': {'fa': 'خطا در تغییر عیب',
                 'en': 'Failed to change/edit defect'},

        'edit_defect_group_failed': {'fa': 'خطا در تغییر گروه عیب',
                 'en': 'Failed to change/edit defect group'},

        'defect_group_cant_edit': {'fa': 'امکان تغییر این گروه عیب وجود ندارد',
                 'en': 'This defect group cant be edited'},

        'defect_cant_edit': {'fa': 'امکان تغییر این عیب وجود ندارد',
                 'en': 'This defect cant be edited'},

        'defect_group_cant_removed': {'fa': 'امکان حذف این گروه عیب وجود ندارد',
                 'en': 'This defect group cant be removed'},

        'defect_cant_removed': {'fa': 'امکان حذف این عیب وجود ندارد',
                 'en': 'default defect cant be removed'},

        'remove_defect_groups_failed': {'fa': 'خطا در حذف گروه عیب',
                 'en': 'Failed to temove defect group'},

        'remove_defects_failed': {'fa': 'خطا در حذف عیب(ها)',
                 'en': 'Failed to remove defect(s)'},

        'camera_disconnect_failed': {'fa': 'خطای قطع اتصال دوربین',
                 'en': 'Failed to disconnect from camera'},

        'database_loade_camera_params_failed': {'fa': 'خطای دریافت پارامترهای دوربین از دیتابیس',
                 'en': 'Failed to load camera params from database'},

        'ip_in_used': {'fa': 'آی پی انتخاب شده تکراری است',
                 'en': 'IP is in used'},

        'database_apply_camera_setting_failed': {'fa': 'آی پی انتخاب شده تکراری است',
                 'en': 'Failed to apply camera settings to database'},

        'camera_no_serial_assigned': {'fa': 'سریالی به دوربین انتخاب شده اختصاص داده نشده است',
                 'en': 'No serial is assigned'},

        'camera_connect_failed': {'fa': 'خطای اتصال به دوربین',
                 'en': 'Failed to connected to camera'},

        'database_apply_camera_calibration_params_failed': {'fa': 'خطای ذخیره پارامترهای کالیبراسیون در دیتابیس',
                 'en': 'Failed to apply calibration parmeters to database'},

        'camera_get_picture_failed': {'fa': 'خطای دریافت تصویر از دوربین',
                 'en': 'Failed to get image from camera'},

        'pxvalue_calibration_apply_failed': {'fa': 'خطای اعمال کالیبراسیون ارزش پیکسلی',
                 'en': 'Failed to apply pixel-value calibration'},

        'plc_connection_apply_failed': {'fa': 'خطای اتصال به پی ال سی',
                 'en': 'Failed to connect to PLC'},

        'database_set_plc_ip_failed': {'fa': 'خطای ذخیره آی پی در دیتابیس',
                 'en': 'Failed to update PLC ip on database'},

        'database_get_plc_ip_failed': {'fa': 'خطای دریافت آی پی در دیتابیس',
                 'en': 'Failed to get PLC ip on database'},

        'plc_disconnected_failed': {'fa': 'خطای قطع اتصال پی ال سی',
                 'en': 'Failed to disconnect from PLC'},

        'plc_path_error': {'fa': 'خطای خواندن آدرس در پی ال سی',
                 'en': 'Failed to read path from PLC'},

        'plc_write_json_failed': {'fa': 'خطای ثبت اطلاعات پی ال سی در فایل',
                 'en': 'Failed to write PLC params to json file'},

        'plc_set_value_failed': {'fa': 'خطای آپدیت مقدار متغیر در پی ال سی',
                 'en': 'Failed to set vaule on PLC'},

        'database_update_plc_params_failed': {'fa': 'خطای آپدیت پارامترهای پی ال سی در دیتابیس',
                 'en': 'Failed to update PLC params on database'},

        'database_get_plc_params_failed': {'fa': 'خطای دریافت پارامترهای پی ال سی از دیتابیس',
                 'en': 'Failed to get PLC params from database'},

        'failed_to_translate_ui_to_persian': {'fa': 'خطای تغییر زبان نرم افزار به فارسی',
                 'en': 'Failed to change app language to Persian'},

        'failed_to_translate_ui_to_english': {'fa': 'خطای تغییر زبان نرم افزار به انگلیسی',
                 'en': 'Failed to change app language to English'},

        'setting_app_closed_force': {'fa': 'نرم افزار تنظیمات با اجبار بسته شد، ممکن است خطایی رخ داده باشد',
                 'en': 'Setting app closed by force, there may an error/exception occured.'},

        'username_password_incorrect': {'fa': 'نام کاربری/گذرواژه اشتباه است',
                 'en': 'Username/password incorrect'},
                 
        'user_authenticate_failed': {'fa': 'خطای اعتبارسنجی کاربر',
                 'en': 'Failed to authenticate user'},
        
        'all_cameras_not_calibrated': {'fa':'کالیبره نشده',
            'en':'Not calibrated'},

        'drive_not_selected': {'fa':'انتخاب نشده',
            'en':'Not Selected'},

        

}


WARNINGS={

        'logout_confirm_message': {'fa':'آیا از خروج از حساب کربری خود اطمینان دارید؟',
            'en':'Are you sure you want to logout?'},
            
        'drive_fulled_with_other_content': {'fa':'درایو جاری حاوی اسناد دیگری نامرتبط با نرم افزار است، لطفا آنها را به صورت دستی پاک کنید.',
            'en':'Current drive contains other files taken space, please remove them manually'},

        'some_camera_not_connected': {'fa':'تعدادی از دوربین ها در شبکه متصل نیستند.',
            'en':'Some Cameras are not connected.'},

        'change_login_button_icon_failed': {'fa':'خطای تغییر آیکون دکمه ورود/خروج',
            'en':'Failed to change login button icon.'},

        'clear_storage': {'fa':'پاکسازی فایل های قدیمی حافظه',
            'en':'Start removing old files'},

        'min_bigger_than_max': {'fa':'مقدار مینیمم نمیتواند کمتر از ماکزیمم باشد',
            'en':'Min threshold cant be bigger than max'},

        'default_drive_select': {'fa':'هیچ درایو پیشفرضی انتخاب نشده است',
            'en':'No default drive selected'},

        'fields_empty': {'fa':'فیلدها نبایستی خالی باشند',
            'en':'Fields cant be empty'},

        'passwords_match': {'fa':'پسوردهای واردشده یکسان نیستند',
            'en':'Passwords dont match'},

        'admin_users_remove': {'fa':'امکان حذف کاربران ادمین وجود ندارد',
            'en':'Admin user(s) cant be removed'},

        'current_user_remove': {'fa':'امکان حذف کاربر فعلی واردشده وجود ندارد',
            'en':'Current logged-in user cant be removed'},

        'defect_id_only_numbers': {'fa':'آی دی عیب بایستی تنها حاوی اعداد باشد',
            'en':'Defect-ID should contain only numbers'},

        'defect_group_id_only_numbers': {'fa':'آی دی گروه عیب بایستی تنها حاوی اعداد باشد',
            'en':'Defect group ID should contain only numbers'},

        'no_defect_color_selected': {'fa':'هیچ رنگی برای عیب انتخاب نشده است',
            'en':'No defect Color is Selected'},

        'defect_color_only_white': {'fa':'برای این عیب تنها رنگ سفید قابل انتخاب است',
            'en':'Only white color could be assigned to this defect'},

        'defect_color_not_white': {'fa':'امکان انتخاب رنگ سفید برای این عیب وجود ندارد',
            'en':'White color couldnt be assigned to this defect'},

        'defect_level_only_zero': {'fa':'برای این عیب تنها سطح صفر قابل انتخاب است',
            'en':'Only level 0 could be assigned to this defect'},

        'defect_level_not_zero': {'fa':'امکان انتخاب سطح صفر برای این عیب وجود ندارد',
            'en':'Level 0 couldnt be assigned to this defect'},

        'select_only_one_to_edit': {'fa':'امکان انتخاب بیش از یک مورد برای تغییر وجود ندارد',
            'en':'Cant select more than one element to edit'},

        'no_selected_to_edit': {'fa':'لطفا حداقل یک مورد برای تغییر انتخاب نمایید ',
            'en':'Please select at least one element to edit'},

        'select_only_one_to_remove': {'fa':'امکان انتخاب بیش از یک مورد برای حذف وجود ندارد',
            'en':'Cant select more than one element to remove'},

        'no_selected_to_remove': {'fa':'لطفا حداقل یک مورد برای حذف انتخاب نمایید',
            'en':'Please select at least one element to remove'},

        'remove_defect_group_containing_defects': {'fa':'با حذف این گروه عیب، عیب های متعلق به این گروه نیز حذف می شوند',
            'en':'There are some defects related to this defect-group, Removing this defect-group cause to removing theme.'},

        'ip_invalid': {'fa':'آی پی واردشده نامعتبر است',
            'en':'IP invalid'},

        'ip_out_of_range': {'fa':'آی پی واردشده خارج از رنج است',
            'en':'IP out of range'},

        'ip_contain_letters': {'fa':'آی پی بایستی تنها شامل اعداد باشد',
            'en':'IP shoud not contain letters/symbols'},

        'camera_settings_apply_to_top': {'fa':'تنظیمات بر روی تمامی دوربین های بالا اعمال شود؟',
            'en':'Settings will be applied to all the top cameras?'},

        'camera_settings_apply_to_bottom': {'fa':'تنظیمات بر روی تمامی دوربین های پایین اعمال شود؟',
            'en':'Settings will be applied to all the bottom cameras?'},

        'camera_settings_apply_to_all': {'fa':'تنظیمات بر روی تمامی تمامی دوربین ها اعمال شود؟',
            'en':'Settings will be applied to all the cameras?'},

        'camera_no_picture': {'fa':'هنوز تصویری از دوربین دریافت نشده است',
            'en':'No picture is taken yet'},

        'no_picture_loaded': {'fa':'هنوز تصویری بارگزاری نشده است',
            'en':'No picture is loaded yet'},

        'app_warning': {'fa':'نرم افزار سبا - پیغام',
            'en':'SABA - Settings App Message'},

        'read_storage_check_interval_from_json_failed': {'fa':'خطای دریافت مقدار فاصله زمانی چک حافظه از فایل شروع',
            'en':'Failed to get storage check interval from startup json'},

        'read_dashboard_refresh_interval_from_json_failed': {'fa':'خطای دریافت مقدار فاصله زمانی نوسازی حافظه از فایل شروع',
            'en':'Failed to get dashboard refresh interval from startup json'},

        'storage_check_interval_change_failed': {'fa':'خطای تغییر فاصله زمانی چک حافظه',
            'en':'Failed to change dtorage check interval'},

        'username_len': {'fa':'طول نام کاربری بایستی در رنج روبرو باشد',
            'en':'Username length most be between range'},

        'password_len': {'fa':'طول پسورد بایستی در رنج روبرو باشد',
            'en':'Password length most be between range'},

        'defect_name_len': {'fa':'طول نام عیب بایستی حداکثر برابر باشد با',
            'en':'Defect name length most be at most'},

        'defectgroup_name_len': {'fa':'طول نام گروه عیب بایستی حداکثر برابر باشد با',
            'en':'Defect-group name length most be at most'},

        'defect_shortname_len': {'fa':'طول نام کوتاه عیب بایستی حداکثر برابر باشد با',
            'en':'Defect short-name length most be at most'},

        'no_user_logged_in': {'fa':'کاربری وارد نشده است',
            'en':'No User Logged In'},

        'username_password_empty': {'fa':'نام کاربری/گذرواژه خالی است',
            'en':'Username/password empty'},

        'some_cameras_not_calibrated': {'fa':'کالیبره نشده',
            'en':'Not calibrated'},

        'camera_summary_failed': {'fa':'خطای دریافت اطلاعات کلی دوربین ها',
            'en':'Failed to get cameras summary'},

        'calibration_summary_failed': {'fa':'خطای دریافت اطلاعات کلی کالیبراسیون',
            'en':'Failed to get calibration summary'},

        'plc_summary_failed': {'fa':'خطای دریافت اطلاعات کلی پی ال سی',
            'en':'Failed to get PLC summary'},

        'storage_summary_failed': {'fa':'خطای دریافت اطلاعات کلی حافظه',
            'en':'Failed to get storage summary'},

        'defects_summary_failed': {'fa':'خطای دریافت اطلاعات کلی عیوب',
            'en':'Failed to get defects summary'},

        'users_summary_failed': {'fa':'خطای دریافت اطلاعات کلی کاربران',
            'en':'Failed to get users summary'},



                  
}


MESSEGES = {

        'create_api_object': {'fa': 'ساخت کلاس ای پی آی',
                 'en': 'Creating API object.'},

        'initialize_login_ui': {'fa': 'ساخت کلاس واسط کاربری کاربران',
                 'en': 'Login UI object initialized.'},

        'initialize_login_api': {'fa': 'ساخت کلاس ای پی آی کاربران',
                 'en': 'Login API object initialized.'},

        'initialize_confirm_ui': {'fa': 'ساخت کلاس واسط کاربری تایید',
                 'en': 'Confirmaton UI object initialized.'},

        'initialize_notif_ui': {'fa': 'ساخت کلاس واسط کاربری اعلانات',
                 'en': 'Notficaion UI object initialized.'},

        'initialize_database_object': {'fa': 'ساخت کلاس دیتابیس',
                 'en': 'Database object initialized.'},

        'get_available_camera_serials': {'fa': 'دریافت اطلاعات دوربین های فعال در دسترس',
                 'en': 'Get available camera serials using camera-connecton API.'},

        'initialize_storage_check_timer': {'fa': 'ساخت تایمر بررسی وضعیت حافظه',
                 'en': 'Timer for checking storage initialized.'},

        'initialize_dashborad_refresh_timer': {'fa': 'ساخت تایمر نوسازی داشبورد',
                 'en': 'Timer for refreshing dashboard initialized.'},

        'stop_storage_check_timer': {'fa': 'توقف تایمر بررسی وضعیت حافظه',
                 'en': 'Timer for checking storage stopeed.'},

        'user_logged_out': {'fa': 'کاربر از حساب کاربری خود خارج شد',
                 'en': 'User logged-out from account'},

        'user_logged_in': {'fa': 'کاربر وارد حساب کاربری خود شد',
                 'en': 'User logged-in to account'},

        'storage_ok': {'fa': 'حافظه در وضعیت خوبی قرار دارد',
                 'en': 'Storage statues OK'},

        'storage_cleared': {'fa': 'اسناد قدیمی موجود در درایو پاکسازی شده و اکنون درایو در وضعیت خوبی قرار دارد',
                 'en': 'Old files cleared, space available now'},
                 
        'camera_live_drive_params_applied': {'fa': 'تنظیمات درایو دخیره سازی تصاویر دوربین اعمال شد',
                 'en': 'Settings for camera live drive applied'},

        'mainsetting_applied': {'fa': 'تنظیمات اعمال شد',
                 'en': 'Settings Applied Successfully'},

        'database_laod_users_list': {'fa': 'دریافت لیست کاربران از دیتابیس',
                 'en': 'Users list loaded from database'},

        'new_user_created': {'fa': 'کاربر جدید ایجاد شد',
                 'en': 'New user created'},

        'users_removed': {'fa': 'کاربران حذف شدند',
                 'en': 'Users removed'},

        'database_load_defects': {'fa': 'دریافت لیست عیوب از دیتابیس',
                 'en': 'Defects loaded from database'},

        'database_load_defect_groups': {'fa': 'دریافت لیست گروه عیوب از دیتابیس',
                 'en': 'Defect groups loaded from database'},

        'crate_new_defect': {'fa': 'عیب جدید ساخته ایجاد شد',
                 'en': 'New defect created'},

        'crate_new_defect_group': {'fa': 'گروه عیب جدید ساخته ایجاد شد',
                 'en': 'New defect group created'},

        'edit_defect': {'fa': 'عیب تفییر داده شد',
                 'en': 'Defect changed successfully'},

        'edit_defect_group': {'fa': 'گروه عیب تفییر داده شد',
                 'en': 'Defect group changed successfully'},

        'defect_on_edit': {'fa': 'یک عیب برای تغییر انتخاب شد',
                 'en': 'Defect selected to edit'},

        'defect_group_on_edit': {'fa': 'یک گروه عیب برای تغییر انتخاب شد',
                 'en': 'Defect group selected to edit'},

        'remove_defects': {'fa': 'عیب(ها) حذف شدند',
                 'en': 'Defect(s) removed successfully'},

        'remove_defect_groups': {'fa': 'کلاس عیب حذف شد',
                 'en': 'Defect group removed successfully'},

        'camera_disconnect': {'fa': 'اتصال دوربین قطع شد',
                 'en': 'Disconnected from camera'},

        'camera_connect': {'fa': 'اتصال دوربین وصل شد',
                 'en': 'Connected to camera'},

        'database_loade_camera_params': {'fa': 'پارامترهای دوربین از دیتابیس دریافت شدند',
                 'en': 'Camera params are loaded from database'},

        'database_apply_camera_setting': {'fa': 'پارامترهای دوربین در دیتابیس ذخیره شد',
                 'en': 'Camera parameters applied to databse'},

        'database_apply_camera_calibration_params': {'fa': 'پارامترهای کالیبراسیون در دیتابیس ذخیره شد',
                 'en': 'Calibration parmeters applied to database'},

        'pxvalue_calibration_apply': {'fa': 'کالیبراسیون ارزش پیکسلی اعمال شد',
                 'en': 'Pixel-value calibration applied'},

        'plc_connection_apply': {'fa': 'اتصال به پی ال سی برقرار شد',
                 'en': 'Connection to PLC established'},

        'plc_disconnected': {'fa': 'اتصال به پی ال سی قطع شد',
                 'en': 'Disconnected from PLC'},

        'plc_start_connecting': {'fa': 'برقراری اتصال با پی ال سی',
                 'en': 'Start Connecting to PLC'},

        
        'database_set_plc_ip': {'fa': 'آی پی پی ال سی در دیتابیس ذخیره شد',
                 'en': 'PLC ip updated on database'},

        'database_get_plc_ip': {'fa': 'آی پی پی ال سی از دیتابیس دریافت شد',
                 'en': 'PLC ip recieved from database'},

        'plc_set_value': {'fa': 'مقدار متغیر در پی ال سی آپدیت شد',
                 'en': 'Vaule updated on PLC'},

        'database_update_plc_params': {'fa': 'پارامترهای پی ال سی در دیتابیس آپدیت شدند',
                 'en': 'PLC params updated on database'},
        
        'database_get_plc_params': {'fa': 'پارامترهای پی ال سی از دیتابیس دریافت شد',
                 'en': 'PLC params reciecved from database'},

        'translate_ui_to_persian': {'fa': 'زبان نرم افزار به فارسی تغییر کرد',
                 'en': 'App language changed to Persian'},

        'translate_ui_to_english': {'fa': 'زبان نرم افزار به انگلیسی تغییر کرد',
                 'en': 'App language changed to English'},

        'app_close_change_language': {'fa': 'برای تغییر زبان، نرم افزار بایستی ریستارت شود',
                 'en': 'App most be restarted to change language'},

        'read_storage_check_interval_from_json': {'fa':'مقدار فاصله زمانی چک حافظه از فایل شروع دریافت شد',
            'en':'Storage check interval was read from startup json'},

        'read_dashboard_refresh_interval_from_json': {'fa':'مقدار فاصله زمانی نوسازی داشبورد از فایل شروع دریافت شد',
            'en':'Dashboard refresh interval was read from startup json'},

        'storage_check_interval_changed': {'fa':'مقدار فاصله زمانی چک حافظه تغییر داده شد',
            'en':'Storage check interval was changed'},

        'adding_defalt_user': {'fa':'اضافه کردن کاربر پیش فرض به دیتابیس',
            'en':'Adding default user to database'},

        'adding_defalt_defect': {'fa':'اضافه کردن عیب پیش فرض به دیتابیس',
            'en':'Adding default defect to database'},

        'adding_defalt_defectgroup': {'fa':'اضافه کردن گروه عیب پیش فرض به دیتابیس',
            'en':'Adding default defect-group to database'},

        'login_success': {'fa':'تایید ورود',
            'en':'Login successfully'},

        'all_cameras_calibrated': {'fa':'کالیبره شده',
            'en':'All calibrated'},



                 
                    
}


Titles = {
        
        'PLC (OPC) IP': {'fa':'آی پی پی ال سی'},
        'Connect': {'fa':'اتصال'},
        'Options': {'fa':'تنظیمات'},
        'Disconnect': {'fa':'قطع اتصال'},
        'Message': {'fa':'پیغام'},
        'PLC Addresses and Values': {'fa':'آدرس ها و مقادیر پی ال سی'},
        'Top Limit Switch': {'fa':'لیمیت سوویچ بالا'},
        'Bottom Limit Switch': {'fa':'لیمیت سوویچ پایین'},
        'Thermometer Min': {'fa':'کمینه دماسنج'},
        'Thermometer Max': {'fa':'بیشینه دماسنج'},
        'Cooling Up-Time (s)': {'fa':'زمان کار خنک کننده (ثانیه)'},
        'System Operating': {'fa':'عملکرد سیستم'},
        'Air Electric Valve': {'fa':'شیر برقی هوا'},
        'Cameras Limit': {'fa':'محدودیت دوربین ها'},
        'Camera Frame Rate': {'fa':'نرخ تصویربرداری دوربین ها'},
        'Projectors Limit': {'fa':'محدودیت پروژکتورها'},
        'Coil Detect Sensor': {'fa':'سنسور تشخیص ورق'},
        'Off Value': {'fa':'مقدار خاموش'},
        'On Value': {'fa':'مقدار روشن'},
        'Min Value': {'fa':'مقدار کمینه'},
        'Max Value': {'fa':'مقدار بیشینه'},
        'Max Value': {'fa':'مقدار بیشینه'},
        'Check': {'fa':'چک کردن'},
        'Value': {'fa':'مقدار'},
        'Data Value': {'fa':'مقدار داده'},
        'Check All Addresses': {'fa':'چک کردن همه'},
        'Save PLC Parameters': {'fa':'ذخیره پارامترها'},
        'Addresses': {'fa':'آدرس ها'},
        'Path': {'fa':'مسیر'},
        'Set Value': {'fa':'اختصاص مقدار'},
        'Current Value': {'fa':'مقدار فعلی'},
        'New Value': {'fa':'مقدار جدید'},
        'Set PLC Value': {'fa':'اختصاص مقدار به پی ال سی'},

        'Camera Management': {'fa':'مدیریت دوربین ها'},
        'Calibration Management': {'fa':'مدیریت کالیبراسیون'},
        'PLC Management': {'fa':'مدیریت پی ال سی'},
        'Storage Management': {'fa':'مدیریت حافظه'},
        'Defects Management': {'fa':'مدیریت عیوب'},
        'Users Management': {'fa':'مدیریت کاربران'},
        'Level-2 Management': {'fa':'مدیریت لول 2'},
        'General Settings': {'fa':'تنظیمات عمومی'},
        'Dashboard': {'fa':'داشبورد'},
        'Close': {'fa':'بستن'},
        'Minimize': {'fa':'کوچکنمایی'},
        'Maximize': {'fa':'بزرگنمایی'},
        'No User Logged In': {'fa':'کاربری وارد نشده است'},
        'Defined Defects': {'fa':'عیوب تعریف شده'},
        'Defined Defect-Groups': {'fa':'کلاس عیوب تعریف شده'},
        'Available Cameras': {'fa':'دوربین های در دسترس'},
        'Mean Temperature': {'fa':'میانگین دما'},
        'Image Peocessing': {'fa':'پردازش تصویر'},
        'Width Guage': {'fa':'عرض سنج'},
        'Status': {'fa':'وضعیت'},
        'Default Drive': {'fa':'درایو پیشفرض'},
        'Total Space': {'fa':'حافظه کلی'},
        'Used Space': {'fa':'حافظه استفاده شده'},
        'Defined Users': {'fa':'کاربران تعریف شده'},
        'Connected': {'fa':'متصل شده', 'en': 'Connected'},
        'Disconnected': {'fa':'نامتصل', 'en':'Disconnected'},

        'Add User': {'fa':'افزودن کاربر'},
        'Deatils': {'fa':'جزئیات'},
        'Remove User': {'fa':'حذف کاربر'},
        'Create User': {'fa':'افزودن کاربر'},
        'Remove User': {'fa':'حذف کاربر'},
        'ADD New User': {'fa':'افزودن کاربر جدید'},
        'Username': {'fa':'نام کاربری'},
        'Password': {'fa':'گذرواژه'},
        'Re-Enter Password': {'fa':'تکرار گذرواژه'},
        'User Role': {'fa':'نقش کاربر'},
        'Details Of Selected User': {'fa':'اطلاعات کاربر انتخاب شده'},
        'Users List': {'fa':'لیست کاربران'},

        'Camera': {'fa':'دوربین'},
        'Serial Number': {'fa':'شماره سریال'},
        'Gain': {'fa':'گین'},
        'Exposure': {'fa':'اکسپوژر'},
        'Width': {'fa':'عرض'},
        'Height': {'fa':'طول'},
        'Offset X': {'fa':'آفست عرض'},
        'Offset Y': {'fa':'آفست طول'},
        'Trigger Mode': {'fa':'تریگر'},
        'Max Buffer': {'fa':'بافر'},
        'Packet Delay': {'fa':'تاخیر بسته'},
        'Packet Size': {'fa':'طول بسته'},
        'Transmision Delay': {'fa':'تاخیر انتقال'},
        'IP Address': {'fa':'آدرس آی پی'},
        'Apply Settings': {'fa':'اعمال تنظیمات'},
        'Get Picture': {'fa':'دریافت تصویر'},
        'Select Top Cameras': {'fa':'انتخاب دوربین های بالا'},
        'Select Bottom Cameras': {'fa':'انتخاب دوربین های پایین'},

        'Appearance Parameters': {'fa':'پارامترهای دیداری'},
        'Style': {'fa':'استایل'},
        'Color': {'fa':'رنگ'},
        'Font-Style': {'fa':'استایل فونت'},
        'Font-Size': {'fa':'سایز فونت'},
        'Language': {'fa':'زبان'},
        'Defects Parameters': {'fa':'پارامترهای عیوب'},
        'Colors Number': {'fa':'تعداد رنگ'},
        'Calibration Parameters': {'fa':'پارامترهای کالیبراسیون'},
        'Large Rectangle Area': {'fa':'مساحت مستطیل بزرگ'},
        'Small Rectangle Area': {'fa':'مساحت مستطیل کوچک'},
        'Rectangle Accuracy': {'fa':'دقت مستطیل بودن'},
        'Split-Size': {'fa':'سایز تقسیم بندی'},
        'Num Camera Threads': {'fa':'تعداد تردهای دوربین'},
        'Num Camera Process': {'fa':'تعداد پروسس های دوربین'},
        'Num Writing Threads': {'fa':'تعداد تردهای ذخیره سازی'},
        'Camera Refresh-Rate (ms)': {'fa':'نرخ نوسازی تصویر (میلی ثانیه)'},

        'Defects List': {'fa':'لیست عیوب'},
        'Defect-Groups List': {'fa':'لیست گروه های عیب'},
        'Edit Defect': {'fa':'ویرایش عیب'},
        'Remove Defect(s)': {'fa':'حذف عیب'},
        'Search/Filter Defect(s)': {'fa':'جستجو/فیلتر عیب ها'},
        'Defect Name': {'fa':'نام عیب'},
        'Is Defect': {'fa':'عیب بودن'},
        'Defect-Group': {'fa':'گروه عیب'},
        'Defect Level': {'fa':'سطح عیب'},
        'Search/Filter': {'fa':'جستجو/فیلتر'},
        'Clear Filters': {'fa':'حذف فیلترها'},
        'Defect Short-Name': {'fa':'نام کوتاه عیب'},
        'Defect ID': {'fa':'شناسه عیب'},
        'Defect Color Label': {'fa':'رنگ برچسب عیب'},
        'Create/Apply Defect': {'fa':'ایجاد/ثبت عیب'},
        'Show Related  defects': {'fa':'نمایش عیب های مربوط'},
        'Edit Defect-Group': {'fa':'ویرایش گروه عیب'},
        'Remove Defect-Group': {'fa':'حذف گروه عیب'},
        'Search/Filter Defect-Group(s)': {'fa':'جستجو/فیلتر گروه عیب'},
        'Defect-Group Name': {'fa':'نام گروه عیب'},
        'ADD/Edit  Defect-Group': {'fa':'افزودن/ویرایش گروه عیب'},
        'ADD/Edit Defect': {'fa':'افزودن/ویرایش عیب'},
        'Defect-Group ID': {'fa':'شناسه گروه عیب'},
        'Yes': {'fa':'بله'},
        'No': {'fa':'خیر'},
        'Create/Apply Defect-Group': {'fa':'ایجاد/ثبت گروه عیب'},
        'Created Date': {'fa':'تاریخ ایجاد'},

        'Camera Live Storage Management': {'fa':'مدیریت حافظه تصاویر دوربین ها'},
        'Drive Path': {'fa':'آدرس درایو'},
        'Max Used Space (%)': {'fa':'بیشینه حافظه پرشده (%)'},
        'Optimal Used Space (%)': {'fa':'حافظه پرشده بهینه (%)'},
        'Storage Statues': {'fa':'وضعیت حافظه'},
        'Force Clear Storage': {'fa':'پاکسازی حافظه'},
        'Current Used Space (%)': {'fa':'حافظه استفاده شده فعلی (%)'},
        'Current Statues': {'fa':'وضعیت فعلی حافظه'},
        'Storage Check Interval (s)': {'fa':'فاصله زمانی چک حافظه (ثانیه)'},

        'Optimal Used Space': {'fa':'حافظه پرشده بهینه'},
        'Warning Used Space': {'fa':'حافظه پرشده هشدار'},
        'Critical Used Space': {'fa':'حافظه پرشده بحرانی'},
        'Warning Used Space': {'fa':'حافظه پرشده هشدار'},
        'Free Space': {'fa':'حافظه خالی/آزاد'},
        'Space (Gigabyte)': {'fa':'حافظه (گیگابایت)'},

        'User Login': {'fa':'ورود کاربر'},
        'Login': {'fa':'ورود'},







}


