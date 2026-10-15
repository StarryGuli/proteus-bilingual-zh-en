<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Proteus 8.17 中英对照语言包：英文在前，中文在后，示例为 Proteus 右键菜单">
</p>

<p align="center"><a href="./README.md">English</a> · <b>简体中文</b></p>

替换 **Proteus 8 Professional 8.17** 的语言文件，让每个菜单、对话框、右键菜单都显示成 `英文 中文`。适合对照英文教程和数据手册学习，又想在术语旁边保留中文。

只替换 `.qm` 翻译文件，不修改 EXE、DLL、元件库和许可证。

<p align="center">
  <img src="./docs/screenshots/schematic-capture.jpg" width="100%" alt="Proteus 原理图绘制界面，菜单栏为中英对照：File 文件、Edit 编辑、View 视图、Tool 工具、Design 设计">
</p>

<table>
  <tr>
    <td width="50%"><img src="./docs/screenshots/file-menu.jpg" alt="文件菜单：Open Project 打开工程、Save Project 保存工程"></td>
    <td width="50%"><img src="./docs/screenshots/context-menu.jpg" alt="右键菜单：Place Wire Label 添加网络标号、Highlight Net on current Sheet"></td>
  </tr>
</table>

## 安装（Windows）

1. 保存工程，完全退出 Proteus。
2. **备份** Proteus 安装目录下整个 `Translations` 文件夹。
3. 把 [`release/Translations/`](release/Translations) 里的 4 个文件复制到该 `Translations` 文件夹，同名文件替换，不要多套一层文件夹。
4. 重新启动 Proteus。

**恢复：** 关闭 Proteus，还原备份。如果安装前本来没有 `*_en_US.qm`，直接删掉 `proteus_en_US.qm` 和 `qt_en_US.qm` 也可以。

### 为什么是 4 个文件？

<p align="center">
  <img src="./assets/readme/load-order.svg" width="100%" alt="系统区域 en_US 或 zh_CN 决定 Qt 4 加载 proteus_LOCALE.qm 和 qt_LOCALE.qm，四个文件内容相同，都是双语">
</p>

Proteus 自带的 Qt 4 按系统区域选文件。有的电脑即使 Windows 是中文，区域也会报 `en_US`，只复制 `zh_CN` 两个文件就会毫无效果。这不会更改 Windows 的语言或区域设置。

## 覆盖范围

| 范围 | 结果 |
|---|---|
| 原语言包 | 保留全部 6,226 个主目录条目，查找键不变，改为英文在前 |
| 代码编辑器 | 补入 554 条命令、语法高亮和样式名称 |
| 菜单与对话框 | 对照已安装 EXE/DLL 资源补入 1,902 种标签（含资源名、大小写别名，别名数不等于独立翻译数） |
| Qt 控件 | 补入 Qt 官方 4.8 `zh_CN` 目录里原包缺少的 53 条 |
| 保持原样 | 元件标识、文件路径、协议名、数值、快捷键 |

**不在覆盖范围：** 帮助文档、样例工程、元件数据，以及 Proteus 里硬编码、没有调用翻译接口的文字。

**已知限制：** 固定宽度的按钮、菜单和对话框可能截断较长的双语文字。我在 Proteus 8.17 里确认过菜单栏、文件菜单、右键菜单和原理图绘制界面（见上方截图），没有逐屏检查。

## 验证方式

用 Proteus 自带的 `QtCore4.dll`，在单独的 32 位 Python 进程里逐条读取：主目录 15,765 / 15,765、Qt 目录 1,451 / 1,451 全部通过，`en_US` 区域下两类文件都能自动加载。原始查找键、条目数、`printf` 占位符个数和制表符后的快捷键也与原包核对过。详细结果和 SHA-256 见 [`release/validation.json`](release/validation.json)。

## 自己重新生成

`tools/` 是生成脚本，需要 Windows、已安装的 Proteus 和 32 位 Python（用于 `QtCore4.dll`）。

| 脚本 | 作用 |
|---|---|
| `qm_catalog.py` | 读取完整 `.qm`，正确处理 Qt 的空字符串标记 |
| `build_complete.py` | 生成双语目录，保留原始查找键并加入补译 |
| `qscintilla_zh.py`、`new_labels_zh.py` | 补译词典 |
| `extract_ui_resources.py`、`inspect_resources.py` | 读取 EXE/DLL 里的菜单与对话框资源 |
| `qt4_verify.py` | 用 Proteus 自带 Qt 4 运行库验证读取 |
| `package_complete.py` | 打包 |

路径由两个环境变量提供：`PROTEUS_DIR`（含 `BIN` 的安装目录）和 `ORIGINAL_PATCH_DIR`（原中文语言包所在目录）。脚本从硬编码路径改成环境变量后只做过语法检查，没有完整重跑；遇到问题请开 issue。

## 来源、许可与免责

- `tools/` 里的脚本以 MIT 许可发布，见 [LICENSE](LICENSE)。
- `.qm` 语言文件和 `data/` 是对第三方内容的衍生，**不适用**该许可，归属见 [NOTICE.md](NOTICE.md)。原中文语言包的作者和许可未知，再分发权利并未确认。
- Proteus 是 Labcenter Electronics 的产品。本项目与其无关，**不提供** Proteus 本体、安装程序或许可证，使用 Proteus 需自行获得合法授权。
- 如果你是权利人并希望下架或署名，请开 issue，会尽快处理。
