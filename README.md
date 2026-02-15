
# Marp-Autosplitter

**Marp-Autosplitter** 是一个快速、智能的命令行工具，能将任意 Markdown 文档完美转换为排版精美、高度精准的 PPTX 和 PDF 演示文稿。它通过自动切分内容并修复跨页结构，再利用 Marp 转为适合展示的 PPTX 和 PDF 演示文稿。程序确保每一页都美观且信息完整，无论是文本、表格还是 LaTeX 公式，都能得到完美呈现。

## 核心特性

* **物理级精准防溢出**：告别字符估算，真实渲染高度测量，100% 杜绝内容越界。
* **语义感知分页**：支持根据指定的标题层级（如 H1、H2）自动智能断页。
* **细胞级结构保护**：跨页时自动修补 Markdown 表格（补全表头）与列表结构，确保 LaTeX 公式完美渲染。
* **高度可定制**：内置多款主题，并支持挂载本地 `themes` 文件夹拓展自定义 CSS 皮肤。
* **跨平台免配置**：自动探测系统内置的 Chrome/Edge 浏览器，支持 Windows, macOS, Linux。

## 安装配置

请确保你的电脑已安装 Python 3.10+ 和 Node.js。

1. **克隆并进入项目**
```bash
git clone <your-repo-url>
cd marp-autosplitter
```

2. **安装核心依赖**
```bash
npm install
pip install -r requirements.txt
```


*(注：程序会自动调用本机的 Chrome/Edge，无需额外执行 playwright install)*

## 快速开始

基础转换（默认输出 PPTX 和 PDF，使用 `default` 主题）：

```bash
python cli.py report.md
```

带参数的进阶转换（使用 `gaia` 主题，文档中前 3 级标题都触发分页，输出 PPTX 和 HTML）：

```bash
python cli.py report.md -t gaia -l 3 -f pptx html

```

### ⚙️ 命令参数参考

| 参数 | 简写 | 说明 | 默认值 |
| --- | --- | --- | --- |
| `input` | 无 | **[必填]** 要转换的 Markdown 文件路径 | - |
| `--theme` | `-t` | 主题名称（支持 `default`, `gaia`, `uncover` 及 `themes/` 下的自定义主题） | `default` |
| `--level` | `-l` | 触发自动分页的 “前 $n$ 个实际存在的最高标题层级”。例如设为 2 时，若文档仅含 H1 和 H3，则 H1 与 H3 均会触发分页起新页。 | `2` |
| `--class_style` | `-c` | 附加的全局 CSS 类（如 `lead` 居中, `invert` 反色暗黑模式） | 空 |
| `--format` | `-f` | 指定输出格式，多个格式用空格隔开（可选: `pptx`, `pdf`, `html`） | `pptx pdf` |

## 产物输出

生成的中间件 `.md` 和最终的 PPT 文件均会自动保存在项目根目录下的 `output_slides` 文件夹中。


## 反馈与支持
使用中如遇问题或有任何建议，欢迎提交 Issue 或 Pull Request！
如果觉得本项目对你有帮助，别忘了点个 Star 支持一下！✨
