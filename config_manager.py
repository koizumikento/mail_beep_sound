"""設定ファイル（config.ini）の管理モジュール"""
import configparser
import os


class ConfigManager:
    """設定ファイル（config.ini）の管理クラス"""
    
    def __init__(self, config_path="config.ini"):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load_or_create()
    
    def load_or_create(self):
        """設定ファイルの読み込み、存在しない場合はデフォルト値で作成"""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path, encoding='utf-8')
        else:
            # デフォルト設定を作成
            self.config['Gmail'] = {
                'email': '',
                'password': ''
            }
            self.config['Monitor'] = {
                'check_interval': '60',
                'time_window_minutes': '2',
                'sender_filter': '',
                'keyword_filter': ''
            }
            self.config['Sound'] = {
                'beep_duration': '10'
            }
            self.save()
    
    def save(self):
        """設定ファイルを保存"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get(self, section, key, fallback=''):
        """設定値を取得"""
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        """設定値を設定"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
    
    def is_configured(self):
        """最低限の設定がされているか確認"""
        email_addr = self.get('Gmail', 'email')
        password = self.get('Gmail', 'password')
        return bool(email_addr and password)

