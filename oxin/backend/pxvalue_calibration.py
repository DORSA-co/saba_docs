from matplotlib import backends
import numpy as np
import cv2
from scipy.spatial import distance
from . import colors_pallete, camera_funcs, mainsetting_funcs, texts



def draw_contour(gray, cnts):
    img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    img = cv2.drawContours( img, cnts , -1, (0,0,255), thickness=3)
    return img


def draw_rect(gray, cnts, areas):
    img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    #print(len(cnts))
    for i,cnt in enumerate(cnts):
        x,y,w,h = cv2.boundingRect(cnt)
        color = (np.random.randint(0,255),np.random.randint(0,255),np.random.randint(0,255),)
        cv2.putText( img, str(areas[i]) , (x,y) , cv2.FONT_HERSHEY_DUPLEX, 1, color )
        img = cv2.drawContours( img, [cnt] , 0, color, thickness=3)
    return img



class extract_info():
    def __init__(self, gray, areas_mm , min_area=2000, max_area=50000 , accuracy = 0.9, gray_thrs=100):
        self.nrects = len(areas_mm)
        self.areas_mm = list(areas_mm)
        self.gray = np.array(gray, dtype=np.uint8)
        self.min_area = min_area
        self.max_area = max_area
        self.accuracy = accuracy
        self.gray_thrs = gray_thrs

    
    def thrs_map(self):
        _, mask = cv2.threshold(self.gray, self.gray_thrs, 255, cv2.THRESH_BINARY)
        return mask

    
    def find_contours(self, mask):
        cnts,_ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        img = draw_contour(self.gray, cnts)
        return img, cnts
        
    
    def filter_contours_by_area(self, cnts):
        filter_area = lambda x: self.min_area< cv2.contourArea(x) < self.max_area
        cnts = list( filter( filter_area, cnts))
        img = draw_contour( self.gray, cnts)
        return img, cnts

    
    def filter_acc(self, x):
        _,(w,h),_ = cv2.minAreaRect(x)
        rect_area = w*h
        area = cv2.contourArea(x)
        return area/rect_area > self.accuracy

    def filter_contours_by_accuracy(self, cnts):
        cnts = list( filter( self.filter_acc, cnts))
        img = draw_contour( self.gray, cnts)
        return img, cnts

    
    def draw_rects(self, cnts):
        cnts.sort(key = lambda x:cv2.contourArea(x), reverse=True)
        rects = cnts[:self.nrects]
        self.areas_mm.sort(reverse=True)
        img = draw_rect( self.gray, rects, self.areas_mm)
        return img, rects


    def final_decision(self, cnts, rects):
        # check if all 6 rects are detected
        if len(cnts) < self.nrects:
            return False, 0, 0
        # else
        infoes = []
        for i in range(len(rects)):
            (x,y),_,_ = cv2.minAreaRect(rects[i])
            area_px = cv2.contourArea(rects[i])
            area_mm = self.areas_mm[i]
            px2mm = np.sqrt( area_mm/ area_px )
            infoes.append([x,y , px2mm])
        infoes = np.array(infoes)
        # sorting contours to assign each small rect to its paired large rect (check by rects centers)
        infoes_final = []
        for i in range(len(rects)//2):
            large_rect = (infoes[i,0], infoes[i,1])
            dist_min = np.Infinity
            j_itr = 0
            for j in range(len(rects)//2, len(rects)):
                small_rect = (infoes[j,0], infoes[j,1])
                # check distance
                if distance.euclidean(large_rect, small_rect) <= dist_min:
                    dist_min = distance.euclidean(large_rect, small_rect)
                    j_itr = j
            # append
            infoes_final.append(np.mean(np.array([infoes[i], infoes[j_itr]]), axis=0))
            
        return True, infoes, np.array(infoes_final)


    def solve_equation( self, inputs ):
        inputs = np.array(inputs)
        inputs = np.insert(inputs, -1, 1, axis=1)

        d = np.copy( inputs[:,:3] )
        
        dx = np.copy( d )
        dx[:,0] = inputs[:,-1]
        
        dy = np.copy( d )
        dy[:,1] = inputs[:,-1]
        
        dz = np.copy( d )
        dz[:,2] = inputs[:,-1]

        d = np.linalg.det(d)
        dx = np.linalg.det(dx)
        dy = np.linalg.det(dy)
        dz = np.linalg.det(dz)

        kx = dx/d
        ky = dy/d
        kz = dz/d
        return np.array([kx,ky,kz])



# pixel value calibration
def apply_pxvalue_calibration(ui_obj, api_obj, db_obj, image, next=True):       
    step = api_obj.pxcalibration_step
    api_obj.pxcalibration_step = 0
    # disable apply button and soft-calibration params if enable
    ui_obj.calib_save_params.setEnabled(False)
    ui_obj.calib_rotate_spinbox.setEnabled(False)
    ui_obj.calib_shifth_spinbox.setEnabled(False)
    ui_obj.calib_shiftw_spinbox.setEnabled(False)
    ui_obj.calib_radio_corsshair.setEnabled(False)
    ui_obj.calib_radio_grid.setEnabled(False)
    #
    try:
        if image == None:
            ui_obj.show_mesagges(ui_obj.camera_calibration_message_label, texts.WARNINGS['camera_no_picture'][ui_obj.language], level=1)
            return
    except:
        # select wheather apply or not soft-calibration to image
        camera_calibration_params = camera_funcs.get_camera_calibration_params_from_ui(ui_obj=ui_obj)
        image = camera_funcs.apply_soft_calibrate_on_image(ui_obj=ui_obj, image=image, camera_calibration_params=camera_calibration_params, pxcalibration=True)
        # apply pxvalue calibration
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # get calibration params from database and UI
        rect_areas, rect_acc = mainsetting_funcs.get_mainsetting_params_from_db(db_obj=db_obj, mode='px_calibration')
        min_area = camera_calibration_params['calib_minarea']
        max_area = camera_calibration_params['calib_maxarea']
        gray_thrs = camera_calibration_params['calib_thrs']
        # define calibration class
        calibration_obj = extract_info(gray=image, areas_mm=rect_areas, min_area=min_area, max_area=max_area, accuracy=rect_acc, gray_thrs=gray_thrs)
    # next
    if next:
        #
        if step >= 0:
            img = calibration_obj.thrs_map()
            api_obj.pxcalibration_step += 1
            ui_obj.pixelvalue_prev_btn.setEnabled(True)
        #
        if step >= 1:
            img, cnts = calibration_obj.find_contours(img)
            api_obj.pxcalibration_step += 1
        #
        if step >= 2:
            img, cnts = calibration_obj.filter_contours_by_area(cnts)
            api_obj.pxcalibration_step += 1
        #
        if step >= 3:
            img, cnts = calibration_obj.filter_contours_by_accuracy(cnts)
            api_obj.pxcalibration_step += 1
        #
        if step >= 4:
            img, rects = calibration_obj.draw_rects(cnts)
            api_obj.pxcalibration_step += 1
        #
        if step >= 5:
            succ, _, infoes = calibration_obj.final_decision(cnts, rects)
            ui_obj.pixelvalue_next_btn.setEnabled(False)
            api_obj.pxcalibration_step += 1
    # prev
    if not next:
        #
        if step >= 1:
            img = image
            ui_obj.pixelvalue_prev_btn.setEnabled(False)
            api_obj.pxcalibration_step = step - 1
        #
        if step >= 2:
            img = calibration_obj.thrs_map()
            api_obj.pxcalibration_step = step - 1
            ui_obj.pixelvalue_prev_btn.setEnabled(True)
        #
        if step >= 3:
            img, cnts = calibration_obj.find_contours(img)
            api_obj.pxcalibration_step = step - 1
            #
        if step >= 4:
            img, cnts = calibration_obj.filter_contours_by_area(cnts)
            api_obj.pxcalibration_step = step - 1
        #
        if step >= 5:
            img, cnts = calibration_obj.filter_contours_by_accuracy(cnts)
            api_obj.pxcalibration_step = step - 1
        #
        if step >= 6:
            img, rects = calibration_obj.draw_rects(cnts)
            api_obj.pxcalibration_step = step - 1
            ui_obj.pixelvalue_next_btn.setEnabled(True)
    # set image to UI
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    camera_funcs.set_camera_picture_to_ui(ui_image_label=ui_obj.calib_camera_image, image=img)
    # validate
    if step >= 5 and next:
        if succ:
            pxvalue_params = calibration_obj.solve_equation(infoes)
            # apply to UI
            ui_obj.pxvaluea_label.setText(pxvalue_params[0])
            ui_obj.pxvalueb_label.setText(pxvalue_params[1])
            ui_obj.pxvaluec_label.setText(pxvalue_params[2])
            # show message
            ui_obj.show_mesagges(ui_obj.camera_calibration_message_label, texts.MESSEGES['pxvalue_calibration_apply'][ui_obj.language], level=0)
            ui_obj.logger.create_new_log(message=texts.MESSEGES['pxvalue_calibration_apply']['en'], level=1)
            # enable apply button
            ui_obj.calib_save_params.setEnabled(True)
        else:
            # show message
            ui_obj.show_mesagges(ui_obj.camera_calibration_message_label, texts.ERRORS['pxvalue_calibration_apply_failed'][ui_obj.language], level=2)
