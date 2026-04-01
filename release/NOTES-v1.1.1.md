# MonteCarloSIPCalculator v1.1.1

V1.1.1 是一次界面体验修正版本，主要调整了左侧控制面板底部装饰图在“高级设置”展开时的布局表现。

本版本包含：

- 修复“高级设置”展开后左下角装饰图随布局下移的问题
- 将底部装饰区改为固定高度并保持底部锚定
- 进一步微调装饰图整体位置，使默认视图更自然
- 更新 smoke test，确保该布局行为稳定
- Windows x64 预编译发布包 `MonteCarloSIPCalculator-v1.1.1-win64.zip`

使用方式：

1. 下载 `MonteCarloSIPCalculator-v1.1.1-win64.zip`
2. 解压整个压缩包
3. 运行 `MonteCarloSIPCalculator\\MonteCarloSIPCalculator.exe`

说明：

- 本 Release 为目录型打包结果，`exe` 依赖同目录下的 `_internal/` 文件
- 普通使用场景下不需要额外安装 Python
