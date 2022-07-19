import xml.etree.ElementTree as ET
from .backend import texts


def translate_ui(language='fa', ui_file_path_en='main_window.ui', ui_file_path_fa='main_window_fa.ui'):
    """
    This function takes as input the default english version ui file, and translate it to input language

    Inputs:
        language: input language to translate ui to (in string), default is fa (stands for farsi/persian)
        ui_file_path_en: path of the default english ui file (in string)
        ui_file_path_fa: path of the output translated ui file to save (in string)

    Returns: None
    """

    # persian lanuage
    if language == 'fa':

        try:
            # load ui file in qml format
            qml_tree = ET.ElementTree(file=ui_file_path_en)

            # get string tags in file (most probably containing titles in ui)
            all_name_elements = qml_tree.findall('.//string')

            # replace english titles with persian ones, by searching in texts dict
            for element in all_name_elements:
                if element.text in texts.Titles.keys():
                    element.text = texts.Titles[element.text]['fa']
            
            # save the new transalted file
            qml_tree.write(ui_file_path_fa)

            print('ui translated to persian')
            
        except:
            print('fialed to translate ui')
        


if __name__ == "__main__":
    translate_ui()
    