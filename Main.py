import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
add_path = [os.path.join(base_dir, path) for path in os.listdir(base_dir)]
sys.path.extend(add_path)

from processing.Main import main1
from jd_monitoring.Main import main2
from jd_analysis_summary.Main import main3


def main(src1: str, src2: str, dst: str, cur_month: int):
    """
    进行岗位数据预处理、JD监控表生成与JD汇总表生成的入口函数
    :param src1: boss直聘上爬取的当前月份的岗位原始数据
    :param src2: boss直聘上爬取的前一月份的岗位原始数据
    :param dst: 所有表生成的根目录
    :param cur_month: 当前月份
    :return: None
    """
    pre_month = 12 if cur_month == 1 else cur_month - 1
    # 当前月岗位数据预处理
    main1(src=src1,
          dst=os.path.join(dst, '10月预处理'),
          log_dst=os.path.join(dst, '岗位去重', f'{cur_month}月岗位去重日志'),
          table_name=rf'{cur_month}月岗位预处理总表')

    # 之前月岗位数据预处理
    main1(src=src2,
          dst=os.path.join(dst, '9月预处理'),
          log_dst=os.path.join(dst, '岗位去重', f'{pre_month}月岗位去重日志'),
          table_name=rf'{pre_month}月岗位预处理总表')

    # JD监控合并表
    main2(src1=os.path.join(dst, f'{cur_month}月预处理', '分表'),
          src2=os.path.join(dst, f'{pre_month}月预处理', '分表'),
          dst=os.path.join(dst, 'JD监控表'),
          log_dst=os.path.join(dst, '岗位去重', 'JD监控去重日志'),
          month=cur_month)

    # JD监控分析汇总表
    path = os.path.join(dst, 'JD监控表', '总表')
    main3(src=os.path.join(path, os.listdir(path)[0]),
          dst=os.path.join(dst, 'JD监控表'),
          month=cur_month)


if __name__ == '__main__':
    main(src1=r'E:\job\岗位处理\9月岗位原始数据',
         src2=r'E:\job\岗位处理\10月岗位原始数据',
         dst=r'E:\job\岗位处理',
         cur_month=10)
