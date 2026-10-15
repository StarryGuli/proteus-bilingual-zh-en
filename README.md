# Proteus 8.17 中英对照语言包

把 Proteus 8 Professional 的界面从「纯中文」或「纯英文」改成 **英文在前、中文在后** 的对照显示，例如：

```
Open Project 打开工程
Place Wire Label 添加网络标号
Highlight Net on PCB Layout 在PCB布版中高亮显示网络
```

只替换语言文件（`.qm`），不修改 Proteus 的 EXE、DLL、元件库和许可证。

| 菜单 | 右键菜单 |
|---|---|
| ![文件菜单](docs/screenshots/file-menu.jpg) | ![右键菜单](docs/screenshots/context-menu.jpg) |

![原理图绘制界面](docs/screenshots/schematic-capture.jpg)

## 安装（Windows）

1. 保存工程，完全退出 Proteus。
2. **备份** 安装目录下整个 `Translations` 文件夹。
3. 把 [`release/Translations/`](release/Translations) 里的 4 个 `.qm` 文件复制到安装目录的 `Translations` 中，同名文件替换，不要多套一层文件夹。
4. 重新启动 Proteus。

> **为什么是 4 个文件？** Proteus 内置的 Qt4 按系统区域设置选文件。区域是 `en_US` 时读 `*_en_US.qm`，是 `zh_CN` 时读 `*_zh_CN.qm`。两组内容相同，都复制才不会因区域不同而不生效。这不会更改 Windows 的语言或区域设置。

**恢复**：关闭 Proteus，把备份的 `Translations` 还原。若安装前并没有 `*_en_US.qm`，也可以直接删掉本包新增的 `proteus_en_US.qm` 和 `qt_en_US.qm`。

## 覆盖范围与已知限制

- 保留原语言包全部 6,226 个主目录条目及原始查找键，并改为英文在前的双语。
- 补入代码编辑器 554 条命令、语法高亮和样式翻译。
- 对照 Proteus 自带 EXE/DLL 的菜单、对话框资源补入 1,902 种标签（含资源名大小写、CORE/PDS 名称的别名，别名数不等于独立翻译数）。
- 补入 Qt 官方 4.8 中文目录里原包缺少的 53 条。
- 保留元件标识、文件路径、协议名、数值、快捷键等技术内容。
- **固定宽度的按钮、菜单、对话框可能截断双语文字。**
- 帮助文档、样例工程、元件数据，以及程序里硬编码、没调用翻译接口的文字不在覆盖范围内。

## 验证

用目标机器上 Proteus 自带的 `QtCore4.dll`（32 位进程）逐条读取：主目录 15,765 条、Qt 目录 1,451 条全部通过；`en_US` 区域下两类文件均可自动加载；原始查找键、条目数、printf 占位符个数、制表符后的快捷键均已核对。详见 [`release/validation.json`](release/validation.json)。

已在 Proteus 8.17 中实际加载并确认菜单、右键菜单和原理图界面显示正常（见上方截图）。其余界面未逐屏检查。

## 自己重新生成

`tools/` 是生成脚本，只在 Windows 上、且已安装 Proteus 时能完整运行（需要 32 位 Python 和 `QtCore4.dll`）：

| 脚本 | 作用 |
|---|---|
| `qm_catalog.py` | 读取完整 `.qm`，正确处理 Qt 的空字符串标记 |
| `build_complete.py` | 生成双语目录，保留原始查找键并加入补译 |
| `qscintilla_zh.py`、`new_labels_zh.py` | 补译词典 |
| `extract_ui_resources.py`、`inspect_resources.py` | 读取 EXE/DLL 里的菜单与对话框资源 |
| `qt4_verify.py` | 用 Proteus 自带的 Qt4 运行库验证读取 |
| `package_complete.py` | 打包 |

脚本通过环境变量取路径：`PROTEUS_DIR`（Proteus 安装目录，其下有 `BIN`）、`ORIGINAL_PATCH_DIR`（原中文语言包所在目录）。**路径改成环境变量后没有重新完整运行过**，仅做过语法检查；遇到问题请开 issue。

## 来源、许可与免责

- 脚本（`tools/`）以 MIT 许可发布，见 [LICENSE](LICENSE)。
- `.qm` 语言文件和 `data/` 中的内容是对第三方内容的衍生与整合，**不适用上面的 MIT 许可**。来源与归属见 [NOTICE.md](NOTICE.md)。
- Proteus 是 Labcenter Electronics 的商标与软件。本项目与 Labcenter 无关，**不提供 Proteus 本体、安装程序或许可证**，使用 Proteus 需要自行获得有效授权。
- 如权利人认为本仓库内容侵权，请开 issue 或联系仓库所有者，将尽快处理。

---

## English summary

A bilingual (English first, Chinese second) UI language pack for **Proteus 8.17 Professional**. It ships four Qt `.qm` translation files (`proteus_{en_US,zh_CN}.qm`, `qt_{en_US,zh_CN}.qm`, identical per pair) that you copy into Proteus's `Translations` folder after backing it up. No executables or libraries are modified. Layout may truncate in fixed-width widgets. Proteus itself is **not** included; you need your own licensed copy. See [NOTICE.md](NOTICE.md) for third-party attribution.
