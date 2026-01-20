#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态 HTML 内容生成器
功能：基于主题生成治愈系静态页面，集成 Bilibili 精选视频
"""

import os
import argparse
from datetime import datetime
from pathlib import Path

# 导入日志系统
try:
    from utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)


class ContentGenerator:
    """内容生成器：生成主题化的静态 HTML 页面"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.output_dir = self.workspace / "deployed" / "content"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载提示词模板
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """从设计文档加载 HTML 生成提示词"""
        template_path = self.workspace / "design" / "html_提示词.md"
        
        if not template_path.exists():
            logger.semantic("提示词模板文件不存在，使用内置默认模板")
            return self._get_default_prompt()
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.execution(f"成功加载提示词模板：{template_path}")
            return content
        except Exception as e:
            logger.semantic(f"读取提示词模板失败：{e}，使用默认模板")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """获取内置默认提示词（紫色系治愈风格）"""
        return """
用原生 HTML/CSS/JS 生成"{theme}"主题页面，紫色系治愈风格。
整体玻璃磨砂效果：背景径向渐变、卡片圆角 14px、半透明 + backdrop-filter: blur(16px)。
左侧粘性目录（H2/H3 锚点，滚动高亮），暗色模式支持（prefers-color-scheme）。
≤980px 时目录上移单列布局。
输出单一 HTML 文件，内联 CSS/JS，CSS 变量管理主题色。

**视频嵌入**：搜索与"{theme}"相关的 Bilibili 精选视频（2-3个），
使用 Bilibili 标准 iframe 框架嵌入：
<iframe src="//player.bilibili.com/player.html?bvid=BV1xxxxxxxx&page=1&high_quality=1" 
        scrolling="no" border="0" frameborder="no" framespacing="0" 
        allowfullscreen="true" style="width:100%; height:500px; border-radius:12px;">
</iframe>
视频卡片继承页面配色，移动端响应式（280px 高度），支持延迟加载，每个视频带标题与简介。
"""
    
    def generate_html_prompt(self, theme: str, patient_id: str = None) -> str:
        """
        生成用于 LLM 的完整提示词
        
        Args:
            theme: 内容主题（如"正念与放松训练"、"营养管理指南"）
            patient_id: 患者 ID（可选，用于个性化）
        
        Returns:
            完整的 HTML 生成提示词
        """
        logger.decision(f"正在为主题 '{theme}' 生成 HTML 提示词")
        
        # 基础提示词
        base_prompt = self._get_default_prompt().format(theme=theme)
        
        # 如果有患者 ID，增加个性化说明
        if patient_id:
            base_prompt += f"\n\n**个性化要求**：在页面顶部 hero 区域标注「为患者 {patient_id} 定制」。"
        
        # 增加视频搜索指令
        video_search_instruction = f"""

**视频搜索任务**：
1. 使用 search_web 工具搜索关键词："{theme} 教学视频 site:bilibili.com"
2. 从搜索结果中提取 2-3 个高质量视频的 BV 号（如 BV1Ab4y1X7zz）
3. 构建 iframe 代码并嵌入页面"精选视频"章节
4. 为每个视频添加标题与 50 字简介

**示例 BV 号提取规则**：
- URL: https://www.bilibili.com/video/BV1Ab4y1X7zz/ → BV 号: BV1Ab4y1X7zz
- URL: https://b23.tv/BV1Ab4y1X7zz → BV 号: BV1Ab4y1X7zz
"""
        
        full_prompt = base_prompt + video_search_instruction
        
        logger.semantic(f"提示词生成完成，总长度：{len(full_prompt)} 字符")
        return full_prompt
    
    def save_html(self, html_content: str, theme: str, patient_id: str = None) -> Path:
        """
        保存生成的 HTML 文件
        
        Args:
            html_content: HTML 内容
            theme: 主题名称
            patient_id: 患者 ID（可选）
        
        Returns:
            保存的文件路径
        """
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        theme_slug = theme.replace(" ", "-").replace("与", "").lower()
        
        if patient_id:
            filename = f"{theme_slug}_{patient_id}_{timestamp}.html"
        else:
            filename = f"{theme_slug}_{timestamp}.html"
        
        output_path = self.output_dir / filename
        
        # 写入文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.execution(f"HTML 文件已保存：{output_path}")
            logger.semantic(f"文件大小：{len(html_content)} 字节")
            
            return output_path
        except Exception as e:
            logger.semantic(f"保存 HTML 文件失败：{e}")
            raise
    
    def generate_content_metadata(self, theme: str, output_path: Path, patient_id: str = None) -> dict:
        """
        生成内容元数据（用于与其他 Skill 集成）
        
        Returns:
            元数据字典
        """
        metadata = {
            "skill": "content-generator",
            "version": "1.0.0",
            "theme": theme,
            "patient_id": patient_id,
            "generated_at": datetime.now().isoformat(),
            "file_path": str(output_path),
            "file_size_bytes": output_path.stat().st_size
        }
        
        logger.decision(f"内容元数据已生成：{metadata}")
        return metadata


def main():
    parser = argparse.ArgumentParser(description="生成主题化静态 HTML 内容页面")
    parser.add_argument("--theme", required=True, help="内容主题（如：正念与放松训练）")
    parser.add_argument("--patient-id", help="患者 ID（可选，用于个性化）")
    parser.add_argument("--output-prompt-only", action="store_true", 
                       help="仅输出提示词，不生成 HTML（用于手动调用 LLM）")
    
    args = parser.parse_args()
    
    logger.execution(f"[ContentGenerator] 启动内容生成器，主题：{args.theme}")
    
    generator = ContentGenerator()
    
    # 生成提示词
    prompt = generator.generate_html_prompt(args.theme, args.patient_id)
    
    if args.output_prompt_only:
        # 仅输出提示词模式
        print("\n" + "="*80)
        print("请将以下提示词复制给 LLM，生成 HTML 后使用 --html-content 参数保存：")
        print("="*80 + "\n")
        print(prompt)
        print("\n" + "="*80)
        logger.execution("提示词已输出到终端")
    else:
        # 自动模式（需要 LLM 集成）
        print("\n" + "="*80)
        print("📝 生成提示词已完成，请执行以下步骤：")
        print("="*80)
        print("\n1️⃣  将以下提示词复制给支持 Web 搜索的 LLM（如 Claude + MCP）：")
        print("-"*80)
        print(prompt)
        print("-"*80)
        print("\n2️⃣  LLM 生成 HTML 后，将内容保存为文件并运行：")
        print(f"   python src/content_generator.py --theme \"{args.theme}\" --save-html <生成的HTML文件路径>")
        print("\n3️⃣  或直接将 HTML 内容通过 EdgeOne MCP 发布到公网\n")
        
        logger.execution("等待 LLM 生成 HTML 内容...")


if __name__ == "__main__":
    main()
