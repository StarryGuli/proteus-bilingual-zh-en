import os
# coding: utf-8
from pathlib import Path
import json,hashlib,zipfile
root=Path(__file__).resolve().parent.parent
out=root/'outputs/Proteus-8.17-Bilingual-v2'
stats=json.loads((out/'validation.json').read_text(encoding='utf-8'))
stats['verification']={
 'Qt4_runtime':'QtCore4.dll from the installed Proteus, loaded in a separate 32-bit Python process',
 'proteus_lookup_checks_passed':15765,
 'qt_lookup_checks_passed':1451,
 'Qt4_system_locale':'en_US',
 'locale_based_load_proteus':True,
 'locale_based_load_qt':True,
 'original_keys_and_record_counts_preserved':True,
 'printf_placeholder_counts_checked':True,
 'original_shortcut_suffixes_checked':True,
 'running_Proteus_modified_or_restarted':False,
 'visual_layout_checked_in_Proteus':False}
stats['sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/'Translations').glob('*.qm')}
(out/'validation.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'安装说明.txt').write_text('''Proteus 8.17 中英对照补齐版 v2
显示顺序：英文在前，中文在后。

你这台电脑已确认的安装目录：
<Proteus install dir>\\Translations

安装步骤：
1. 保存项目并完全退出 Proteus。
2. 把上述安装目录的整个 Translations 文件夹复制一份，作为安装前备份。
3. 将本包 Translations 文件夹里的四个 .qm 文件复制到上述安装目录的 Translations 中。
   有同名文件则替换；没有同名文件则新增。不要再套一层 Translations 文件夹。
4. 重新启动 Proteus。

关键说明：
这台电脑的 Qt4 区域设置实际是 en_US。
因此 proteus_en_US.qm、qt_en_US.qm 是本机生效用的名字，不能只复制 zh_CN 两个文件。
proteus_zh_CN.qm、qt_zh_CN.qm 则供简体中文区域设置使用，文件内容与对应 en_US 文件相同。
这不会更改 Windows 的语言或区域设置。

恢复英文：
关闭 Proteus，移除本次新增的 proteus_en_US.qm、qt_en_US.qm，并从安装前备份还原原有语言文件。
若安装前本来就有上述 en_US 文件，应还原备份，不能直接删除原文件。

本版修正与范围：
- 修正 v1 转换提前终止的问题，完整保留原包 6,226 个 Proteus 条目及原始查找键。
- 原包中的菜单、原理图、PCB、物料清单、设置、对话框等中文均改为英文在前的双语。
- 补入代码编辑器 554 条命令、语法高亮和语言样式翻译，合并到主翻译文件，无须额外编辑器加载器。
- 对照本机 EXE/DLL 的菜单、对话框资源补入 1,902 种标签；为资源名大小写和 CORE/PDS 名称建立别名。
  这些别名是同一标签的多个查找入口，不能把别名数量当作独立翻译数量。
- 补充 Qt 官方 4.8 中文目录中现有包缺少的 53 条中文翻译。
- 保留元件标识、文件路径、协议名、数值和快捷键等技术内容。
- 此包仅修改语言文件，未修改安装目录中的 EXE、DLL、项目、元件库或许可证。

已完成的检查：
- 使用本机 Proteus 自带 QtCore4.dll，逐条验证 15,765 条主目录和 1,451 条 Qt 目录翻译读取。
- 验证 en_US 区域设置下两类语言文件均可自动加载。
- 校验原始查找键、条目数量、printf 参数数量和制表符后的快捷键。

实际使用的限制：
- 没有在你的运行中 Proteus 里替换文件或重启，所以尚未逐屏检查排版。
- 固定宽度按钮、菜单或对话框可能截断双语文字。
- 新增资源的查找入口做过运行库检查，但不代表已逐一操作全部功能验证界面调用。
- 帮助文档、样例工程内容、元件数据和模块硬编码且未调用翻译接口的文字不在本语言包覆盖范围。

本地材料：你提供的原始语言包，以及本机已安装程序的菜单和对话框资源。
Qt 补充翻译来源：https://github.com/qt/qt/blob/4.8/translations/qt_zh_CN.ts
详细检查结果和 SHA-256 见 validation.json。
''',encoding='utf-8-sig')
target=root/'outputs/Proteus-8.17-Bilingual-v2.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in out.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(out))
with zipfile.ZipFile(target) as z:assert z.testzip() is None
print(target)
print('Verified package:',target.stat().st_size,'bytes')
