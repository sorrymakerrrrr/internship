import numpy as np
import pandas as pd
import re
from typing import List
from utils.ColumnExist import is_columns_exists

__all__ = ['SalarySummary']


class SalarySummary:

    def __init__(self, src: str, cur_month: int):
        """
        初始化薪资监控类
        :param src: JD监控总表所在的路径
        :param cur_month: JD监控当前月份
        """
        self.src = src
        self.cur_month = cur_month
        # company_std、post_std、exp_std 分别是 公司标准化名字、职位标准化名字、经验标准化名字
        self.company_std = (
            '百田', '深蓝互动', '祖龙娱乐', '冰川网络', '吉比特', '心动网络', '库洛', '完美世界', '中手游',
            '4399', '三七互娱', '字节跳动', '米哈游', '腾讯', '网易', '莉莉丝', 'FunPlus', '总计')
        self.post_std = ('策划类', '技术类', '美术类', 'UE类', '测试类', '发行类', '其他', '总计')
        self.exp_std = ('经验不限', '1年', '1-3年', '3-5年', '5-10年', '10年', '实习生', '总计')

    @property
    def sheet_names(self):
        """
        :return: JD监控表的所有表的sheet_name
        """
        keywords = ['变化', '减', '增']
        all_sheets = pd.ExcelFile(self.src).sheet_names
        sheet_names = []
        for sheet_name in all_sheets:
            for word in keywords:
                pat = re.compile(word, re.I)
                if re.search(pat, sheet_name) is not None:
                    sheet_names.append(sheet_name)
                    break
        if len(sheet_names) < 3:
            raise ValueError(
                f"should have 3 sheets in {all_sheets} include '变化'、'减'、'增', please rename sheet first！")
        return sheet_names

    @staticmethod
    def get_exp(df: pd.DataFrame, cur_month: int):
        """
        工作经验列进行更新
        :param df: JD监控总表
        :param cur_month: JD监控月份
        :return: 工作经验列更新后的值
        """
        if cur_month is None:
            update_exp, exp = '更新工作经验', '工作经验'
        else:
            update_exp, exp = f'{cur_month}月更新工作经验', f'{cur_month}月工作经验'

        if not pd.isna(df[update_exp]):
            df[exp] = df[update_exp]

        return df[exp] if not pd.isna(df[exp]) else '经验不限'

    def get_dataframe(self, sheet_name: str, cur_month: int = None, header: int = 0):
        """
        得到pd.DataFrame表
        :param sheet_name: 需要读取表的表名
        :param cur_month: JD监测当前月份
        :param header: 表开始读取的行
        :return: 更新了工作经验列之后的表
        """
        df = pd.read_excel(self.src, sheet_name=sheet_name, header=header)
        if cur_month is not None:
            column_name = f'{cur_month}月工作经验'
        else:
            column_name = '工作经验'
        is_columns_exists(df, column_name)
        df[column_name] = df.apply(lambda x: self.get_exp(x, cur_month), axis=1)
        return df

    def summary(self, sheet_name: str, header: int, row: str, cur_month: int = None,
                sum_info: str = '薪资变化岗位个数'):
        """
        统计行为 (公司 / 工作经验),列岗位类型的二位联列表 参考腾讯文档 - 202209-10游戏公司JD监测 - 202210分析汇总表
        :param sheet_name: JD监控表当前需要整合分析的sheet_name
        :param header: 表开始读取的行
        :param row: 需要整合的行: 公司 / 工作经验
        :param cur_month: 当前月份
        :param sum_info:表统计内容: 薪资变化幅度 / 薪资变化岗位个数
        :return: 整合完的summary表
        """
        assert sum_info in ('薪资变化幅度', '薪资变化岗位个数')
        assert row in ('公司', '工作经验')
        row = f'{cur_month}月{row}' if cur_month is not None else row
        by = [row, f'{cur_month}月岗位类型' if cur_month is not None else '岗位类型']
        df = self.get_dataframe(sheet_name, cur_month, header)
        if cur_month is not None:
            ans = self._salary_change_summary(df, by) if sum_info == '薪资变化幅度' \
                else self._salary_count_summary(df, by)
            print(f'{sheet_name}表(按{row}){sum_info}统计完成')
            return ans
        else:
            if sum_info == '薪资变化幅度':
                raise TypeError('月份增减岗位数据没有薪资变化幅度对比!')
            else:
                ans = self._salary_count_summary(df, by)
                print(f'{sheet_name}表(按{row}){sum_info}统计完成')
                return ans

    def _salary_change_summary(self, df: pd.DataFrame, by: List[str]):
        """
        得到薪资变化幅度总计
        :param df: 需要汇总的表
        :param by: 根据 ['公司', '薪资变化幅度'] 或 ['工作经验', '薪资变化幅度'] 或 ['X月工作经验', '薪资变化幅度']字段统计薪资变化幅度
        :return: 薪资变化幅度汇总表
        """
        is_columns_exists(df, ['薪资上限变化', '薪资下限变化', '薪资中位数变化'])

        def salary_change_info(x: pd.DataFrame):
            # 统计薪资幅度变化
            num = round(1 / 3 * (x['薪资上限变化'].mean() + x['薪资下限变化'].mean() + x['薪资中位数变化'].mean()), 5)
            return num

        stack_salary_change = df.groupby(by).apply(lambda x: salary_change_info(x))
        salary_change = stack_salary_change.unstack()

        # 不同岗位类型薪资变化幅度总计
        total4post = df.groupby(by[1]).apply(lambda x: salary_change_info(x))
        # 不同公司 或 不同工作经验薪资变化幅度总计
        total4other = df.groupby(by[0]).apply(lambda x: salary_change_info(x))
        # 所有公司 或所有工作经验 与所有岗位的薪资变化幅度总计
        total_change = round(
            1 / 3 * (df['薪资上限变化'].mean() + df['薪资下限变化'].mean() + df['薪资中位数变化'].mean()), 5)

        return self.data2table(salary_change, total4post, total4other, total_change, by)

    def _salary_count_summary(self, df: pd.DataFrame, by: List[str]):
        """
        得到薪资岗位变化数量总计
        :param df: 需要汇总的表
        :param by: 根据 ['公司', '薪资变化幅度'] 或 ['工作经验', '薪资变化幅度'] 或 ['X月工作经验', '薪资变化幅度']字段统计薪资变化幅度
        :return: 薪资岗位变化数量汇总表
        """
        is_columns_exists(df, by)
        column_name = df.columns.values[1]
        stack_salary_change_count = df.groupby(by).count()[column_name]

        salary_change_count = stack_salary_change_count.unstack()
        total4post = df.groupby(by[1]).count()[column_name]
        total4other = df.groupby(by[0]).count()[column_name]
        total_change = df.count()[column_name]
        return self.data2table(salary_change_count, total4post, total4other, total_change, by)

    def data2table(self, basic_data: pd.DataFrame, total4post: pd.Series, total4other: pd.Series,
                   total_change: pd.Series, by: List[str]) -> pd.DataFrame:
        """
        将计算得到的联列表增加行与列的总计与所有数据的总计
        :param basic_data: 不包含行与列的总计的表
        :param total4post: 在最后一行增加对岗位类型的总计
        :param total4other: 在最后一列增加对 公司/工作经验 的总计
        :param total_change: 由最后一行最后一列所定位的数据框增加所有薪资变化岗位的 薪资变化幅度/薪资变化岗位数量 的总计
        :param by: 根据 ['公司', '薪资变化幅度'] 或 ['工作经验', '薪资变化幅度'] 或 ['X月工作经验', '薪资变化幅度']字段统计薪资变化幅度
        :return: 最后的总表
        """
        basic_data.loc[:, '总计'] = total4other
        basic_data.loc['总计'] = total4post
        basic_data.loc['总计', '总计'] = total_change

        # 修改成标准化的名字
        if by[0] in ('公司', f'{self.cur_month}月公司'):
            fields = self.company_std
        elif by[0] in ('工作经验', f'{self.cur_month}月工作经验'):
            fields = self.exp_std
        else:
            raise KeyError(f'{by} is not in 公司 or 工作经验 or {self.cur_month}月工作经验')

        basic_data.rename(self._transfer(fields, basic_data.index.values), inplace=True)
        basic_data.rename(columns=self._transfer(self.post_std, basic_data.columns.values), inplace=True)

        ans = pd.DataFrame(basic_data, index=fields, columns=self.post_std)
        ans.fillna(0.00000, inplace=True)
        return ans

    @staticmethod
    def _transfer(fields: tuple, names4transfer: np.ndarray) -> dict:
        """
        汇总表中的名字标准化
        :param fields: 标准化名字集合
        :param names4transfer: 需要标准化的索引或列
        :return: {非标准化名字: 标准化名字}
        """
        renames = {}
        for name in names4transfer:
            for k in fields:
                pat = re.compile(k, re.I)
                if re.search(pat, name) is not None:
                    renames[name] = k
                    break
            else:
                raise ValueError(f"not find the standard name of {name}, please check!")
        return renames


if __name__ == '__main__':
    sum_ = SalarySummary(r'E:\job\11月内容\9,10月份jd对比总表\9,10月相同岗位薪资对比-20221110.xlsx', cur_month=10)
    # print(sum_.sheet_names[2])
    # print(sum_.summary(sum_.sheet_names[2], 1, row='公司', cur_month=None, sum_info='薪资变化岗位个数'))
    print(sum_.sheet_names)
