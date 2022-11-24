import numpy as np
import pandas as pd
import re
import os
from typing import Tuple, Union
from utils.MinDistance import min_distance
from utils.WriteLog import write_log
from SalaryChangeAnalysis import SalaryAnalysis


class JDMerge:

    def __init__(self, src1: str, src2: str, log_dst: str, cur_month: int):
        """
        初始化类
        :param src1: 当前月份不同公司岗位表所在的文件夹
        :param src2: 之前月份不同公司岗位表所在的文件夹
        :param log_dst: 日志文件存放的目标文件夹
        :param cur_month: 当前月份
        """
        self.src1 = src1
        self.src2 = src2
        self.cur_month = cur_month
        self.log_dst = log_dst
        # 不同月份需要合并的所有公司名字
        self.all_company = (
            '百田', '深蓝互动', '祖龙娱乐', '冰川网络', '吉比特', '心动网络', '库洛', '完美世界', '中手游',
            '4399', '三七互娱', '字节跳动', '米哈游', '腾讯', '网易', '莉莉丝', 'funplus')

    @staticmethod
    def column_name_process(original_column_name: np.ndarray, month: int):
        """
        为原始列名做处理
        :return: 处理之后的列名
        """
        return [f'{month}月{column_name}' for column_name in original_column_name]

    def get_dataframes(self, company: str, header: int) -> Union[Tuple[pd.DataFrame, pd.DataFrame], Tuple[None, None]]:
        """
        获得company不同两个月份的表
        :param company: 指定公司
        :param header: 指定以第几行作为开头读取
        :return: 制定公司不同月份的两张JD表
        """
        dir1 = os.listdir(self.src1)
        dir2 = os.listdir(self.src2)
        pat = re.compile(rf'.*{company}.*', re.I)
        file1, file2 = None, None
        for file in dir1:
            if re.match(pat, file) is not None:
                file1 = file
                break
        for file in dir2:
            if re.match(pat, file) is not None:
                file2 = file
                break
        if file1 is None or file2 is None:
            return None, None
        df1 = pd.read_excel(os.path.join(self.src1, file1), header=header)
        df2 = pd.read_excel(os.path.join(self.src2, file2), header=header)
        return df1, df2

    def single_merge(self, company: str, header: int = 0) -> \
            Union[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame], str]:
        df1, df2 = self.get_dataframes(company, header)
        if df1 is None:
            return f'未找到{company}相关文件, 已跳过!'
        cur_month, pre_month = self.cur_month, 12 if self.cur_month == 1 else self.cur_month - 1
        # 日志列表
        logs_list = []
        # 两张表重复索引列表
        df1_duplicate_index, df2_duplicate_index = [], []
        info = f'当前处理的公司为: {company}'
        logs_list.append(info)

        merge_df_list = []
        for idx1, row1 in df1.iterrows():
            for idx2, row2 in df2.iterrows():
                exp1, exp2 = str(row1['工作经验']), str(row2['工作经验'])
                update_exp1, update_exp2 = str(row1['更新工作经验']), str(row2['更新工作经验'])
                jd1, jd2 = str(row1['职位描述']), str(row2['职位描述'])
                jr1, jr2 = str(row1['任职要求']), str(row2['任职要求'])
                # 职位描述或者任职要求为空 直接跳过
                if pd.isna(jd1) and pd.isna(jr1):
                    break
                # 如果更新工作经验为空 则用工作经验作为判断依据
                if pd.isna(update_exp1):
                    update_exp1 = exp1
                if pd.isna(update_exp2):
                    update_exp2 = exp2
                # 工作经验不一样或者字符串长度相差过大的岗位跳过
                if update_exp1 != update_exp2 or abs(len(jd1) - len(jd2)) >= 50 or abs(len(jr1) - len(jr2)) >= 50:
                    continue

                if min_distance(jd1, jd2) <= round(0.08 * max(len(jd1), len(jd2))) and \
                        min_distance(jr1, jr2) <= round(0.08 * max(len(jr1), len(jr2))):
                    info = f"当前公司: {company}\t{cur_month}月岗位索引: {idx1 + 2}\t岗位名: {row1['岗位']}\t" \
                           f"{pre_month}月相同岗位索引: {idx2 + 2}\t岗位名: {row2['岗位']}"
                    print(info)
                    logs_list.append(info)
                    df1_duplicate_index.append(idx1)
                    df2_duplicate_index.append(idx2)
                    merge_df_list.append(pd.concat([row1, row2], ignore_index=True))
                    break
        print(write_log(self.log_dst, logs_list, company, 'JD合并去重日志'))
        df_merge = pd.DataFrame(merge_df_list)
        cur_original_column_name, pre_original_column_name = df1.columns.values, df2.columns.values
        columns = self.column_name_process(cur_original_column_name, cur_month) + self.column_name_process(
            pre_original_column_name, pre_month)

        # 公司与地区字段修改
        df_merge.rename(columns={k: v for k, v in enumerate(columns)}, inplace=True)
        del df_merge[f'{pre_month}月公司']
        del df_merge[f'{pre_month}月地区']
        df_merge.rename(columns={f'{cur_month}公司': '公司', f'{cur_month}地区': '地区'}, inplace=True)
        # 增加两个月薪资处理部分
        salary_analysis = SalaryAnalysis(df_merge)
        for month in (cur_month, pre_month):
            min_sal, max_sal, mid_sal, struct_sal = salary_analysis.get_salary_info(f'{month}月薪资')
            df_merge[f'{month}月薪资'] = df_merge.pop(fr'{month}月薪资')
            df_merge[f'{month}月下限'] = min_sal
            df_merge[f'{month}月上限'] = max_sal
            df_merge[f'{month}月中位数'] = mid_sal
            df_merge[f'{month}月奖金'] = struct_sal

        df_merge['薪资下限变化'] = df_merge.apply(
            lambda x: (x[f'{cur_month}月下限'] - x[f'{pre_month}月下限']) / x[f'{pre_month}月下限'], axis=1)
        df_merge['薪资上限变化'] = df_merge.apply(
            lambda x: (x[f'{cur_month}月上限'] - x[f'{pre_month}月上限']) / x[f'{pre_month}月上限'], axis=1)
        df_merge['薪资中位数变化'] = df_merge.apply(
            lambda x: (x[f'{cur_month}月中位数'] - x[f'{pre_month}月中位数']) / x[f'{pre_month}月中位数'], axis=1)
        df_merge['奖金变化'] = df_merge.apply(lambda x: x[f'{cur_month}月奖金'] != x[f'{pre_month}月奖金'], axis=1)

        # 去除一个月JD薪资结构为日薪 另一个月JD薪资结构为月薪的情况
        df_merge = df_merge.query(f"not ((`{cur_month}月奖金` != '日薪' and `{pre_month}月奖金` == '日薪') "
                                  f"or (`{cur_month}月奖金` == '日薪' and `{pre_month}月奖金` != '日薪'))").copy()
        # 两个月份没有重复的岗位的表
        df1_remain = df1.append(df1.loc[df1_duplicate_index]).drop_duplicates(keep=False)  # 10月新增岗位
        df2_remain = df2.append(df2.loc[df2_duplicate_index]).drop_duplicates(keep=False)  # 10月删减岗位
        return df_merge, df2_remain, df1_remain


if __name__ == '__main__':
    demo = JDMerge(r'E:\job\11月内容\10月游戏岗位预处理分表', r'E:\job\11月内容\9月游戏岗位预处理分表',
                   r'E:\job\11月内容\实验', cur_month=10)
    demo.single_merge('4399')
