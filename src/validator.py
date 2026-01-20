"""
HADS 数据验证器
验证评估数据的完整性和有效性
"""

from typing import Dict, List, Tuple


class HADSValidator:
    """HADS 数据验证器"""
    
    @staticmethod
    def validate_scores(anxiety: int, depression: int) -> Tuple[bool, List[str]]:
        """
        验证评分有效性
        
        Args:
            anxiety: 焦虑评分
            depression: 抑郁评分
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # 验证评分范围
        if not (0 <= anxiety <= 21):
            errors.append(f"焦虑评分超出范围 (0-21): {anxiety}")
        
        if not (0 <= depression <= 21):
            errors.append(f"抑郁评分超出范围 (0-21): {depression}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_json_structure(data: Dict) -> Tuple[bool, List[str]]:
        """
        验证 JSON 数据结构
        
        Args:
            data: JSON 数据字典
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # 验证必需字段
        required_fields = ['hads']
        for field in required_fields:
            if field not in data:
                errors.append(f"缺少必需字段: {field}")
        
        # 验证 hads 字段结构
        if 'hads' in data:
            hads = data['hads']
            if not isinstance(hads, dict):
                errors.append("hads 字段必须是对象类型")
            else:
                if 'anxiety' not in hads:
                    errors.append("hads 对象缺少 anxiety 字段")
                if 'depression' not in hads:
                    errors.append("hads 对象缺少 depression 字段")
                
                # 验证评分值
                if 'anxiety' in hads and 'depression' in hads:
                    anxiety = hads.get('anxiety')
                    depression = hads.get('depression')
                    
                    if not isinstance(anxiety, int):
                        errors.append(f"anxiety 必须是整数: {type(anxiety)}")
                    if not isinstance(depression, int):
                        errors.append(f"depression 必须是整数: {type(depression)}")
                    
                    if isinstance(anxiety, int) and isinstance(depression, int):
                        is_valid, score_errors = HADSValidator.validate_scores(
                            anxiety, depression
                        )
                        errors.extend(score_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_patient_id(patient_id: str) -> str:
        """
        清理患者ID，移除不安全字符
        
        Args:
            patient_id: 原始患者ID
        
        Returns:
            清理后的患者ID
        """
        import re
        # 只保留字母、数字、下划线、连字符
        return re.sub(r'[^\w\-]', '', patient_id)


def main():
    """测试验证器"""
    validator = HADSValidator()
    
    # 测试用例
    test_cases = [
        {
            'name': '正常数据',
            'data': {
                'patient_id': 'P001',
                'hads': {'anxiety': 12, 'depression': 8}
            }
        },
        {
            'name': '评分超范围',
            'data': {
                'patient_id': 'P002',
                'hads': {'anxiety': 25, 'depression': -1}
            }
        },
        {
            'name': '缺少字段',
            'data': {
                'patient_id': 'P003',
                'hads': {'anxiety': 10}
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n测试: {test['name']}")
        is_valid, errors = validator.validate_json_structure(test['data'])
        if is_valid:
            print("✓ 验证通过")
        else:
            print("✗ 验证失败:")
            for error in errors:
                print(f"  - {error}")


if __name__ == '__main__':
    main()
