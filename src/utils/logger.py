import os
import logging
from datetime import datetime

class SkillLogger:
    """强化版日志记录器，支持四级日志体系"""
    
    def __init__(self, name="skill-hads"):
        self.log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'logs'
        )
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            log_file = os.path.join(self.log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            # 使用统一前缀，但在消息中区分类型
            formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def execution(self, msg):
        """记录客观事实"""
        self.logger.info(f"EXECUTION: {msg}")

    def semantic(self, msg):
        """记录 LLM 自评质量"""
        self.logger.info(f"SEMANTIC: {msg}")

    def decision(self, msg):
        """记录选择逻辑"""
        self.logger.info(f"DECISION: {msg}")

    def reflection(self, msg):
        """记录改进建议"""
        self.logger.info(f"REFLECTION: {msg}")

    def info(self, msg):
        self.logger.info(f"INFO: {msg}")

    def error(self, msg):
        self.logger.error(msg)

# 全局单例
logger = SkillLogger()
