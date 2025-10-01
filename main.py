"""Gmail監視ビープアプリケーション - エントリーポイント"""
import argparse
import sys
import tkinter as tk
from ui import MailBeepApp
from utils import setup_logging
from cli import main as cli_main


def run_gui():
    """GUIモードでアプリケーションを起動"""
    setup_logging()
    
    root = tk.Tk()
    app = MailBeepApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


def main():
    """アプリケーションのエントリーポイント"""
    # 引数が無い、または最初の引数がguiの場合はGUIモード
    if len(sys.argv) == 1 or (len(sys.argv) >= 2 and sys.argv[1] == 'gui'):
        # GUI引数があれば削除
        if len(sys.argv) >= 2 and sys.argv[1] == 'gui':
            sys.argv.pop(1)
        run_gui()
        return
    
    # 最初の引数がcliの場合はCLIモード
    if sys.argv[1] == 'cli':
        # 'cli'引数を削除してcli_mainに渡す
        sys.argv.pop(1)
        cli_main()
        return
    
    # それ以外の場合はヘルプを表示
    parser = argparse.ArgumentParser(
        description='Gmail監視ビープアプリケーション',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
モード:
  cli    - コマンドラインインターフェース（CUI）で起動
  gui    - グラフィカルユーザーインターフェース（GUI）で起動（デフォルト）

使用例:
  # GUIモードで起動（デフォルト）
  %(prog)s
  %(prog)s gui

  # CLIモードで起動
  %(prog)s cli

  # CLIモードで追加オプションを指定
  %(prog)s cli --config /path/to/config.ini --debug
        """
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        choices=['cli', 'gui'],
        default='gui',
        help='起動モード: cli または gui（デフォルト: gui）'
    )
    
    parser.parse_args()


if __name__ == "__main__":
    main()
