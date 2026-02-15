import gradio as gr
from cli import convert_markdown 

async def generate_ppt(file_obj, theme, level, formats):
    if not file_obj:
        return None, "❌ 请先上传 Markdown 文件. Please upload a Markdown file first."
    

    input_path = file_obj.name
    
    try:

        output_files = await convert_markdown(
            input_file=input_path, 
            theme=theme, 
            style_class="", 
            heading_split_levels=int(level), 
            output_formats=formats
        )
        if output_files:
            return output_files, "🎉 生成成功！请点击上方下载。Success! Click above to download."
        else:
            return None, "❌ 生成失败，请检查控制台报错。Error occurred during generation. Please check console for details."
    except Exception as e:
        return None, f"❌ 发生异常: {str(e)}"

with gr.Blocks(title="Marp 极速排版引擎", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚀 Marp-Autosplitter 可视化控制台 Console")
    gr.Markdown("上传 Markdown 文档，调整参数，一键生成排版完美的 PPTX。 Upload your Markdown file, tweak settings, and generate perfectly paginated PPTX with one click.")
    
    with gr.Row():
        with gr.Column():
            file_in = gr.File(label="1. 上传 Markdown 文件 (.md)", file_types=[".md"])
            theme_in = gr.Dropdown(
                choices=["default", "gaia", "uncover", "academic", "rose-pine"], 
                value="default", 
                label="2. 选择主题皮肤 Choose Theme"
            )
            level_in = gr.Slider(minimum=1, maximum=4, value=2, step=1, label="3. 触发分页的最高标题层级 Heading Level to Trigger Pagination")
            format_in = gr.CheckboxGroup(choices=["pptx", "pdf", "html"], value=["pptx", "pdf"], label="4. 输出格式 Output Formats")
            submit_btn = gr.Button("⚡ 开始生成 PPT ", variant="primary")
            
        with gr.Column():
            output_msg = gr.Textbox(label="运行状态 status", interactive=False)
            file_out = gr.File(label="5. 下载生成的演示文稿 Download Generated Presentation", interactive=False)

    submit_btn.click(
        fn=generate_ppt,
        inputs=[file_in, theme_in, level_in, format_in],
        outputs=[file_out, output_msg]
    )
if __name__ == "__main__":

    demo.launch(inbrowser=True, server_port=7860, prevent_thread_lock=False)