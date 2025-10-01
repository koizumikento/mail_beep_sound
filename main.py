"""Gmail監視ビープアプリケーション - エントリーポイント"""
import tkinter as tk
from ui import MailBeepApp
from utils import setup_logging


def main():
    """アプリケーションのエントリーポイント"""
    # ロギング設定を初期化
    setup_logging()
    
    root = tk.Tk()
    app = MailBeepApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
