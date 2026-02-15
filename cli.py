import os
import sys
import shutil
import asyncio
import argparse
import re
from engine import EngineSplitter

def find_browser_path():
    if sys.platform == "win32":
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        ]
    elif sys.platform == "darwin":
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        ]
    else:
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/microsoft-edge-stable",
            "/usr/bin/microsoft-edge"
        ]
        
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def find_marp_executable():
    local_marp_dir = os.path.abspath(os.path.join(os.getcwd(), "node_modules", ".bin"))
    local_marp = shutil.which("marp", path=local_marp_dir)
    if local_marp:
        return local_marp
    return shutil.which("marp")

async def convert_markdown(
    input_file: str, 
    theme: str, 
    style_class: str, 
    heading_split_levels: int,
    output_formats: list
):
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file '{input_file}' not found.")
        return

    marp_bin = find_marp_executable()
    if not marp_bin:
        print("❌ Error: Marp executable not found. Please run 'npm install @marp-team/marp-cli'")
        return
        
    browser_path = find_browser_path()
    if not browser_path:
        print("❌ Error: Chrome/Edge browser not found.")
        return

    env = os.environ.copy()
    env["CHROME_PATH"] = browser_path
    if sys.platform != "win32":
        env["PATH"] = "/usr/local/bin:/opt/homebrew/bin:" + env.get("PATH", "")

    # Read input file content
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"📄 Reading and cleaning document: {input_file} ...")
    final_content = content.strip()
    
    # Strip existing Frontmatter
    if final_content.startswith('---'):
        parts = final_content.split('---', 2)
        if len(parts) >= 3:
            final_content = parts[2].strip()

    # Clean: remove manual pagination, normalize formulas, clear extra blank lines, fix block sticking
    final_content = re.sub(r'^\s*---\s*$', '', final_content, flags=re.MULTILINE)
    final_content = re.sub(r'([^\n])\n( {0,3}#{1,6}\s)', r'\1\n\n\2', final_content)
    final_content = re.sub(r'\\\((.*?)\\\)', r'$\1$', final_content)
    final_content = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', final_content, flags=re.DOTALL)
    final_content = re.sub(r'\n{3,}', '\n\n', final_content).strip()

    print(f"🚀 Launching Two-Pass physical layout engine (Theme: {theme}, Split Level: H{heading_split_levels}) ...")
    splitter = EngineSplitter(slide_usable_height=620)
    final_content = await splitter.process(final_content, theme, marp_bin, env, heading_split_levels)

    # Assemble final Markdown
    header = f"---\nmarp: true\ntheme: {theme}\nclass: {style_class}\npaginate: true\n---\n\n"
    full_markdown = header + final_content

    base_dir = os.path.abspath(os.getcwd())
    output_dir = os.path.join(base_dir, "output_slides")
    os.makedirs(output_dir, exist_ok=True)
    
    file_base_name = os.path.splitext(os.path.basename(input_file))[0]
    md_file = os.path.join(output_dir, f"{file_base_name}_slide.md")
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(full_markdown)

    async def run_marp_async(output_path, format_name):
        print(f"⏳ Generating {format_name} ...")
        cmd = [marp_bin, md_file, "-o", output_path, "--allow-local-files"]
        themes_dir = os.path.join(base_dir, "themes")
        if os.path.exists(themes_dir):
            cmd.extend(["--theme-set", themes_dir])

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.DEVNULL,
                env=env
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
            if proc.returncode != 0:
                print(f"❌ Failed to generate {format_name}: {stderr.decode()}")
            else:
                print(f"✅ Successfully output: {output_path}")
        except asyncio.TimeoutError:
            print(f"❌ {format_name} generation timed out.")
        except Exception as e:
            print(f"❌ Error generating {format_name}: {str(e)}")

    for fmt in output_formats:
        out_path = os.path.join(output_dir, f"{file_base_name}.{fmt}")
        await run_marp_async(out_path, fmt.upper())

    print("All tasks completed successfully!")

def main():
    parser = argparse.ArgumentParser(description="Marp-Autosplitter: Blazing fast Markdown to perfectly paginated PPT")
    parser.add_argument("input", help="Path to the Markdown file to convert")
    parser.add_argument("-t", "--theme", default="default", help="Select theme (default: default)")
    parser.add_argument("-c", "--class_style", default="", help="Additional CSS class, e.g., lead or invert (default: none)")
    parser.add_argument("-l", "--level", type=int, default=2, help="trigger pagination on the top N actual heading levels (default: 2)")
    parser.add_argument("-f", "--format", nargs="+", choices=["pptx", "pdf", "html"], default=["pptx", "pdf"], help="Output formats (default: pptx pdf)")
    
    args = parser.parse_args()
    
    # Start async event loop
    asyncio.run(convert_markdown(args.input, args.theme, args.class_style, args.level, args.format))

if __name__ == "__main__":
    main()