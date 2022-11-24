import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
add_path = [os.path.join(base_dir, path) for path in os.listdir(base_dir)]
sys.path.extend(add_path)

from processing.Main import main1
from jd_monitoring.Main import main2
from jd_analysis_summary.Main import main3

# 十月岗位数据预处理
main1(src=r'E:\job\10月内容\10月岗位原始数据',
      dst=r'E:\job\11月内容\9,10月JD监控\10月预处理',
      log_dst=r'E:\job\11月内容\9,10月JD监控\10月岗位去重日志',
      table_name=r'10月岗位预处理总表')

# 九月岗位数据预处理
main1(r'E:\job\9月内容\9月岗位原始数据',
      r'E:\job\11月内容\9,10月JD监控\9月预处理',
      r'E:\job\11月内容\9,10月JD监控\9月岗位去重日志',
      r'9月岗位预处理总表')

# JD监控合并表
main2(src1=r'E:\job\11月内容\9,10月JD监控\10月预处理\分表',
      src2=r'E:\job\11月内容\9,10月JD监控\9月预处理\分表',
      dst=r'E:\job\11月内容\9,10月JD监控\JD监控表',
      log_dst=r'E:\job\11月内容\9,10月JD监控\JD监控去重日志',
      month=10)

# JD监控分析汇总表
main3(src=os.path.join(r'E:\job\11月内容\9,10月JD监控\JD监控表\总表',
                       os.listdir(r'E:\job\11月内容\9,10月JD监控\JD监控表\总表')[0]),
      dst=r'E:\job\11月内容\9,10月JD监控',
      month=10)
