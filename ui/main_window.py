"""メイン画面モジュール"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging

from config_manager import ConfigManager
from gmail_monitor import GmailMonitor
from utils import play_beep
from .settings_window import SettingsWindow

logger = logging.getLogger(__name__)


class MailBeepApp:
    """メインアプリケーションクラス"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gmail監視ビープアプリ")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        # 設定管理
        self.config_manager = ConfigManager()
        
        # Gmail監視
        self.gmail_monitor = GmailMonitor(self.config_manager)
        
        # 監視状態
        self.is_monitoring = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.beep_count = 0
        
        # GUI作成
        self._create_widgets()
        
        # 初回起動時に設定画面を開く
        self.root.after(100, self._check_initial_config)
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="Gmail監視ビープアプリ", font=('', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # ステータス表示
        self.status_label = ttk.Label(main_frame, text="ステータス: 停止中", font=('', 12))
        self.status_label.pack(pady=10)
        
        # ビープ回数表示
        self.count_label = ttk.Label(main_frame, text="ビープ回数: 0回", font=('', 12))
        self.count_label.pack(pady=10)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # 開始/停止ボタン
        self.start_stop_button = ttk.Button(button_frame, text="開始", command=self._toggle_monitoring, width=15)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)
        
        # 設定ボタン
        ttk.Button(button_frame, text="設定", command=self._open_settings, width=15).pack(side=tk.LEFT, padx=5)
    
    def _check_initial_config(self):
        """初回設定チェック"""
        if not self.config_manager.is_configured():
            messagebox.showinfo("初回設定", "最初に設定を行ってください")
            self._open_settings()
    
    def _open_settings(self):
        """設定画面を開く"""
        # 監視中の場合は停止
        if self.is_monitoring:
            messagebox.showwarning("警告", "監視を停止してから設定を変更してください")
            return
        
        SettingsWindow(self.root, self.config_manager, on_save=self._on_settings_saved)
    
    def _on_settings_saved(self):
        """設定保存後の処理"""
        # 必要に応じて処理を追加
        pass
    
    def _toggle_monitoring(self):
        """監視の開始/停止を切り替え"""
        if self.is_monitoring:
            self._stop_monitoring()
        else:
            self._start_monitoring()
    
    def _start_monitoring(self):
        """監視を開始"""
        logger.info("監視開始を試行中...")
        
        # 設定チェック
        if not self.config_manager.is_configured():
            logger.warning("設定が未完了です")
            messagebox.showerror("エラー", "先に設定を行ってください")
            return
        
        # 接続テスト
        try:
            logger.info("接続テスト開始")
            self.gmail_monitor.connect()
            self.gmail_monitor.disconnect()
            logger.info("接続テスト成功")
        except Exception as e:
            logger.error(f"接続テスト失敗: {e}")
            messagebox.showerror("接続エラー", str(e))
            return
        
        # 監視開始
        self.is_monitoring = True
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("監視を開始しました")
        
        # UI更新
        self.start_stop_button.config(text="停止")
        self.status_label.config(text="ステータス: 監視中")
    
    def _stop_monitoring(self):
        """監視を停止"""
        logger.info("監視を停止しています...")
        self.is_monitoring = False
        self.stop_event.set()
        
        # UI更新
        self.start_stop_button.config(text="開始")
        self.status_label.config(text="ステータス: 停止中")
        logger.info("監視を停止しました")
    
    def _monitor_loop(self):
        """監視ループ（別スレッドで実行）"""
        check_interval = int(self.config_manager.get('Monitor', 'check_interval', '60'))
        time_window_minutes = int(self.config_manager.get('Monitor', 'time_window_minutes', '2'))
        logger.info(f"監視ループ開始 (チェック間隔: {check_interval}秒, 時間範囲: {time_window_minutes}分)")
        
        while not self.stop_event.is_set():
            try:
                logger.info("=" * 50)
                logger.info("新しい監視サイクル開始")
                
                # Gmail接続
                self.gmail_monitor.connect()
                
                # メールチェック（時間範囲を指定）
                if self.gmail_monitor.check_new_mail(time_window_minutes=time_window_minutes):
                    # 条件に合致するメールあり
                    logger.info("条件に合致するメールが見つかりました！ビープ音を再生します")
                    # 設定からビープ音の秒数を取得
                    beep_duration = float(self.config_manager.get('Sound', 'beep_duration', '10'))
                    play_beep(duration=beep_duration)
                    self.beep_count += 1
                    self._update_count_label()
                    logger.info(f"ビープ回数: {self.beep_count}")
                
                # 切断
                self.gmail_monitor.disconnect()
                
                logger.info(f"次のチェックまで {check_interval}秒 待機します")
                
            except Exception as e:
                logger.error(f"監視エラー: {e}")
                # エラーが発生してもループを継続
            
            # 指定間隔待機（中断可能）
            self.stop_event.wait(check_interval)
        
        logger.info("監視ループを終了しました")
    
    def _update_count_label(self):
        """ビープ回数ラベルを更新"""
        # メインスレッドで実行
        self.root.after(0, lambda: self.count_label.config(text=f"ビープ回数: {self.beep_count}回"))
    
    def on_closing(self):
        """アプリ終了時の処理"""
        if self.is_monitoring:
            self._stop_monitoring()
        self.gmail_monitor.disconnect()
        self.root.destroy()


