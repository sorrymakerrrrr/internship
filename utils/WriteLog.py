import os
import datetime
from Save import FSave


def write_log(log_dst: str, logs_list: list, company: str, log_name: str) -> str:
    """
    :param log_dst: 日志存放路径
    :param logs_list: 日志列表
    :param company: 当前公司
    :param log_name: 日志命名
    :return: 是否成功
    """
    dst = log_dst
    time = datetime.date.strftime(datetime.datetime.today(), "%Y%m%d")
    los_name = f'{log_name}-{company}-{time}.txt'
    logs = '\n'.join(logs_list) + '\n'
    FSave.mkdir(dst)
    with open(os.path.join(dst, los_name), mode='w', encoding='utf-8') as f:
        f.write(logs)
    return '日志写入成功!'
