"""
HADS 问卷发布器
生成交互式 HTML 问卷并通过 EdgeOne MCP 发布
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict
from src.utils.logger import logger


class HADSPublisher:
    """HADS 问卷发布器"""
    
    def __init__(self):
        self.template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'templates',
            'hads_questionnaire.html'
        )
        self.deployed_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'deployed',
            'questionnaires'
        )
        os.makedirs(self.deployed_dir, exist_ok=True)
    
    def generate_questionnaire(
        self,
        patient_id: Optional[str] = None,
        save_local: bool = True
    ) -> Dict:
        """
        生成 HADS 问卷 HTML
        
        Args:
            patient_id: 患者ID（可选）
            save_local: 是否保存本地副本
        
        Returns:
            {
                'html_content': str,
                'local_path': str,
                'patient_id': str,
                'instruction': str
            }
        """
        # 读取模板
        if not os.path.exists(self.template_path):
            return {
                'success': False,
                'error': f'模板文件不存在: {self.template_path}'
            }
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        logger.info(f"正在为患者 {patient_id} 生成问卷")
        patient_id = patient_id or '未指定'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        result = {
            'success': True,
            'html_content': html_content,
            'patient_id': patient_id,
            'generated_at': datetime.now().isoformat()
        }
        
        # 保存本地副本
        if save_local:
            filename = f'hads_{patient_id}_{timestamp}.html'
            filepath = os.path.join(self.deployed_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"问卷本地副本已保存: {filepath}")
            result['local_path'] = os.path.abspath(filepath)
            print(f"✓ 问卷已生成: {filepath}")
        
        # 添加发布指令
        result['instruction'] = (
            f"\n{'='*60}\n"
            f"📋 下一步：使用 AI Agent 发布问卷\n"
            f"{'='*60}\n"
            f"请在 AI 对话中执行：\n"
            f"  用 EdgeOne MCP 发布 {result.get('local_path', '')}\n\n"
            f"发布后将获得公网链接，格式如：\n"
            f"  https://mcp.edgeone.site/share/xxxxx?patient_id={patient_id}\n"
            f"{'='*60}\n"
        )
        
        return result


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='HADS 问卷发布器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python src/publisher.py --patient-id P001
  python src/publisher.py --patient-id P002 --no-save
        """
    )
    
    parser.add_argument(
        '--patient-id',
        type=str,
        default=None,
        help='患者ID（可选，如：P001）'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='不保存本地副本'
    )
    
    args = parser.parse_args()
    
    # 创建发布器
    publisher = HADSPublisher()
    
    # 生成问卷
    result = publisher.generate_questionnaire(
        patient_id=args.patient_id,
        save_local=not args.no_save
    )
    
    if not result.get('success'):
        print(f"❌ 错误: {result.get('error')}")
        sys.exit(1)
    
    # 输出结果
    print(f"\n患者ID: {result['patient_id']}")
    print(f"生成时间: {result['generated_at']}")
    
    if 'local_path' in result:
        print(f"本地路径: {result['local_path']}")
    
    print(result['instruction'])


if __name__ == '__main__':
    main()
