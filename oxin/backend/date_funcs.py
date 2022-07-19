from persiantools.jdatetime import JalaliDate
import datetime


def get_date(persian=True, folder_path=False):
    if persian:
        day = str(JalaliDate.today().day)
        if len(day)==1:
            day = '0' + day
        #
        month = str(JalaliDate.today().month)
        if len(month)==1:
            month = '0' + month
        #
        if not folder_path:
            date = '%s/%s/%s' % (JalaliDate.today().year, month, day)
        else:
            date = '%s-%s-%s' % (JalaliDate.today().year, month, day)

    else:
        day = str(datetime.datetime.today().date().day)
        if len(day)==1:
            day = '0' + day
        #
        month = str(datetime.datetime.today().date().month)
        if len(month)==1:
            month = '0' + month
        #
        if not folder_path:
            date = '%s/%s/%s' % (datetime.datetime.today().date().year, month, day)
        else:
            date = '%s-%s-%s' % (datetime.datetime.today().date().year, month, day)

    return date


def get_time(folder_path=False):
    if not folder_path:
        time = str(datetime.datetime.today().hour) + ":" + str(datetime.datetime.today().minute) + ":" + str(datetime.datetime.today().second)
    else:
        time = str(datetime.datetime.today().hour) + "-" + str(datetime.datetime.today().minute) + "-" + str(datetime.datetime.today().second)
    return time


def get_datetime(persian=True, folder_path=True):
    date = get_date(persian=persian, folder_path=folder_path)
    time = get_time(folder_path=folder_path)

    return date + "-" + time



if __name__ == "__main__":
    print(get_datetime(persian=True, folder_path=False))
    