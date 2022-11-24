# doc
### 结构
```
├─jd_analysis_summary
|   ├─__init__.py
|   ├─JDAnalysisSummarySave.py
|   ├─JDSummary.py
|   ├─Main.py
|
├─jd_monitoring
|   ├─__init__.py
|   ├─JDMonitorSave.py
|   ├─JDTableMerge.py
|   ├─Main.py
|   ├─SalaryChangeAnalysis.py
|
├─processing
|   ├─__init__.py
|   ├─Main.py
|   ├─ZhiPinProcess.py
|   ├─ZhiPinSave.py
|
├─utils
|   ├─__init__.py
|   ├─ColumnExist.py
|   ├─MinDistance.py
|   ├─PreProcessing.py
|   ├─Save.py
|   ├─WriteLog.py
|
├─__init__.py
|
├─Main.py
|
├─README.md
```
--------------------------
### utils　　工具类
- **ColumnExist.py**　　判断在一张DataFarme中，指定列是否存在
- **MinDistance.py**　　计算两个字符串之间的最小编辑距离
- **PreProcessing.py**　　给出岗位数据预处理的范式，作为具体的不同网站爬取的岗位数据预处理类的父类
- **Save.py**　　给出保存表的范式，作为具体保存类的父类，保存分为单表保存与不同表合并之后再保存
- **WriteLog.py**　　写日志  

### processing　　Boss直聘上爬取文件的预处理过程
- **ZhiPinProcess.py**　　从Boss直聘上爬取的表的预处理类，继承自utils.PreProcessing中的Preprocessing类
- **ZhiPinSave.py**　　从Boss直聘上爬取的表执行完预处理之后执行保存的类，继承自utils.Save中的FSave类
- **Main.py**　　Boss直聘上爬取的岗位表的预处理主程序，执行完程序后会生成多个分表和一个总表

### jd_monitoring　　预处理完之后，JD监控表生成
- **SalaryChangeAnalysis.py**　　生成岗位薪资统计
- **JDTableMerge.py**　　为生成当前月份的岗位表与前一月份的岗位表的相同岗位、当月删减岗位、当月新增岗位的表所创建的类
- **JDMonitorSave.py**　　对表进行保存，从而生成JD监控表的类，继承自utils.Save中的FSave类
- **Main.py**　　JD监控表生成的主程序，执行完程序后会生成多个JD监控分表和一个JD监控总表

### jd_analysis_summary　　分析汇总表生成
- **JDSummary.py**　　分析汇总表生成执行的内容
- **JDAnalysisSummarySave.py**　　分析汇总表保存
- **Main.py**　　分析汇总表生成的主程序，执行完主程序后会生成一张Excel表，表内保存了所有的分析汇总的sheet（目前为8个）

### Main.py
执行以上所有内容的主程序入口，给定存放当前月份与之前月份的岗位原始数据表的目录、输出文件存放的根目录与当前的月份，即可执行
