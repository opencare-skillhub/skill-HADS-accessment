"""
Interpretation Agent
基于 LLM 提示词生成专业的量表结果解读与临床干预建议
"""

import os
import json
from src.utils.logger import logger

class InterpretationAgent:
    """解读与干预 Agent"""
    
    def __init__(self):
        pass

    def generate_interpretation_prompt(self, result_data: dict) -> str:
        """
        根据量表结果生成 LLM 解读提示词
        
        Args:
            result_data: 包含评分、题目答案及患者基本信息的 JSON 数据
        
        Returns:
            优化后的 LLM 提示词
        """
        patient_id = result_data.get('patient_id', '未知')
        hads_data = result_data.get('hads', {})
        anxiety = hads_data.get('anxiety', 0)
        depression = hads_data.get('depression', 0)
        
        logger.decision(f"正在为患者 {patient_id} 生成智能解读提示词")
        
        prompt = f"""
请作为一个专业的心理肿瘤学（Psycho-Oncology）专家，对以下 HADS 量表评估结果进行深度解读，并提供个性化的干预建议。

### 患者基本信息
- 患者 ID: {patient_id}
- 评估工具: 医院焦虑抑郁量表 (HADS)

### 评分数据
- 焦虑评分 (HADS-A): {anxiety} 分
- 抑郁评分 (HADS-D): {depression} 分
- 评分参考: 0-7正常，8-10边缘异常，11-21异常

### 任务要求
1. **深度解读**: 结合焦虑和抑郁两个维度，分析患者当前的心理痛苦（Distress）状态及其对治疗依从性的潜在影响。
2. **风险评估**: 识别是否存在高风险情绪波动，并给出临床警示。
3. **干预建议**: 
   - **心理层面**: 建议具体的心理疏导方法（如正念、认知重构等）。
   - **生活层面**: 提供饮食、睡眠或社交支持方面的建议。
   - **医疗建议**: 明确是否需要转介精神科或心理咨询。
4. **语气规范**: 请使用专业、温和、富有同理心的语言，适合志愿者或家属阅读。

请确保输出结构清晰，建议具体且具备可操作性。
"""
        logger.semantic(f"提示词生成完成，覆盖焦虑({anxiety})与抑郁({depression})维度")
        return prompt

if __name__ == '__main__':
    # 示例测试
    sample_data = {
        "patient_id": "BC001",
        "hads": {"anxiety": 12, "depression": 9}
    }
    agent = InterpretationAgent()
    print(agent.generate_interpretation_prompt(sample_data))
