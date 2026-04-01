# 蒙特卡洛定投计算器

一个基于 `PySide6 + NumPy + Matplotlib` 的本地桌面应用，用蒙特卡洛模拟估算定投计划在不同收益波动和极端事件情境下的资产区间。界面采用复古账本风格，适合本地试算、参数对比和结果演示。

## 功能概览

- 左侧输入核心参数，右侧展示关键指标与图表。
- 按月生成随机收益路径，可调预期年化收益率与年化波动率。
- 将极端事件建模为“平均每多少年发生 1 次”的频率模型，并按月离散采样。
- 同一路径内允许多次极端事件，投资期内会自然出现 `0 / 1 / 2 / 3+` 次事件分布。
- 输出终值中位数、分位区间、本金亏损概率与极端事件覆盖摘要。
- 提供样本路径图、路径扇形图和终值直方图三类可视化。

## 目录结构

```text
Calculator/
|-- main.py
|-- requirements.txt
|-- app/
|   |-- bootstrap.py
|   |-- resources.py
|   |-- core/
|   `-- ui/
|-- assets/
|   |-- backdrops/
|   |-- icons/
|   `-- fonts/
`-- tests/
```

## 环境要求

- Windows PowerShell
- Python 3.14 x64
- 建议使用项目内虚拟环境 `.venv`

## 安装依赖

如果项目还没有虚拟环境，先创建一个：

```powershell
python -m venv .venv
```

安装依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` 当前包含：

- `numpy`
- `matplotlib`
- `PySide6`

## 运行方式

推荐使用项目内虚拟环境启动：

```powershell
.\.venv\Scripts\python.exe main.py
```

如果项目目录中已经有可用的 `.venv`，也可以直接使用：

```powershell
py .\main.py
```

此时入口会自动优先加载项目本地虚拟环境中的依赖。

程序启动后可填写以下主要参数：

- 目前持仓：当前持仓市值，作为 `t=0` 初始本金。
- 每月定投额：默认按月末投入。
- 预期年化收益率：用于校准长期收益水平。
- 投资期限：以年为单位。
- 极端回撤幅度：极端事件发生时的单次下跌比例。
- 极端情况平均每多少年发生 1 次：用于定义极端事件发生频率，程序会将其换算为月度触发概率；投资期内可自然出现多次事件。
- 年化波动率：位于“高级设置”中，用于控制月度路径波动。
- 模拟次数：位于“高级设置”中，默认 `5000`。

结果页会额外展示极端事件覆盖摘要，包括：

- 投资期内至少发生 `1` 次极端事件的实际触发率
- 单条路径的平均触发次数
- `0 次 / 1 次 / 2 次 / 3 次及以上` 事件占比

## 测试方式

运行单元测试：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

当前测试主要覆盖：

- 参数边界校验
- 无波动、零回撤时的确定性路径
- 超长极端事件间隔下的低触发率
- 高频极端事件配置下的多次触发
- `0 / 1 / 2 / 3+` 事件占比与至少一次触发率的一致性
- 分位数结果的单调性
- 货币格式化输出

## 打包 Windows 可执行文件

如果需要重新生成 Windows 发布包，可在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\pyinstaller.exe --noconfirm calculator.spec
```

打包完成后会生成目录型产物：

```text
dist/
`-- MonteCarloSIPCalculator/
    |-- MonteCarloSIPCalculator.exe
    `-- _internal/
```

请不要只复制单独的 `MonteCarloSIPCalculator.exe`，运行时还依赖同目录下的 `_internal/` 资源和动态库。对外分发时应打包整个 `dist/MonteCarloSIPCalculator/` 目录，例如压缩为 zip 后再提供下载。

## 下载 Release

项目会提供预编译的 Windows x64 版本 Release，下载地址：

[`https://github.com/SkywalkerLiu/MonteCarloSIPCalculator/releases`](https://github.com/SkywalkerLiu/MonteCarloSIPCalculator/releases)

当前正式版资源文件名为：

- `MonteCarloSIPCalculator-v1.1.1-win64.zip`

下载后解压，直接运行：

```text
MonteCarloSIPCalculator\MonteCarloSIPCalculator.exe
```

该 Release 为自带依赖的桌面程序，普通使用场景下不需要额外安装 Python。

## 开发说明

- 入口文件是 `main.py`。
- 核心模拟逻辑位于 `app/core/`。
- 界面、主题和图表位于 `app/ui/`。
- 字体和背景素材位于 `assets/`。
