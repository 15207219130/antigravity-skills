"""
merge_tex.py — 将 \input{} 引用的子文件内联合并为单个 .tex 文件
用法: python merge_tex.py main.tex
输出: main_merged.tex
"""
import re
import os
import sys


def merge(main_path):
    """递归合并所有 \\input{} 引用的子文件"""
    base = os.path.dirname(os.path.abspath(main_path))
    with open(main_path, 'r', encoding='utf-8') as f:
        text = f.read()

    def replacer(m):
        fname = m.group(1).strip()
        if not fname.endswith('.tex'):
            fname += '.tex'
        fp = os.path.join(base, fname)
        if os.path.exists(fp):
            print(f'  合并: {fname}')
            with open(fp, 'r', encoding='utf-8') as f2:
                content = f2.read()
            # 递归处理子文件中的 \input
            content = re.sub(
                r'\\input\{([^}]+)\}',
                lambda m2: replacer(m2),
                content
            )
            return content
        else:
            print(f'  警告: 文件不存在 {fp}')
            return m.group(0)

    text = re.sub(r'\\input\{([^}]+)\}', replacer, text)

    out = main_path.replace('.tex', '_merged.tex')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'\n合并完成 → {out}')
    return out


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python merge_tex.py <main.tex>')
        sys.exit(1)
    merge(sys.argv[1])
