# 蒙特卡洛定投计算器

一个基于 `PySide6 + NumPy + Matplotlib` 的本地桌面应用，用蒙特卡洛模拟估算定投计划在不同收益波动和极端回撤情境下的资产区间。界面采用复古账本风格，适合本地试算、参数对比和结果演示。

## 功能概览

- 左侧输入核心参数，右侧展示关键指标与图表。
- 按月生成随机收益路径，可调预期年化收益率与年化波动率。
- 将黑天鹅事件建模为“整个投资期内最多触发一次”的极端回撤。
- 输出终值中位数、分位区间、本金亏损概率等结果。
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
- 极端回撤幅度：黑天鹅发生时的单次下跌比例。
- 极端回撤发生概率：整个投资期内至少出现一次极端回撤的概率。
- 年化波动率：位于“高级设置”中，用于控制月度路径波动。
- 模拟次数：位于“高级设置”中，默认 `5000`。

## 测试方式

运行单元测试：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

当前测试主要覆盖：

- 参数边界校验
- 无波动、无回撤时的确定性路径
- 极端回撤概率上下界
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

首个正式版资源文件名为：

- `MonteCarloSIPCalculator-v1.0.0-win64.zip`

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
