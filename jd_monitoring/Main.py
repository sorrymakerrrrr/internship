from JDTableMerge import JDMerge
from JDMonitorSave import Save


def main2(src1: str, src2: str, dst: str, log_dst: str, month: int):
    """
    JD监控入口
    :param src1: 当前月份数据预处理所在文件夹
    :param src2: 之前月份数据预处理所在文件夹
    :param dst: 保存文件的根目录
    :param log_dst: 保存去重日志文件的文件夹
    :param month: 当前月份
    :return: None
    """
    merge = JDMerge(src1=src1, src2=src2, log_dst=log_dst, cur_month=month)
    save = Save(dst=dst, cur_month=month)
    dfs = []
    save.set_dst(rf'{dst}\分表')
    for company in merge.all_company:

        if type(merge.single_merge(company=company, header=0)) == str:
            print(merge.single_merge(company=company, header=0))
            break

        df_merge, df2_remain, df1_remain = merge.single_merge(company=company, header=0)
        dfs_ = [df_merge, df2_remain, df1_remain]
        save.single_table_save(dfs_, table_name=f'{company} {month}月JD监控表')
        dfs.append(dfs_)
    save.set_dst(rf'{dst}\总表')
    save.merge_table_save(dfs, table_name=f'{month}月JD监控总表')


if __name__ == '__main__':
    main2(src1=r'E:\job\11月内容\9,10月JD监控\分表',
          src2=r'E:\job\11月内容\9月游戏岗位预处理分表',
          dst=r'E:\job\11月内容\9,10月JD监控',
          log_dst=r'E:\job\11月内容\JD监控去重',
          month=10)
