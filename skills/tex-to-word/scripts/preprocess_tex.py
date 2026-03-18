"""
preprocess_tex.py — LaTeX 预处理 v3
  1. \\ref{} → 实际编号数字（从 .aux 解析）
  2. equation → $$ display math $$ + 下一行 EQNUM(N)
  3. 移除 \\textit / \\emph 斜体

策略：$$ 让 pandoc 生成居中的 OMML 段落，EQNUM(N) 单独成段，
postprocess 再把编号合并回公式段落并右对齐。

用法: python preprocess_tex.py main_merged.tex [main.aux]
输出: main_merged_prepped.tex
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
    """
    \\begin{equation}...\\end{equation}
    →
    $$ math $$

    EQNUM(N)

    EQNUM(N) 独占一个段落（空行分隔），postprocess 会合并回上方公式段落。
    """
    eq_counter = [0]

    def replacer(m):
        eq_counter[0] += 1
        body = m.group(1)
        body = re.sub(r'\\label\{[^}]+\}', '', body).strip()
        body = re.sub(r'\\boxed\{([^}]*)\}', r'\1', body)
        num = eq_counter[0]
        # $$ 前后的空行保证 pandoc 将其作为 display math 段落
        # EQNUM 单独一行，会成为一个单独的文本段落
        return f'\n\n$${body}$$\n\nEQNUM({num})\n\n'

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


# ============================================================
# 英文学术术语 → 中文翻译
# ============================================================
TERM_MAP = {
    # 环境名/标签（pandoc 会输出这些英文名）
    'Proof':        '证明',
    'proof':        '证明',
    'Proposition':  '命题',
    'proposition':  '命题',
    'Theorem':      '定理',
    'theorem':      '定理',
    'Lemma':        '引理',
    'lemma':        '引理',
    'Corollary':    '推论',
    'corollary':    '推论',
    'Definition':   '定义',
    'definition':   '定义',
    'Remark':       '注',
    'remark':       '注',
    'Assumption':   '假设',
    'assumption':   '假设',
    'Property':     '性质',
    'property':     '性质',
    'Example':      '例',
    'example':      '例',
    'Algorithm':    '算法',
    'Figure':       '图',
    'Table':        '表',
}


def translate_academic_terms(text):
    """
    将 pandoc 输出中残留的英文学术术语替换为中文。
    使用词边界匹配避免误替换（如 'Table' 不会匹配 'Tablecloth'）。
    仅替换独立出现的术语（前后为空格、标点或行首行尾）。
    """
    count = 0
    for en, zh in TERM_MAP.items():
        # 匹配独立单词：前后是非字母字符或行首行尾
        pattern = rf'(?<![a-zA-Z]){re.escape(en)}(?![a-zA-Z])'
        matches = len(re.findall(pattern, text))
        if matches > 0:
            text = re.sub(pattern, zh, text)
            count += matches
    print(f'  翻译了 {count} 个英文术语 → 中文')
    return text


def inline_bibliography(text, tex_dir):
    """
    将 .bbl 文件的内容内联到 .tex 中，替换 \\bibliographystyle 和 \\bibliography 命令。
    这样 pandoc 能直接处理参考文献列表，无需外部工具。
    
    前提：必须先用 bibtex 编译过，生成 .bbl 文件。
    """
    # 找到 .bbl 文件
    bbl_path = os.path.join(tex_dir, 'main.bbl')
    if not os.path.exists(bbl_path):
        # 尝试其他名字
        for f in os.listdir(tex_dir):
            if f.endswith('.bbl'):
                bbl_path = os.path.join(tex_dir, f)
                break

    if not os.path.exists(bbl_path):
        print('  警告: 未找到 .bbl 文件，跳过参考文献内联')
        return text

    with open(bbl_path, 'r', encoding='utf-8', errors='ignore') as f:
        bbl_content = f.read()

    print(f'  读取 {os.path.basename(bbl_path)} ({len(bbl_content)} 字符)')

    # 删除 \bibliographystyle{...}
    text = re.sub(r'\\bibliographystyle\{[^}]*\}\s*', '', text)

    # 将 \bibliography{...} 替换为 .bbl 的内容
    if '\\bibliography{' in text:
        text = re.sub(r'\\bibliography\{[^}]*\}', bbl_content, text)
        print('  已将 \\bibliography{} 替换为 .bbl 内容')
    else:
        # 如果没有 \bibliography 命令，在 \end{document} 前插入
        text = text.replace('\\end{document}', bbl_content + '\n\\end{document}')
        print('  已在 \\end{document} 前插入 .bbl 内容')

    return text


def preprocess(tex_path, aux_path=None):
    if aux_path is None:
        aux_path = os.path.join(os.path.dirname(tex_path), 'main.aux')
    tex_dir = os.path.dirname(os.path.abspath(tex_path))

    with open(tex_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print('[1/6] 解析 .aux 标签...')
    labels = parse_aux_labels(aux_path)
    print('[2/6] 替换交叉引用...')
    text = resolve_refs(text, labels)
    print('[3/6] 公式编号...')
    text = convert_equations(text)
    print('[4/6] 移除斜体...')
    text = remove_italics(text)
    print('[5/6] 英文术语 → 中文...')
    text = translate_academic_terms(text)
    print('[6/6] 内联参考文献 (.bbl)...')
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
