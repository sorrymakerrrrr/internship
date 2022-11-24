import pandas as pd
import re
from utils.PreProcessing import Preprocessing
from utils.MinDistance import min_distance
from utils.WriteLog import write_log

__all__ = ['ZhiPinProcessing']


class ZhiPinProcessing(Preprocessing):
    src = None
    log_dst = None

    def __new__(cls, src: str, log_dst: str, sheet_name=0, header=0, *args, **kwargs):
        cls.log_dst = log_dst
        return super().__new__(cls, src, sheet_name, header)

    def _company(self, column_name: str = '公司'):
        """
        清洗公司列数据
        :param column_name: 公司列的列名
        :return: 清洗完公司列的表
        """
        self.is_columns_exists(column_name)
        self.df[column_name] = self.df[column_name].str[: -2]

    def _title(self, column_name: str = '标题'):
        self.is_columns_exists(column_name)
        df = self.df
        df.rename(columns={column_name: '岗位'}, inplace=True)

    def _salary_exp_edu(self, column_name: str = '薪资 工作经验 学历要求'):
        """
        对表的'薪资 工作经验 学历要求'字段进行分割
        :param column_name: 表的列名
        :return: 划分完薪资、工作经验、学历要求并清洗完这些字段的表的表
        """
        self.is_columns_exists(column_name)
        df = self.df
        self.is_columns_exists(column_names=column_name)
        sal_exp_edu = df[column_name].str.split(r'\s+', expand=True)
        df['薪资'] = sal_exp_edu[0]
        df['工作经验'] = sal_exp_edu[1]
        self._exp()
        df['学历要求'] = sal_exp_edu[2] if len(sal_exp_edu.columns) >= 3 else sal_exp_edu[1]
        self._edu()
        del df[column_name]

    def _exp(self, column_name: str = '工作经验', column_check: str = "要求"):
        """
        清洗工作经验列, 增加更新工作经验列
        :param column_name: 工作经验字段列名
        :param column_check: 辅助提取更新工作经验字段的列名
        :return: 清洗工作经验列，增加更新工作经验列之后的表
        """
        self.is_columns_exists([column_name, column_check])
        df = self.df
        # 在所有行中搜索要求字段,如果在要求字段中出现工作经验要求,则更新
        year = r'(\d+[~-]|[一二两三四五六七八九十]到)?[\d一二两三四五六七八九十]{1,2}年'
        ch2num = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8',
                  '九': '9', '十': '10', '两': '2'}
        df[column_name] = df[column_name].str.strip().str.extract(r'(.*年|经验不限|在校|实习生)')

        def update_edu_(x):
            if re.search(year, str(x[column_check])) is not None:
                res = re.search(year, str(x[column_check])).group()
                # 更新工作经验字段年限变为数字形式
                res = ''.join([ch2num[i] if i in ch2num.keys() else i for i in res])[: -1]
                return res
            else:
                return None

        update_edu = df.loc[:, [column_name, column_check]].apply(lambda x: update_edu_(x), axis=1)
        for i in range(len(update_edu)):
            update = update_edu[i]
            if update is not None:
                cnt = re.split(r'(-|~|到|--)', update)
                if int(cnt[0]) == 1:
                    update_edu[i] = '1年'
                elif int(cnt[0]) == 2:
                    update_edu[i] = '1-3年'
                elif 3 <= int(cnt[0]) < 5:
                    update_edu[i] = '3-5年'
                elif 5 <= int(cnt[0]) < 10:
                    update_edu[i] = '5-10年'
                else:
                    update_edu[i] = '10年'
        df[f'更新{column_name}'] = update_edu
        df.query(f"`{column_name}` in ('1年', '1-3年', '3-5年', '5-10年', '10年', '经验不限', '在校', '实习生') or "
                 f"`更新{column_name}` in ('1年', '1-3年', '3-5年', '5-10年', '10年')", inplace=True)
        df[column_name].replace('在校', '实习生', inplace=True)
        df.reset_index(inplace=True)
        del df['index']

    def _edu(self, column_name: str = '学历要求'):
        """
        提取学历要求
        :param column_name: 学历字段列名
        :return: 清洗学历要求列的表
        """
        self.is_columns_exists(column_name)
        df = self.df
        df[column_name] = df[column_name].str.strip().str.extract(
            r'(中专|高中|中技|大专|本科|学历不限|应届本科|硕士|博士)')
        pass

    def _location(self, column_name: str = '地区'):
        """
        处理地区字段 将外面括号删除
        :param column_name: 地区字段列名
        :return: 清理地区列的表
        """
        self.is_columns_exists(column_name)
        df = self.df
        df[column_name] = df[column_name].str.strip(r'[]')

    def _requirement(self, column_name: str = '要求'):
        """
        清洗要求字段的表
        :param column_name: 要求字段表的列名
        :return: 得到更新职位描述与任职要求的表
        """
        self.is_columns_exists(column_name)
        df = self.df
        jd = df[column_name].str.split(
            r'[^以下|关键)](任职要求|任职资格|岗位要求|职位要求|任职需求|任职条件|工作要求|能力要求|经验及资格|技能需求|岗位需求|职责要求|必备条件|Requirement|技能要求|职位需求)',
            expand=True)  # 分割

        def adjust_format_(x):
            if x is not None:
                return str(x).strip(r'\s:：」]').replace(' ', '').replace("，", ",").replace("。", "."). \
                    replace("；", ";").replace("、", " ").replace("：", ":").replace("【", "[").replace("】", "]")

        # 对字段做去除空格等处理
        jd[0] = jd[0].apply(lambda x: adjust_format_(x))
        jd[2] = jd[2].apply(lambda x: adjust_format_(x))
        # 加入职位描述与任职要求字段
        df['职位描述'] = jd[0]
        df['任职要求'] = jd[2]

    def _add_post_classifier(self, column_name: str = '岗位', loc: int = 2):
        df = self.df
        posts = self._clean_post_type(df, column_name)
        df.insert(loc=loc, column='岗位类型', value=posts)

    @staticmethod
    def _get_post_type() -> dict:
        """
        给出各个类别分类依据
        :return: 包含标签分类依据的字典
        """
        tech = r'.*((?<!测试)工程师|主程|程序|开发|技术|[^A-Za-z]*TA[^A-Za-z]*|技术美术|引擎|前端|后端|后台|服务端|客户端|服务器|CTO' \
               r'|研发|c\+\+|java|算法|U3D)+.*'
        sche = r'.*((?<!市场|营销|运营|创意|推广|技术|交互)策划|制作人|编剧|剧情|世界观|关卡|数值|文案|主策|主笔)+.*'
        art = r'.*((?<!技术)美术|(?<!交互)设计|模型|原画|场景|角色|动效|特效|动画|分镜|导演|地编|[^A-Za-z]*UI[^A-Za-z]*|界面|视频|' \
              r'平面|美宣|主美|灯光|编导|动作|绑定|分境)+.*'
        issue = r'.*(运营|营销|客服|媒介|广告|投放|UA|用户研究|市场|数据分析|本地化|制片|品牌|(?<=市场|营销|创意|推广)策划|Marketing|' \
                r'剪辑|发行|COO|质检|代投|活动)+.*'
        test = r'.*(测试|qa)+.*'
        ue = r'.*(交互设计|UE[^4].*|用户体验|交互)+.*'
        return {'技术类': tech, '策划类': sche, '美术类': art, '发行类': issue, '测试类': test, 'UE类': ue}

    @classmethod
    def _set_post_type(cls, df: pd.DataFrame, column_name: str) -> list:  # 设置每一行的岗位类型
        posts = []
        types = {k: re.compile(v, re.I) for k, v in cls._get_post_type().items()}  # 预编译 不区分表达式中大小写
        for job in df[column_name]:
            # 岗位字段去除括号里内容 例: 技术美术（渲染向）-> 技术美术
            job = re.sub(r'（.*?）|\(.*?\)', '', str(job))
            post = []
            for k, v in types.items():
                if re.match(v, job) is not None:  # 粗略匹配 将可以匹配到的所有岗位都加入
                    post.append(k)
            if len(post) == 0:
                post.append('其他')
            posts.append(post)
        return posts

    @classmethod
    def _clean_post_type(cls, df: pd.DataFrame, column_name: str, column_check: str = '要求'):
        """
        清洗标签
        一行中有一个以上标签,则在职位描述列寻找对应标签出现的次数,将标签确定为出现次数最多的标签
        一行中有一个标签,则最后标签就是该标签
        一行中没有标签,则设置为其他
        :param cls: 本类实例
        :param column_name: 岗位所在列的名称
        :param column_check: 要求所在列的名称, 用于二次筛查岗位类型
        :return: 返回岗位的一个列表
        """
        cls.is_columns_exists([column_name, column_check])
        requirement = df[column_check]
        posts = cls._set_post_type(df, column_name)
        types = cls._get_post_type()

        for i in range(len(posts)):
            if len(posts[i]) > 1:
                tmp = []
                for j in posts[i]:
                    count = len(re.findall(types[j][3: -4], str(requirement[i])))
                    tmp.append((j, count))
                tmp.sort(key=lambda x: x[-1], reverse=True)
                posts[i] = tmp[0][0]
            else:
                posts[i] = posts[i][0]
        return posts

    def _screen_game_job(self):
        """
        筛选出游戏岗位
        :return: 返回筛选游戏岗位后的表
        """
        df = self.df
        self.is_columns_exists(['岗位类型'])

        df_game_job = df.query("`岗位类型` in ['策划类', '美术类', 'UE类']").copy()
        df2screen = df.query("`岗位类型` in ['测试类', '发行类', '技术类', '其他']").copy()

        def is_game(s: str):
            return '游戏' in s

        self.is_columns_exists(['岗位', '要求'])
        df2screen['is_game'] = df2screen.loc[:, ['岗位', '要求']] \
            .apply(lambda x: is_game(str(x['岗位'])) or is_game(str(x['要求'])), axis=1)
        df2screen = df2screen.query("is_game")
        df = pd.concat([df_game_job, df2screen])
        df.reset_index(inplace=True)
        del df['index']
        del df['is_game']
        self.df = df

    def _drop_duplicates(self, threshold: int = 0.08, column_company: str = '公司', column_salary: str = '薪资',
                         column_jd: str = '职位描述', column_jr: str = '任职要求', log_name: str = '岗位去重'):
        """
        按照薪资相等, 职位描述与任职要求近似相等给岗位去重
        :param threshold 去重的阈值
        :param column_company 公司名所在列
        :param column_salary 薪资所在列
        :param column_jd 职位描述所在列
        :param column_jr 任职要求所在列
        :return: 去完重之后的表
        """
        df = self.df
        self.is_columns_exists([column_company, column_salary, column_jd, column_jr])
        company = df.loc[0, column_company]
        idx = []
        logs_list = []
        # s存放重复行的index
        s = set()
        for idx1, row1 in df.iterrows():
            # 遇到重复岗位时跳过
            if idx1 in s:
                s1 = f'当前公司:{company}  第{str(idx1 + 2)}行是已经发现的重复岗位, 跳过本行搜索!'
                print(s1)
                logs_list.append(s1)
                continue
            for idx2, row2 in df.iterrows():
                # 已经遍历过的行跳过
                if idx2 <= idx1:
                    continue
                salary1, salary2 = str(row1[column_salary]), str(row2[column_salary])
                jd1, jd2 = str(row1[column_jd]), str(row2[column_jd])
                jr1, jr2 = str(row1[column_jr]), str(row2[column_jr])
                # 薪资不一样或者字符串长度相差过大的岗位跳过
                if salary1 != salary2 or abs(len(jd1) - len(jd2)) >= 50 or abs(len(jr1) - len(jr2)) >= 50:
                    continue
                # 判定岗位是否重复
                if min_distance(jd1, jd2) <= round(threshold * max(len(jd1), len(jd2))) and \
                        min_distance(jr1, jr2) <= round(threshold * max(len(jr1), len(jr2))):
                    s2 = f'当前公司:{company}  第{idx1 + 2}行与第{idx2 + 2}行重复!'
                    print(s2)
                    logs_list.append(s2)
                    s.add(idx2)
            print(f'当前公司:{company}  第{idx1 + 2}行遍历完成!')
            idx.append(idx1)
        df = df.loc[idx, :].reset_index()
        del df['index']
        self.df = df
        # 将去重信息写入日志中
        log_dst = self.log_dst
        print(write_log(log_dst, logs_list=logs_list, company=company, log_name=log_name))

    def clean_table(self) -> pd.DataFrame:
        """
        对表做所有清洗操作
        :return: 清洗之后的表
        """
        print('开始预处理!')
        steps = [self._company(), self._title(), self._salary_exp_edu(), self._location(), self._requirement(),
                 self._add_post_classifier(), self._screen_game_job(), self._drop_duplicates()]
        for step in steps:
            _ = step

        return self.df


if __name__ == '__main__':
    test = ZhiPinProcessing(src=r'E:\job\10月内容\10月岗位原始数据\网易-20221026.xlsx', log_dst=r'E:\job\11月内容\实验')
    test.set_src(r'E:\job\10月内容\10月岗位原始数据\4399-20221026.xlsx', sheet_name=0, header=0)
