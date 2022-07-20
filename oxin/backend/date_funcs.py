from persiantools.jdatetime import JalaliDate
import datetime


def get_date(persian=True, folder_path=False):
    """
    this function retrns current date, wheter in persian or miladi.

    Inputs:
        persian: a bolean value determining the foramt of date (in persian or miladi)
        folder_path: a boolean value determiningn if the date will be used as a folder name or not
    
    :returns:
        date: current date (in string)
    """

    # persian date
    if persian:
        # get day
        day = str(JalaliDate.today().day)
        if len(day)==1:
            day = '0' + day
        #
        # get month
        month = str(JalaliDate.today().month)
        if len(month)==1:
            month = '0' + month
        #
        # full date string
        if not folder_path:
            date = '%s/%s/%s' % (JalaliDate.today().year, month, day)
        else:
            date = '%s-%s-%s' % (JalaliDate.today().year, month, day)

    # miladi date
    else:
        # get day
        day = str(datetime.datetime.today().date().day)
        if len(day)==1:
            day = '0' + day
        #
        # get month
        month = str(datetime.datetime.today().date().month)
        if len(month)==1:
            month = '0' + month
        #
        # full date string
        if not folder_path:
            date = '%s/%s/%s' % (datetime.datetime.today().date().year, month, day)
        else:
            date = '%s-%s-%s' % (datetime.datetime.today().date().year, month, day)

    return date


def get_time(folder_path=False):
    """
    this functionn :returns: current time

    Inputs: 
        folder_path: a boolean value determiningn if the date will be used as a folder name or not
    
    :returns:
        time: current time (in string)
    """

    time = datetime.datetime.now()
    
    if not folder_path:
        time = str(time.strftime("%H:%M:%S"))
    else:
        time = str(time.strftime("%H-%M-%S"))
    
    return time


def get_datetime(persian=True, folder_path=True):
    """
    this function returns both curent date and time in wheater persian or miladi format

    :param persian: a bolean value determining the foramt of date (in persian or miladi)
    :param folder_path: a boolean value determiningn if the date will be used as a folder name or not
    
    :returns: date and time: current date and time (in string)
    """
    
    date = get_date(persian=persian, folder_path=folder_path)
    time = get_time(folder_path=folder_path)

    return date + "-" + time



if __name__ == "__main__":
    
    print(get_datetime(persian=True, folder_path=True))

    