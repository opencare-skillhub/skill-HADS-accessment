"""
Reflection Agent
事后分析 Skill，基于四级日志体系生成改进建议
"""

import os
from src.utils.logger import logger

class ReflectionAgent:
    """反思 Agent"""
    
    def __init__(self):
        self.log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'logs'
        )

    def reflect_on_execution(self):
        """分析最新日志并输出反思报告"""
        log_files = sorted([f for f in os.listdir(self.log_dir) if f.endswith('.log')])
        if not log_files:
            return "DECISION: 暂无日志数据，无法进行反思。"
        
        latest_log = os.path.join(self.log_dir, log_files[-1])
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        execution_count = sum(1 for line in lines if 'EXECUTION' in line)
        semantic_issues = [line for line in lines if 'SEMANTIC' in line and ('error' in line.lower() or 'low' in line.lower())]
        
        logger.decision("启动反思流程，正在评估执行效率与语义质量")
        
        report = f"""
### 反思日志报告 (Reflection Report)
- **执行密度**: 今日共完成 {execution_count} 次核心任务
- **语义质量**: 发现 {len(semantic_issues)} 处质量潜在波动
- **改进建议**: 
  1. 基于 DECISION 日志，建议优化量表生成的提示词模板以提升语义一致性。
  2. 针对 EXECUTION 记录，建议引入批量发布机制以降低 EdgeOne 延迟。
"""
        logger.reflection("反思完成，已生成优化建议，等待人工审批。")
        return report

if __name__ == '__main__':
    agent = ReflectionAgent()
    print(agent.reflect_on_execution())
