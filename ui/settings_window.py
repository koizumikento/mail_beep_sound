"""設定画面モジュール"""
import tkinter as tk
from tkinter import ttk, messagebox


class SettingsWindow:
    """設定画面ウィンドウ"""
    
    def __init__(self, parent, config_manager, on_save=None):
        self.config_manager = config_manager
        self.on_save = on_save
        
        # トップレベルウィンドウを作成
        self.window = tk.Toplevel(parent)
        self.window.title("設定")
        self.window.geometry("500x480")
        self.window.resizable(False, False)
        
        # モーダルに設定
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        self._load_settings()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Gmail設定
        gmail_label = ttk.Label(main_frame, text="Gmail設定", font=('', 12, 'bold'))
        gmail_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(main_frame, text="メールアドレス:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(main_frame, width=40)
        self.email_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(main_frame, text="アプリパスワード:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=40, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
        
        # 監視設定
        monitor_label = ttk.Label(main_frame, text="監視設定", font=('', 12, 'bold'))
        monitor_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
        
        ttk.Label(main_frame, text="チェック間隔（秒）:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.interval_entry = ttk.Entry(main_frame, width=40)
        self.interval_entry.grid(row=4, column=1, pady=5)
        
        ttk.Label(main_frame, text="時間範囲（分）:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.time_window_entry = ttk.Entry(main_frame, width=40)
        self.time_window_entry.grid(row=5, column=1, pady=5)
        
        ttk.Label(main_frame, text="送信者フィルター:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.sender_entry = ttk.Entry(main_frame, width=40)
        self.sender_entry.grid(row=6, column=1, pady=5)
        
        ttk.Label(main_frame, text="キーワードフィルター:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.keyword_entry = ttk.Entry(main_frame, width=40)
        self.keyword_entry.grid(row=7, column=1, pady=5)
        
        # サウンド設定
        sound_label = ttk.Label(main_frame, text="サウンド設定", font=('', 12, 'bold'))
        sound_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
        
        ttk.Label(main_frame, text="ビープ音の秒数:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.beep_duration_entry = ttk.Entry(main_frame, width=40)
        self.beep_duration_entry.grid(row=9, column=1, pady=5)
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="保存", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="キャンセル", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
    def _load_settings(self):
        """現在の設定を読み込んで表示"""
        self.email_entry.insert(0, self.config_manager.get('Gmail', 'email'))
        self.password_entry.insert(0, self.config_manager.get('Gmail', 'password'))
        self.interval_entry.insert(0, self.config_manager.get('Monitor', 'check_interval'))
        self.time_window_entry.insert(0, self.config_manager.get('Monitor', 'time_window_minutes', '2'))
        self.sender_entry.insert(0, self.config_manager.get('Monitor', 'sender_filter'))
        self.keyword_entry.insert(0, self.config_manager.get('Monitor', 'keyword_filter'))
        self.beep_duration_entry.insert(0, self.config_manager.get('Sound', 'beep_duration', '10'))
    
    def _save(self):
        """設定を保存"""
        # バリデーション
        try:
            interval = int(self.interval_entry.get())
            if interval < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("エラー", "チェック間隔は1以上の整数を入力してください", parent=self.window)
            return
        
        try:
            time_window = int(self.time_window_entry.get())
            if time_window < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("エラー", "時間範囲は1以上の整数を入力してください", parent=self.window)
            return
        
        try:
            beep_duration = int(self.beep_duration_entry.get())
            if beep_duration < 1 or beep_duration > 60:
                raise ValueError
        except ValueError:
            messagebox.showerror("エラー", "ビープ音の秒数は1〜60の整数を入力してください", parent=self.window)
            return
        
        if not self.email_entry.get().strip():
            messagebox.showerror("エラー", "メールアドレスを入力してください", parent=self.window)
            return
        
        if not self.password_entry.get().strip():
            messagebox.showerror("エラー", "アプリパスワードを入力してください", parent=self.window)
            return
        
        # 設定を保存
        self.config_manager.set('Gmail', 'email', self.email_entry.get().strip())
        self.config_manager.set('Gmail', 'password', self.password_entry.get().strip())
        self.config_manager.set('Monitor', 'check_interval', str(interval))
        self.config_manager.set('Monitor', 'time_window_minutes', str(time_window))
        self.config_manager.set('Monitor', 'sender_filter', self.sender_entry.get().strip())
        self.config_manager.set('Monitor', 'keyword_filter', self.keyword_entry.get().strip())
        self.config_manager.set('Sound', 'beep_duration', str(beep_duration))
        self.config_manager.save()
        
        messagebox.showinfo("成功", "設定を保存しました", parent=self.window)
        
        if self.on_save:
            self.on_save()
        
        self.window.destroy()


