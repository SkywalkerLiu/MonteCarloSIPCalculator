# 字体说明

界面会优先从本目录加载字体文件。

当前默认字体组合：

- 中文正文与图表：`NotoSerifCJKsc-Regular.otf`
- 中文强调：`NotoSerifCJKsc-SemiBold.otf`
- 英文装饰：`CormorantGaramond-Regular.ttf`
- 英文装饰强调：`CormorantGaramond-SemiBold.ttf`

加载顺序会优先选择 `Source Han Serif SC / Noto Serif CJK SC` 作为中文主字体，再选择 `Cormorant Garamond` 作为英文花体和装饰字体；如果这些文件缺失，程序会回退到 `Microsoft YaHei`。
