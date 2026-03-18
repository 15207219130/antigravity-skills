---
name: tex-to-word
description: 将数学建模相关LaTeX论文转换为Word文档，保留原生公式、正确字体和学术排版规范
---

# TeX → Word 转换技能

将 `.tex` 论文转换为格式规范的 `.docx` 文件，适用于数学建模、管理科学、运筹学等领域的中文学术论文。

## 核心规范

| 项目 | 规范 |
|------|------|
| 公式 | Word 原生 OMML 格式（非图片），**居中显示** |
| 公式编号 | 显式 (1), (2), (3)...，**右对齐**，与公式同行 |
| 交叉引用 | `\ref{}` / `\eqref{}` → 解析为实际编号数字（从 `.aux` 文件读取） |
| 中文字体 | **宋体** (SimSun) |
| 英文/数字字体 | **Times New Roman** |
| 标题字体 | **黑体** (SimHei) |
| 斜体 | **全部移除**（包括 proposition/theorem/lemma 内容，不要改字体） |
| 表格 | **三线表**（顶线+表头底线+底线，无竖线和其他横线） |
| 表标题 | 表名在表**上方** |
| 图标题 | 图名在图**下方** |
| 模板 | 若用户提供 `.docx` 模板，内容填入模板样式 |
| 英文术语 | **全部翻译为中文**（Proof→证明, Proposition→命题, Theorem→定理 等）|

## 前置依赖

```powershell
# 检查
pandoc --version    # 需要 ≥ 2.16
pip show python-docx  # 需要 python-docx + lxml

# 安装（如缺失）
pip install python-docx lxml
```

## 转换流程（4 步）

```
merge_tex.py → preprocess_tex.py → pandoc → postprocess_docx.py
   合并子文件     解析引用+编号+去斜体    转OMML    字体+三线表+居中公式+去斜体
```

### Step 1: 合并 LaTeX 子文件

将 `\input{}` 引用的子文件内联合并为单个 `.tex`：

```powershell
python scripts/merge_tex.py main.tex
# 输出: main_merged.tex
```

### Step 2: 预处理 LaTeX

解析交叉引用、添加公式编号标记、移除斜体命令：

```powershell
python scripts/preprocess_tex.py main_merged.tex main.aux
# 输出: main_merged_prepped.tex
```

> [!IMPORTANT]
> **必须先用 xelatex 编译过 main.tex** 生成 `.aux` 文件，否则交叉引用无法解析。

预处理做了四件事：
1. **解析 `\ref{}`**：从 `.aux` 文件读取 label→编号映射，替换为实际数字
2. **公式编号**：`\begin{equation}...\end{equation}` → `$$ math $$` + 下一行 `EQNUM(N)`
3. **去斜体**：移除 `\textit{}`、`\emph{}`，在定理环境中添加 `\upshape`
4. **英文术语翻译**：将 Proof→证明, Proposition→命题, Theorem→定理, Lemma→引理, Corollary→推论, Definition→定义, Remark→注, Assumption→假设, Figure→图, Table→表 等独立出现的英文学术术语替换为对应中文（使用词边界匹配避免误替换）

### Step 3: Pandoc 转换

```powershell
# 无模板
pandoc main_merged_prepped.tex -o output.docx --from latex --to docx --number-sections

# 有模板
pandoc main_merged_prepped.tex -o output.docx --from latex --to docx --reference-doc=template.docx --number-sections
```

### Step 4: 后处理

```powershell
python scripts/postprocess_docx.py output.docx output_final.docx
```

后处理做了五件事：
1. **正文字体** → 宋体 + Times New Roman (12pt)
2. **标题字体** → 黑体
3. **移除所有斜体**（XML 层面彻底清除 `w:i` 和 `w:iCs`）
4. **三线表**：所有表格只保留顶线、表头底线、末行底线
5. **公式居中+编号右对齐**：
   - 找到 `EQNUM(N)` 段落
   - 在上方公式段落的 OMML 元素**前**插入 tab run（推到居中制表位 4320 twips）
   - 在公式段落**末尾**添加 tab + `(N)`（推到右对齐制表位 8640 twips）
   - 删除 `EQNUM(N)` 段落
   - 最终布局：`[center-tab] 公式 [right-tab] (N)`

### Step 5 (可选): 注入 Word 模板

如果用户提供了 Word 模板文档（含封面、目录框架等）：

```powershell
python scripts/inject_into_template.py template.docx output_final.docx result.docx "正文开始"
```

模板中应包含标记文本（默认"正文开始"），脚本会在该位置插入转换后的内容并删除标记。

## 完整命令序列

```powershell
# 1. 合并
python scripts/merge_tex.py main.tex

# 2. 预处理
python scripts/preprocess_tex.py main_merged.tex main.aux

# 3. Pandoc
pandoc main_merged_prepped.tex -o output.docx --from latex --to docx --number-sections

# 4. 后处理
python scripts/postprocess_docx.py output.docx output_final.docx

# 5. (可选) 注入模板
python scripts/inject_into_template.py template.docx output_final.docx result.docx
```

## 公式编号技术细节

> [!NOTE]
> Word 中"公式居中、编号右对齐"的标准做法是**三栏制表位布局**，而非段落居中对齐。

pandoc 将 `$$` 转为 OMML 的 `m:oMathPara` 元素，这是一个段落级别的数学块。postprocess 通过以下 XML 操作实现居中+右对齐：

```xml
<w:p>
  <w:pPr>
    <w:tabs>
      <w:tab w:val="center" w:pos="4320"/>  <!-- 居中制表位 -->
      <w:tab w:val="right" w:pos="8640"/>   <!-- 右对齐制表位 -->
    </w:tabs>
  </w:pPr>
  <w:r><w:tab/></w:r>           <!-- tab → 推到居中位置 -->
  <m:oMathPara>...</m:oMathPara> <!-- OMML 公式 -->
  <w:r><w:tab/></w:r>           <!-- tab → 推到右对齐位置 -->
  <w:r><w:t>(1)</w:t></w:r>     <!-- 编号 -->
</w:p>
```

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 公式变成图片 | 确保 pandoc ≥ 2.16，`--to docx` 默认输出 OMML |
| `\ref{}` 显示 ?? | 确保先编译 LaTeX 生成 `.aux`，传给 preprocess |
| 编号在公式下方 | 不要用 `$$`（块级），用 preprocess+postprocess 合并段落 |
| 编号不靠右 | 检查制表位 pos 值是否匹配页面宽度 |
| proposition 内容斜体 | postprocess 会彻底移除所有 `w:i` 属性 |
| 表格有竖线 | postprocess 会将所有表格转为三线表 |
| 图片缺失 | 确保 `figures/` 目录与 `.tex` 在同一目录 |
| 参考文献缺失 | 添加 `--citeproc --bibliography=references.bib` |

## 注意事项

1. **手动检查公式**：复杂 LaTeX 宏（`\newcommand` 等）可能需要手动调整
2. **图表编号**：pandoc 生成的编号可能与 LaTeX 不同，需在 Word 中统一
3. **页眉页脚**：`--reference-doc` 会保留模板的页眉页脚
4. **多行公式**：`align`/`aligned` 环境需要特殊处理，当前脚本只处理 `equation`
