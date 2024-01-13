import datetime
import time


class TimeUtils:
    """
    时间转换工具类
    """

    @staticmethod
    def string_to_datetime(date_string, ft=None):
        if ft is None:
            ft = "%Y-%m-%d %H:%M:%S"
        return datetime.datetime.strptime(date_string, ft)

    @staticmethod
    def datetime_to_string_yymmddhhmmss(dt=None):
        if dt is None:
            dt = datetime.datetime.now()
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def datetime_to_string_yymmdd(dt=None, ft=None):
        if dt is None:
            dt = datetime.datetime.now()
        if ft is None:
            ft = "%Y-%m-%d"
        return dt.strftime(ft)

    @staticmethod
    def datetime_to_string_yymmddhhmmssms(dt=None):
        if dt is None:
            dt = datetime.datetime.now()
        return dt.strftime("%Y-%m-%d %H:%M:%S:%f")

    @staticmethod
    def get_datetime_now():
        return datetime.datetime.now()

    @staticmethod
    def get_date_now():
        return datetime.date.today()

    @staticmethod
    def datetime_equals_date(datetime1, datetime2):
        return datetime1.date() == datetime2.date()

    @staticmethod
    def datetime_to_string_yymmddhhmmss2(dt=None):
        if dt is None:
            dt = datetime.datetime.now()
        return dt.strftime("%Y%m%d%H%M%S")

    @staticmethod
    def datetime_to_string_yymmddhhmmssff(dt=None):
        if dt is None:
            dt = datetime.datetime.now()
        return dt.strftime("%Y%m%d%H%M%S%f")

    @staticmethod
    def string_to_datetime_yymm(date_string):
        return datetime.datetime.strptime(date_string, "%Y-%m")

    @staticmethod
    def string_to_datetime_yymmdd(date_string):
        return datetime.datetime.strptime(date_string, "%Y-%m-%d")

    @staticmethod
    def day_zero(dt=None):
        """获取某天零点"""
        if dt is None:
            dt = datetime.datetime.now()
        return dt - datetime.timedelta(
            hours=dt.hour,
            minutes=dt.minute,
            seconds=dt.second,
            microseconds=dt.microsecond,
        )

    def day_latest(self, dt=None):
        """获取某天的 23:59:59"""
        return self.day_zero(dt) + datetime.timedelta(hours=23, minutes=59, seconds=59)

    @staticmethod
    def cur_timestamp(digit=13):
        return int(time.time() * 1000 if digit != 10 else time.time())

    @staticmethod
    def timestamp_to_datetime_yymmddhhmmss(ts):
        if len(str(ts)) == 13:
            ts /= 1000
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

    @staticmethod
    def relative_to_today(
        dt=None,
        days=0,
        seconds=0,
        microseconds=0,
        milliseconds=0,
        minutes=0,
        hours=0,
        weeks=0,
    ):
        timedelta_kwargs = {
            k: v
            for k, v in locals().items()
            if v and isinstance(v, (int, float)) and k != "dt"
        }
        if dt is None:
            dt = datetime.datetime.now()
        datetime_res = dt + datetime.timedelta(**timedelta_kwargs)
        return datetime_res


time_util = TimeUtils()


def timestamp_to_datetime(timestamp) -> datetime:
    """
    时间戳转datetime
    :param timestamp:秒级时间戳
    :return:
    """
    return datetime.datetime.fromtimestamp(timestamp)


if __name__ == "__main__":
    print(time_util.relative_to_today(-1))
