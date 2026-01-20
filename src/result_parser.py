"""
HADS 评估结果解析器
解析患者提交的评估结果并生成解读报告
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List
from src.utils.logger import logger
from src.agents.interpretation_agent import InterpretationAgent


class HADSResultParser:
    """HADS 结果解析器"""
    
    def __init__(self):
        self.results_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'results',
            'json'
        )
        os.makedirs(self.results_dir, exist_ok=True)
        self.interpretation_agent = InterpretationAgent()
    
    def parse_json(self, json_file: str) -> Dict:
        """
        解析 JSON 结果文件
        
        Args:
            json_file: JSON 文件路径
        
        Returns:
            解析后的结构化数据
        """
        logger.info(f"正在解析结果文件: {json_file}")
        if not os.path.exists(json_file):
            return {'success': False, 'error': f'文件不存在: {json_file}'}
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证数据结构
            if 'hads' not in data:
                return {'success': False, 'error': '无效的 HADS 数据格式'}
            
            hads = data.get('hads', {})
            anxiety = hads.get('anxiety', 0)
            depression = hads.get('depression', 0)
            
            # 评估级别
            result = {
                'success': True,
                'patient_id': data.get('patient_id', '未知'),
                'assessment_date': data.get('assessment_date'),
                'scores': {
                    'anxiety': anxiety,
                    'depression': depression
                },
                'levels': {
                    'anxiety': self._evaluate_level(anxiety),
                    'depression': self._evaluate_level(depression)
                },
                'interpretation': self._generate_interpretation(anxiety, depression),
                'recommendations': self._generate_recommendations(anxiety, depression)
            }
            
            # 生成智能解读提示词
            llm_prompt = self.interpretation_agent.generate_interpretation_prompt(data)
            result['llm_prompt'] = llm_prompt
            
            logger.info(f"成功解析患者 {result['patient_id']} 的评估数据，并生成了智能解读提示词")
            return result
            
        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'JSON 解析失败: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'处理失败: {str(e)}'}
    
    def _evaluate_level(self, score: int) -> Dict:
        """评估单项得分级别"""
        if score <= 7:
            return {
                'level': 'normal',
                'text': '正常',
                'description': '在正常范围内'
            }
        elif score <= 10:
            return {
                'level': 'borderline',
                'text': '边缘异常',
                'description': '需要关注，建议定期复评'
            }
        else:
            return {
                'level': 'abnormal',
                'text': '异常',
                'description': '建议寻求专业心理咨询或治疗'
            }
    
    def _generate_interpretation(self, anxiety: int, depression: int) -> str:
        """生成综合解读"""
        lines = []
        
        if anxiety >= 11 or depression >= 11:
            lines.append("⚠️ 评估结果显示存在明显的焦虑或抑郁症状。")
            lines.append("强烈建议尽快联系心理肿瘤科或精神科医生进行专业评估。")
        elif anxiety >= 8 or depression >= 8:
            lines.append("⚠️ 评估结果显示存在边缘性焦虑或抑郁倾向。")
            lines.append("建议安排心理咨询，并在 2-4 周后复评。")
        else:
            lines.append("✓ 心理状态在正常范围内。")
            lines.append("建议继续保持良好的生活方式和社会支持。")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self, anxiety: int, depression: int) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        
        # 高风险建议
        if anxiety >= 11 or depression >= 11:
            recommendations.extend([
                "立即联系心理肿瘤科或精神科医生",
                "考虑药物治疗（抗焦虑/抗抑郁药物）结合心理咨询",
                "建议由家属陪同就诊，避免独处",
                "告知主治医生，纳入综合治疗计划"
            ])
        
        # 中风险建议
        elif anxiety >= 8 or depression >= 8:
            recommendations.extend([
                "安排专业心理咨询评估",
                "尝试放松训练、正念冥想等自助方法",
                "2-4 周后复评，关注情绪变化趋势",
                "加强社会支持系统"
            ])
        
        # 低风险建议
        else:
            recommendations.extend([
                "继续保持良好的心理状态",
                "定期（每月）自我评估，预防性关注",
                "保持健康生活方式和社会活动",
                "如有情绪波动，及时与医护人员沟通"
            ])
        
        # 通用建议
        recommendations.extend([
            "加入患者支持小组，分享经验和情感支持",
            "将评估结果告知主治医生",
            "关注小馨宝助手公众号获取更多心理支持资源"
        ])
        
        return recommendations
    
    def format_report(self, parsed_data: Dict) -> str:
        """格式化为可读报告"""
        if not parsed_data.get('success'):
            return f"❌ 错误: {parsed_data.get('error')}"
        
        lines = [
            "\n" + "="*60,
            "�� HADS 心理评估结果报告",
            "="*60,
            f"患者ID: {parsed_data['patient_id']}",
            f"评估时间: {parsed_data.get('assessment_date', '未知')}",
            "",
            "【评分结果】",
            f"  焦虑评分: {parsed_data['scores']['anxiety']}/21 分 - {parsed_data['levels']['anxiety']['text']}",
            f"  抑郁评分: {parsed_data['scores']['depression']}/21 分 - {parsed_data['levels']['depression']['text']}",
            "",
            "【结果解读】",
            parsed_data['interpretation'],
            "",
            "【个性化建议】"
        ]
        
        for i, rec in enumerate(parsed_data['recommendations'], 1):
            lines.append(f"  {i}. {rec}")
        
        lines.extend([
            "",
            "="*60,
            "注意：本评估结果仅供参考，不能替代专业诊断。",
            "="*60
        ])
        
        return "\n".join(lines)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HADS 结果解析器')
    parser.add_argument('json_file', help='HADS 结果 JSON 文件路径')
    parser.add_argument(
        '--save-report',
        action='store_true',
        help='保存报告到 txt 文件'
    )
    
    args = parser.parse_args()
    
    # 解析结果
    parser_obj = HADSResultParser()
    result = parser_obj.parse_json(args.json_file)
    
    if not result.get('success'):
        print(f"❌ 错误: {result.get('error')}")
        sys.exit(1)
    
    # 生成报告
    report = parser_obj.format_report(result)
    print(report)
    
    # 保存报告
    if args.save_report:
        report_file = args.json_file.replace('.json', '_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✓ 报告已保存: {report_file}")


if __name__ == '__main__':
    main()
