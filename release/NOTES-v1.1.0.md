# MonteCarloSIPCalculator v1.1.0

V1.1.0 将极端事件模型从“整个投资期内最多一次”升级为“平均每多少年发生 1 次”的频率模型，让投资期内的 `0 / 1 / 2 / 3+` 次极端事件都能自然出现在模拟结果中。

本版本包含：

- 极端事件频率化输入：按“平均每多少年发生 1 次”配置风险强度
- 同一路径支持多次极端事件叠加，不再限制为单次黑天鹅
- 结果页新增极端事件覆盖摘要，展示平均触发次数与 `0 / 1 / 2 / 3+` 次分布
- README、测试与 Windows 打包说明同步更新
- Windows x64 预编译发布包 `MonteCarloSIPCalculator-v1.1.0-win64.zip`

使用方式：

1. 下载 `MonteCarloSIPCalculator-v1.1.0-win64.zip`
2. 解压整个压缩包
3. 运行 `MonteCarloSIPCalculator\\MonteCarloSIPCalculator.exe`

说明：

- 本 Release 为目录型打包结果，`exe` 依赖同目录下的 `_internal/` 文件
- 普通使用场景下不需要额外安装 Python
