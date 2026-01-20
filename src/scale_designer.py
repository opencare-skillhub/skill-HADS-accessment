"""
量表设计 Agent
结合 LLM 提示词生成标准化量表，包括问题、评分标准和表单内容
"""

import os
from src.utils.logger import logger

class ScaleDesigner:
    """量表设计 Agent"""
    
    def __init__(self):
        self.template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'templates'
        )
        os.makedirs(self.template_dir, exist_ok=True)

    def generate_scale_definition(self, description: str) -> str:
        """
        根据描述生成量表设计的 LLM 提示词
        
        Args:
            description: 量表需求描述（如：设计一个评估化疗后疲劳度的量表）
        
        Returns:
            优化后的 LLM 提示词
        """
        logger.info(f"正在为需求生成量表设计提示词: {description}")
        
        prompt = f"""
请作为一个专业的临床心理测量专家，根据以下需求设计一个标准化量表：
需求：{description}

要求输出以下结构化内容：
1. 量表名称与简介
2. 评估维度（如：躯体疲劳、心理疲劳）
3. 具体题目（建议 5-15 题，交替排列维度）
4. 评分选项（如：0-3 分，李克特量表格式）
5. 临床解读标准（如：0-7 分正常，8-10 分边缘...）
6. 对应的 HTML 表单代码片段（遵循 HADS 模板样式）

请确保量表具有临床严谨性，语义清晰，选项无歧义。
"""
        return prompt

    def save_design_result(self, scale_name: str, html_content: str):
        """保存生成的量表 HTML 到模板目录"""
        file_path = os.path.join(self.template_dir, f"{scale_name}_questionnaire.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"量表模板已保存: {file_path}")
        return file_path

if __name__ == '__main__':
    # 示例用法
    designer = ScaleDesigner()
    test_prompt = designer.generate_scale_definition("乳腺癌术后身体形象自评量表")
    print("--- 建议的 LLM 提示词 ---")
    print(test_prompt)
