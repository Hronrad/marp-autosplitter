import gradio as gr
from cli import convert_markdown 
import tempfile
import traceback
import os

async def generate_ppt(input_mode, file_obj, text_content, theme, level, formats):
    try:
        input_path = ""
        
        if input_mode == "upload":
            if not file_obj:
                return None, "❌ 请先上传 Markdown 文件. Please upload a Markdown file first."
            input_path = file_obj.name
        else:
            if not text_content.strip():
                return None, "❌ 请输入 Markdown 文本内容. Please enter Markdown text."
            fd, temp_path = tempfile.mkstemp(suffix=".md", text=True)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(text_content)
            input_path = temp_path

        output_files = await convert_markdown(
            input_file=input_path, 
            theme=theme, 
            style_class="", 
            heading_split_levels=int(level), 
            output_formats=formats
        )
        if output_files:
            return output_files, "🎉 生成成功！请点击下载。Success! Now you can download."
        else:
            return None, "❌ 生成失败，请检查控制台报错。Error occurred during generation. Please check console for details."
            
    except Exception as e:
        error_detail = traceback.format_exc()
        print(error_detail) 
        return None, f"❌ 发生异常:\n\n{error_detail}"


with gr.Blocks(title="Marp 极速排版引擎") as demo:
    gr.Markdown("# Marp-Autosplitter 可视化控制台 Console")
    gr.Markdown("上传 Markdown 文档或直接粘贴内容，调整参数，一键生成排版完美的 PPTX。 Upload your Markdown file or paste text, tweak settings, and generate perfectly paginated PPTX with one click.")
    
    with gr.Row():
        with gr.Column():
            input_mode = gr.State(value="upload")
            
            with gr.Tabs():
                with gr.Tab("📁 1. 上传 Markdown 文件 (Upload)") as tab_upload:
                    file_in = gr.File(label="文件 (.md)", file_types=[".md"])
                with gr.Tab("✍️ 1. 直接输入内容 (Type Content)") as tab_text:
                    text_in = gr.Textbox(label="粘贴或输入 Markdown 代码", lines=10)
            
            tab_upload.select(lambda: "upload", inputs=None, outputs=input_mode)
            tab_text.select(lambda: "text", inputs=None, outputs=input_mode)

            theme_in = gr.Dropdown(
                choices=["default", "gaia", "uncover", "academic", "beam", "rose-pine-dawn", "rose-pine-moon", "rose-pine-dawn-modern"], 
                value="default", 
                label="2. 选择主题皮肤 Choose Theme")
            with gr.Accordion("💡 点击查看主题说明 (Theme Details)", open=False):
                gr.Markdown("""
- **default**: Small font, clean black-on-white, best compatibility.
- **gaia**: Medium font, warm tone, low contrast. Good for humanities, art/design, eco/lifestyle topics.
- **uncover**: Large font, minimalist, high contrast. Good for product launches, TED-style talks.
- **academic**(community theme):  Medium font with red titles. Note: right-aligned; use only when needed.
- **beam**(community theme): Small font, Beamer-like. Good for academic content.
- **rose-pine-dawn**(community theme): Small font, light background, gentle style.
- **rose-pine-moon**(community theme): Small font, dark background, elegant for dark themes.
- **rose-pine-dawn-modern**(community theme): Medium font, adds a modern card-style title on top of rose-pine-dawn.
            """)
            level_in = gr.Slider(minimum=1, maximum=6, value=2, step=1, label="3. 触发分页的最高标题层级 Heading Level to Trigger Pagination")
            format_in = gr.CheckboxGroup(choices=["pptx", "pdf", "html", "md"], value=["pptx", "pdf"], label="4. 输出格式 Output Formats")
            submit_btn = gr.Button("⚡ 开始生成 PPT ", variant="primary")
            
        with gr.Column():
            output_msg = gr.Textbox(label="运行状态 status", interactive=False, lines=15)
            file_out = gr.File(label="5. 下载生成的演示文稿 Download Generated Presentation", interactive=False)

    submit_btn.click(
        fn=generate_ppt,
        inputs=[input_mode, file_in, text_in, theme_in, level_in, format_in],
        outputs=[file_out, output_msg]
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True, server_port=9080, prevent_thread_lock=False, theme=gr.themes.Soft())