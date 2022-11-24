import pandas as pd
import re


class SalaryAnalysis:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.pat1 = r'([0-9]+)-([0-9]+)K?·?([0-9]+薪)?'
        self.pat2 = r'([0-9]+)-([0-9]+).*天$'

    def get_salary_info(self, salary_column: str) -> tuple:
        """
        得到薪资情况 最高薪资 最低薪资 薪资结构
        :param salary_column: 薪资所在列
        :return: 最低薪资水平列表 最高薪资水平列表 薪资结构列表
        """
        min_salary = []
        max_salary = []
        medium_salary = []
        salary_struct = []

        for s in self.data[salary_column]:
            if re.match(self.pat2, str(s)) is not None:
                m = re.match(self.pat2, str(s)).groups()
                salary_struct.append('日薪')
            else:
                m = re.match(self.pat1, str(s)).groups()
                salary_struct.append(m[2] if m[2] is not None else '12薪')

            min_salary.append(int(m[0]))
            max_salary.append(int(m[1]))
            medium_salary.append(1 / 2 * (int(m[0]) + int(m[1])))

        return min_salary, max_salary, medium_salary, salary_struct


if __name__ == '__main__':
    pass
