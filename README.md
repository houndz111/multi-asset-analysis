# Multi-Asset Risk and Return Analysis

## 项目简介

本项目使用 Python 比较多类资产的历史风险收益特征，作为量化投资学习的第一个完整项目。

## 研究问题

- 不同资产的累计收益和年化收益有何差异？
- 不同资产的波动率和最大回撤有何差异？
- 不同资产之间的相关性如何？
- 多资产配置是否具有分散风险的潜力？

## 计划使用的指标

- 日收益率
- 累计净值
- 年化收益率
- 年化波动率
- 夏普比率
- 最大回撤
- 相关系数

## 研究范围

本项目使用以下 ETF 作为不同资产类别和市场的可交易代理：

| 代码   | 名称       | 代表资产或市场 |
| ------ | ---------- | -------------- |
| 510300 | 沪深300ETF | A股大盘权益    |
| 511010 | 国债ETF    | 中国国债       |
| 518880 | 黄金ETF    | 黄金           |
| 513100 | 纳指ETF    | 美国权益       |
| 159920 | 恒生ETF    | 港股权益       |

- 目标样本区间：2015-01-01 至 2025-12-31
- 数据频率：日频
- 数据来源：东方财富，通过 AkShare 获取
- 价格口径：前复权收盘价

不同 ETF 的上市时间和有效交易日期可能不同，实际共同样本区间将在数据检查后确定。

## 数据说明

本项目通过 AkShare 获取东方财富 ETF 日频行情，并使用前复权收盘价。

为减少重复访问数据接口，项目将成功获取的数据保存到本地 `data/raw/` 目录。
后续分析优先读取本地缓存。

不同 ETF 的交易日期可能不同，因此绩效比较使用五只 ETF 同时具有有效价格的共同样本。

## 实际样本

- 共同样本开始日期：2015-01-05
- 共同样本结束日期：2025-12-31
- 共同样本交易日数量：2673
- 纳指ETF存在一个缺失交易日，已在共同样本筛选时排除

## 运行方式

### 1. 获取项目

在 PowerShell 中执行：

```powershell
git clone https://github.com/houndz111/multi-asset-analysis
```

进入项目目录：
```
cd multi-asset-analysis
```

也可以直接在 GitHub 页面点击 Code，选择 Download ZIP 下载项目。

### 2. 创建 Conda 环境
本项目使用 Python 3.11。

如果本地尚未创建 quant 环境，执行：
```
conda create -n quant python=3.11
```
激活环境：
```
conda activate quant
```
安装项目依赖：
```
python -m pip install -r requirements.txt
```
项目主要依赖包括：

- pandas：数据处理和时间序列分析
- numpy：数值计算和向量化运算
- matplotlib：绘制分析图表
- akshare：获取 ETF 历史行情数据

如果本地已经存在 quant 环境，不需要重复创建环境，直接执行：
```
conda activate quant
python -m pip install -r requirements.txt
```
### 3. 在 VS Code 中选择 Python 环境
使用 VS Code 打开项目根目录：
```
multi-asset-analysis/
```
按下：
```
Ctrl + Shift + P
```
搜索并选择：
```
Python: Select Interpreter
```
选择 Python 3.11 对应的 quant 环境。

在 Windows 中，解释器路径通常类似：
```
C:\Users\你的用户名\miniconda3\envs\quant\python.exe
```
### 4. 打开并运行 Notebook
打开项目中的：
```
analysis.ipynb
```
点击 Notebook 右上角的内核选择按钮，选择：
```
quant
```
然后按照从上到下的顺序运行代码单元格。

可以使用以下快捷键运行当前单元格并进入下一个单元格：
```
Shift + Enter
```
### 5. 数据获取与本地缓存
项目使用 AkShare 获取以下 ETF 的日频前复权行情：

- 沪深300ETF
- 国债ETF
- 黄金ETF
- 纳指ETF
- 恒生ETF

第一次运行时，程序会从数据接口获取数据，并将原始数据保存到：
```
data/raw/
```
后续运行时，程序会优先读取本地缓存，避免重复请求数据接口。

由于 data/raw/ 已加入 .gitignore，原始行情 CSV 不会上传到 GitHub。首次运行时，如果本地没有缓存文件，需要确保网络可以访问 AkShare 数据接口。

### 6. 输出结果
运行完成后，分析结果会保存到：
```
outputs/
```
主要输出文件包括：

- performance.csv：各 ETF 的收益和风险指标
- correlation.csv：日收益率相关系数矩阵
- drawdown_summary.csv：最大回撤及发生日期
- cumulative_wealth.png：累计净值曲线
- drawdown.png：回撤曲线
- correlation_heatmap.png：相关系数热力图
  
## 主要研究发现

基于 2015-01-05 至 2025-12-31 的共同样本：

- 纳指 ETF 的累计收益率和复合年化收益率最高，分别为约 597.44% 和 20.10%。
- 黄金 ETF 的累计收益率约为 285.29%，复合年化收益率约为 13.57%。
- 沪深300 ETF 的年化波动率最高，约为 26.86%。
- 国债 ETF 的年化波动率最低，约为 2.44%，最大回撤约为 -5.09%。
- 国债 ETF 的夏普比率最高，约为 1.33；黄金 ETF 次之，约为 1.01。
- 沪深300 ETF 的最大回撤最严重，约为 -52.97%，发生于 2016-01-28。
- 恒生 ETF 的最大回撤约为 -47.31%，发生于 2022-10-28。
- 沪深300 ETF 与恒生 ETF 的日收益率相关系数最高，约为 0.61。
- 黄金 ETF 与其他风险资产的相关性整体较低，可能具有一定的分散化潜力。
- 沪深300 ETF 与国债 ETF 的日收益率相关系数约为 -0.14，显示样本期内二者存在一定反向变动特征。

## 输出文件

- `outputs/performance.csv`：各 ETF 的绩效指标
- `outputs/correlation.csv`：日收益率相关系数矩阵
- `outputs/drawdown_summary.csv`：最大回撤及发生日期
- `outputs/cumulative_wealth.png`：累计净值曲线
- `outputs/drawdown.png`：回撤曲线
- `outputs/correlation_heatmap.png`：相关系数热力图

## 研究限制

- ETF 只是对应资产类别的可交易代理，不能完全代表整个资产类别。
- 结果基于前复权收盘价，实际收益还可能受到交易费用、税费、滑点和买卖价差影响。
- 不同 ETF 的交易时间、节假日和流动性存在差异。
- 共同样本筛选能够提高横向可比性，但会删除无法同时获得全部资产价格的日期。
- 夏普比率假设日无风险收益率为 0，未扣除现金收益。
- 历史表现和相关性不代表未来表现。
- 本项目是描述性历史分析，不构成投资建议。

## 当前进度

- [x] 创建项目结构
- [x] 获取并检查数据
- [x] 计算绩效指标
- [x] 绘制图表
- [x] 分析研究结果
- [x] 整理项目文档