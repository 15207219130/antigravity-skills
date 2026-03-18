"""
preprocess_tex.py — LaTeX 预处理 v4
  1. \ref{} → 实际编号（从 .aux）
  2. equation → $$ + EQNUM(N)
  3. 去斜体
  4. 英文术语 → 中文
  5. 内联 .bbl 参考文献

用法: python preprocess_tex.py main_merged.tex [main.aux]
"""
import re
import sys
import os


def parse_aux_labels(aux_path):
    labels = {}
    if not os.path.exists(aux_path):
        print(f'  警告: .aux 不存在: {aux_path}')
        return labels
    with open(aux_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', text):
        key, val = m.group(1), m.group(2)
        if val and val != '??':
            labels[key] = val
    print(f'  从 .aux 解析到 {len(labels)} 个标签')
    return labels


def resolve_refs(text, labels):
    c1 = len(re.findall(r'\\ref\{[^}]+\}', text))
    c2 = len(re.findall(r'\\eqref\{[^}]+\}', text))
    text = re.sub(r'\\eqref\{([^}]+)\}',
                  lambda m: f'({labels.get(m.group(1), "??")})', text)
    text = re.sub(r'\\ref\{([^}]+)\}',
                  lambda m: labels.get(m.group(1), '??'), text)
    print(f'  替换了 {c1} 个 \\ref 和 {c2} 个 \\eqref')
    return text


def convert_equations(text):
    eq_counter = [0]
    def replacer(m):
        eq_counter[0] += 1
        body = m.group(1)
        body = re.sub(r'\\label\{[^}]+\}', '', body).strip()
        body = re.sub(r'\\boxed\{([^}]*)\}', r'\1', body)
        return f'\n\n$${body}$$\n\nEQNUM({eq_counter[0]})\n\n'
    text = re.sub(
        r'\\begin\{equation\}(.*?)\\end\{equation\}',
        replacer, text, flags=re.DOTALL
    )
    print(f'  编号了 {eq_counter[0]} 个公式')
    return text


def remove_italics(text):
    text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]*)\}', r'\1', text)
    for env in ['proposition', 'theorem', 'lemma', 'corollary',
                'definition', 'remark', 'assumption', 'property']:
        text = text.replace(f'\\begin{{{env}}}',
                           f'\\begin{{{env}}}\\upshape ')
    return text


TERM_MAP = {
    'Proof': '证明', 'proof': '证明',
    'Proposition': '命题', 'proposition': '命题',
    'Theorem': '定理', 'theorem': '定理',
    'Lemma': '引理', 'lemma': '引理',
    'Corollary': '推论', 'corollary': '推论',
    'Definition': '定义', 'definition': '定义',
    'Remark': '注', 'remark': '注',
    'Assumption': '假设', 'assumption': '假设',
    'Property': '性质', 'property': '性质',
    'Example': '例', 'example': '例',
    'Algorithm': '算法',
    'Figure': '图',
    'Table': '表',
}


def translate_academic_terms(text):
    count = 0
    for en, zh in TERM_MAP.items():
        pattern = rf'(?<![a-zA-Z]){re.escape(en)}(?![a-zA-Z])'
        matches = len(re.findall(pattern, text))
        if matches > 0:
            text = re.sub(pattern, zh, text)
            count += matches
    print(f'  翻译了 {count} 个英文术语 → 中文')
    return text


def inline_bibliography(text, tex_dir):
    """读取 .bbl 文件，替换 bibliography 相关命令为实际内容"""
    # 找 .bbl 文件
    bbl_path = os.path.join(tex_dir, 'main.bbl')
    if not os.path.exists(bbl_path):
        for fname in os.listdir(tex_dir):
            if fname.endswith('.bbl'):
                bbl_path = os.path.join(tex_dir, fname)
                break
    if not os.path.exists(bbl_path):
        print('  警告: 未找到 .bbl 文件')
        return text

    with open(bbl_path, 'r', encoding='utf-8', errors='ignore') as f:
        bbl = f.read()
    print(f'  读取 {os.path.basename(bbl_path)} ({len(bbl)} 字符)')

    # 逐行处理，删除 \bibliographystyle 行，替换 \bibliography 行
    out_lines = []
    replaced = False
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('\\bibliographystyle'):
            continue  # 跳过
        elif stripped.startswith('\\bibliography{'):
            out_lines.append(bbl)  # 替换为 .bbl 内容
            replaced = True
            print('  已替换 \\bibliography{} 为 .bbl 内容')
        else:
            out_lines.append(line)

    if not replaced:
        # 在 \end{document} 前插入
        final = []
        for line in out_lines:
            if line.strip() == '\\end{document}':
                final.append(bbl)
            final.append(line)
        out_lines = final
        print('  已在 \\end{document} 前插入 .bbl')

    return '\n'.join(out_lines)


def convert_figures_to_png(text):
    """将 \\includegraphics 中的 .pdf 路径替换为 .png"""
    count = 0
    def replacer(m):
        nonlocal count
        count += 1
        return m.group(0).replace('.pdf', '.png')
    text = re.sub(r'\\includegraphics\[.*?\]\{.*?\.pdf\}', replacer, text)
    print(f'  {count} 个 \\includegraphics .pdf → .png')
    return text


def replace_tikz_with_images(text, tex_dir):
    """将 tikzpicture 环境替换为 \\includegraphics 指向提取的 PNG"""
    figures_dir = os.path.join(tex_dir, 'figures')

    # 找出 figures/ 下所有 tikz_*.png
    tikz_pngs = []
    if os.path.exists(figures_dir):
        tikz_pngs = sorted([f for f in os.listdir(figures_dir) if f.startswith('tikz_') and f.endswith('.png')])

    if not tikz_pngs:
        print('  无 TikZ PNG 文件，跳过')
        return text

    # 按顺序替换 tikzpicture 环境
    tikz_pattern = re.compile(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', re.DOTALL)
    matches = list(tikz_pattern.finditer(text))

    if len(matches) != len(tikz_pngs):
        print(f'  警告: {len(matches)} 个 TikZ 但 {len(tikz_pngs)} 个 PNG，按顺序匹配')

    count = 0
    for i, m in enumerate(matches):
        if i < len(tikz_pngs):
            png_name = tikz_pngs[i]
            replacement = f'\\includegraphics[width=0.85\\textwidth]{{figures/{png_name}}}'
            text = text[:m.start()] + replacement + text[m.end():]
            # 更新后续 match 的位置（因为文本长度变了）
            offset = len(replacement) - (m.end() - m.start())
            matches = list(tikz_pattern.finditer(text))  # 重新搜索
            count += 1

    print(f'  {count} 个 TikZ → \\includegraphics PNG')
    return text


def preprocess(tex_path, aux_path=None):
    if aux_path is None:
        aux_path = os.path.join(os.path.dirname(tex_path), 'main.aux')
    tex_dir = os.path.dirname(os.path.abspath(tex_path))

    with open(tex_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print('[1/8] 解析 .aux 标签...')
    labels = parse_aux_labels(aux_path)
    print('[2/8] 替换交叉引用...')
    text = resolve_refs(text, labels)
    print('[3/8] 公式编号...')
    text = convert_equations(text)
    print('[4/8] 移除斜体...')
    text = remove_italics(text)
    print('[5/8] 英文术语 → 中文...')
    text = translate_academic_terms(text)
    print('[6/8] PDF 图片 → PNG...')
    text = convert_figures_to_png(text)
    print('[7/8] TikZ → PNG 图片...')
    text = replace_tikz_with_images(text, tex_dir)
    print('[8/8] 内联参考文献 (.bbl)...')
    text = inline_bibliography(text, tex_dir)

    out = tex_path.replace('.tex', '_prepped.tex')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'\n预处理完成 → {out}')
    return out


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python preprocess_tex.py <merged.tex> [main.aux]')
        sys.exit(1)
    preprocess(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
