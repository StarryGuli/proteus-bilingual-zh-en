# 第三方内容与来源

本仓库中的语言文件不是从零原创的，下面列出各部分的来源。

| 内容 | 位置 | 来源 | 许可 |
|---|---|---|---|
| Proteus 界面英文原文 | `release/Translations/proteus_*.qm` 的查找键与英文半句 | Labcenter Electronics, Proteus 8 Professional | 版权归 Labcenter 所有。本仓库不授予任何权利 |
| 原中文翻译 | 同上，中文半句 | 一个流传的 Proteus 8.17 汉化语言包（由使用者提供，作者与许可未知） | 未知，**未获得再分发授权** |
| 补充的编辑器、菜单、对话框中文 | `tools/qscintilla_zh.py`、`tools/new_labels_zh.py`、`data/new-labels-to-translate.json` 及 `.qm` 中新增部分 | 本仓库作者补译 | 随 MIT（脚本部分） |
| Qt 4.8 官方简体中文翻译 | `release/Translations/qt_*.qm`、`data/official-qt4-zh_CN.ts` | Qt Project，<https://github.com/qt/qt/blob/4.8/translations/qt_zh_CN.ts> | Qt 4.8 的开源许可（LGPL 2.1 / GPL 3），以 Qt 项目所附声明为准 |

## 关于上表中“未知”的部分

原中文翻译的作者和许可条件无法确认。如果你是权利人并希望下架或署名，请开 issue，会立即处理。
若你需要在许可明确的前提下使用，建议只用 `tools/` 脚本，从你自己持有的语言包生成 `.qm`，不要再分发生成结果。
