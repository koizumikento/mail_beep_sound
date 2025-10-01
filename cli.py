"""Gmail監視ビープアプリケーション - CLIエントリーポイント"""
import argparse
import sys
import time
import signal
import logging
import threading
from pathlib import Path

from config_manager import ConfigManager
from gmail_monitor import GmailMonitor
from utils import play_beep, setup_logging

logger = logging.getLogger(__name__)

# 終了フラグ
should_stop = False


def signal_handler(signum, frame):
    """シグナルハンドラー（Ctrl+Cなど）"""
    global should_stop
    logger.info("終了シグナルを受信しました。監視を停止します...")
    should_stop = True


def wait_for_user_input():
    """ユーザー入力を待機するスレッド"""
    global should_stop
    try:
        input()  # Enterキーまたは任意の入力を待つ
        logger.info("ユーザー入力を検知しました。監視を停止します...")
        should_stop = True
    except Exception:
        # 入力エラーが発生しても無視
        pass


def main():
    """CLIアプリケーションのエントリーポイント"""
    parser = argparse.ArgumentParser(
        description='Gmail監視ビープアプリ（CLI版）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # デフォルト設定で起動（Enter または 'q' + Enter で停止）
  %(prog)s

  # カスタム設定ファイルを使用
  %(prog)s --config /path/to/config.ini

  # デバッグモードで起動
  %(prog)s --debug

  # 設定を指定して起動
  %(prog)s --email user@gmail.com --password 'app-password' --interval 30

停止方法:
  - Enter キーを押す（推奨）
  - 'q' + Enter を押す
  - Ctrl+C を押す
        """
    )
    
    parser.add_argument(
        '--config',
        default='config.ini',
        help='設定ファイルのパス（デフォルト: config.ini）'
    )
    parser.add_argument(
        '--email',
        help='Gmailアドレス（設定ファイルより優先）'
    )
    parser.add_argument(
        '--password',
        help='Gmailアプリパスワード（設定ファイルより優先）'
    )
    parser.add_argument(
        '--interval',
        type=int,
        help='メールチェック間隔（秒）（設定ファイルより優先）'
    )
    parser.add_argument(
        '--time-window',
        type=int,
        help='受信時刻の範囲（分）（設定ファイルより優先）'
    )
    parser.add_argument(
        '--sender-filter',
        help='送信者フィルター（設定ファイルより優先）'
    )
    parser.add_argument(
        '--keyword-filter',
        help='キーワードフィルター（設定ファイルより優先）'
    )
    parser.add_argument(
        '--beep-duration',
        type=float,
        help='ビープ音の秒数（設定ファイルより優先）'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='デバッグモードで実行'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='一度だけチェックして終了（テスト用）'
    )
    
    args = parser.parse_args()
    
    # ロギング設定
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=log_level)
    
    logger.info("=" * 60)
    logger.info("Gmail監視ビープアプリ（CLI版）")
    logger.info("=" * 60)
    
    # 設定ファイルを読み込み
    config_path = Path(args.config)
    if not config_path.exists() and (not args.email or not args.password):
        logger.error(f"設定ファイル '{config_path}' が見つかりません")
        logger.error("設定ファイルを作成するか、--email と --password を指定してください")
        sys.exit(1)
    
    config_manager = ConfigManager(str(config_path))
    
    # コマンドライン引数で設定を上書き
    if args.email:
        config_manager.set('Gmail', 'email', args.email)
    if args.password:
        config_manager.set('Gmail', 'password', args.password)
    if args.interval:
        config_manager.set('Monitor', 'check_interval', str(args.interval))
    if args.time_window:
        config_manager.set('Monitor', 'time_window_minutes', str(args.time_window))
    if args.sender_filter is not None:
        config_manager.set('Monitor', 'sender_filter', args.sender_filter)
    if args.keyword_filter is not None:
        config_manager.set('Monitor', 'keyword_filter', args.keyword_filter)
    if args.beep_duration:
        config_manager.set('Sound', 'beep_duration', str(args.beep_duration))
    
    # 最低限の設定チェック
    if not config_manager.is_configured():
        logger.error("Gmail設定が不足しています")
        logger.error("--email と --password を指定するか、config.ini を設定してください")
        sys.exit(1)
    
    # 設定を表示
    email = config_manager.get('Gmail', 'email')
    check_interval = int(config_manager.get('Monitor', 'check_interval', '60'))
    time_window_minutes = int(config_manager.get('Monitor', 'time_window_minutes', '2'))
    sender_filter = config_manager.get('Monitor', 'sender_filter')
    keyword_filter = config_manager.get('Monitor', 'keyword_filter')
    beep_duration = float(config_manager.get('Sound', 'beep_duration', '10'))
    
    logger.info(f"Gmailアドレス: {email}")
    logger.info(f"チェック間隔: {check_interval}秒")
    logger.info(f"時間範囲: {time_window_minutes}分")
    logger.info(f"送信者フィルター: {sender_filter if sender_filter else '(なし)'}")
    logger.info(f"キーワードフィルター: {keyword_filter if keyword_filter else '(なし)'}")
    logger.info(f"ビープ音の秒数: {beep_duration}秒")
    logger.info("")
    
    # Gmail監視インスタンスを作成
    gmail_monitor = GmailMonitor(config_manager)
    
    # 接続テスト
    logger.info("Gmailへの接続をテスト中...")
    try:
        gmail_monitor.connect()
        gmail_monitor.disconnect()
        logger.info("接続テスト成功")
    except Exception as e:
        logger.error(f"接続テストに失敗しました: {e}")
        sys.exit(1)
    
    # シグナルハンドラーを設定
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # ユーザー入力待機スレッドを開始（--onceモードでは不要）
    if not args.once:
        input_thread = threading.Thread(target=wait_for_user_input, daemon=True)
        input_thread.start()
    
    # 監視ループ
    logger.info("")
    if args.once:
        logger.info("監視を開始します（1回のみチェック）")
    else:
        logger.info("監視を開始します（停止: Ctrl+C または Enter/qキー）")
        print("\n[停止するには Enter キーまたは 'q' + Enter を押してください]\n", flush=True)
    logger.info("=" * 60)
    
    beep_count = 0
    
    try:
        while not should_stop:
            try:
                logger.info("")
                logger.info("=" * 60)
                logger.info("新しい監視サイクル開始")
                
                # Gmail接続
                gmail_monitor.connect()
                
                # メールチェック
                if gmail_monitor.check_new_mail(time_window_minutes=time_window_minutes):
                    # 条件に合致するメールあり
                    logger.info("条件に合致するメールが見つかりました！警告音を再生します")
                    play_beep(duration=beep_duration)
                    beep_count += 1
                    logger.info(f"✓ ビープ回数: {beep_count}")
                else:
                    logger.info("条件に合致するメールはありませんでした")
                
                # 切断
                gmail_monitor.disconnect()
                
                # 一度だけチェックモードの場合は終了
                if args.once:
                    logger.info("--once モードのため、終了します")
                    break
                
                logger.info(f"次のチェックまで {check_interval}秒 待機します")
                logger.info("=" * 60)
                
                # 待機（Ctrl+Cで中断可能）
                for _ in range(check_interval):
                    if should_stop:
                        break
                    time.sleep(1)
                
            except Exception as e:
                logger.error(f"監視エラー: {e}")
                logger.info("エラーが発生しましたが、監視を継続します")
                
                # エラー後は短い待機時間
                if not args.once:
                    time.sleep(10)
    
    finally:
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"監視を終了しました（合計ビープ回数: {beep_count}）")
        logger.info("=" * 60)
        gmail_monitor.disconnect()


if __name__ == "__main__":
    main()

