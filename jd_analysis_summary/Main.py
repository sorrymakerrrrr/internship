from JDSummary import SalarySummary
from JDAnalysisSummarySave import Save


def main3(src: str, dst: str, month: int, header: int = 0):
    sum_ = SalarySummary(src, month)
    sheet_names = sum_.sheet_names  # ['9、10月相同岗位数据', '10月删减岗位数据', '10月新增岗位数据']
    rows = ('公司', '工作经验')
    sum_infos = ('薪资变化幅度', '薪资变化岗位个数')
    dfs = []
    # JD监控相同岗位的薪资变化幅度与岗位变化个数 (四张表)
    for row in rows:
        for sum_info in sum_infos:
            df = sum_.summary(sheet_name=sheet_names[0], header=header, row=row, cur_month=month, sum_info=sum_info)
            dfs.append(df)
    # JD监控增加与减少岗位的薪资变化岗位个数 (四张表)
    for sheet_name in sheet_names[1:]:
        for row in rows:
            df = sum_.summary(sheet_name=sheet_name, header=header, row=row)
            dfs.append(df)

    sheet_names_to_save = [f'{month}月薪资变化幅度（按公司）', f'{month}月薪资变化幅度（按职级）',
                           f'{month}月薪资变化岗位数量（按公司）', f'{month}月薪资变化岗位数量（按职级）',
                           f'{month}月删减岗位数量（按公司）', f'{month}月删减岗位数量（按职级）',
                           f'{month}月新增岗位数量（按公司）', f'{month}月新增岗位数量（按职级）']

    save = Save(dst=dst, sheet_names=sheet_names_to_save)
    save.single_table_save(dfs=dfs, table_name='JD分析汇总表', index=False)


if __name__ == '__main__':
    main3(src=r'E:\job\11月内容\9,10月JD监控', dst=r'E:\job\11月内容\9,10月JD监控', month=10, header=0)
