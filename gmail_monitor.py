"""Gmail監視機能モジュール"""
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


class GmailMonitor:
    """Gmail監視クラス"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.imap = None
        self.mailbox_selected = False
    
    def connect(self):
        """Gmailに接続"""
        email_addr = self.config_manager.get('Gmail', 'email')
        password = self.config_manager.get('Gmail', 'password')
        
        # アプリパスワードのスペースを削除
        password = password.replace(' ', '')
        
        try:
            logger.info(f"Gmailに接続中: {email_addr}")
            self.imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            self.imap.login(email_addr, password)
            logger.info("Gmail接続成功")
            return True
        except Exception as e:
            logger.error(f"Gmail接続エラー: {str(e)}")
            raise Exception(f"Gmail接続エラー: {str(e)}")
    
    def disconnect(self):
        """接続を切断"""
        if self.imap:
            try:
                logger.info("Gmail接続を切断中")
                # メールボックスを選択している場合のみclose()を呼ぶ
                if self.mailbox_selected:
                    self.imap.close()
                    self.mailbox_selected = False
                self.imap.logout()
                logger.info("Gmail接続を切断しました")
            except Exception as e:
                logger.warning(f"切断時にエラー: {str(e)}")
            self.imap = None
            self.mailbox_selected = False
    
    def check_new_mail(self, time_window_minutes=2):
        """未読メールをチェックし、条件に合致するメールがあるか確認
        
        Args:
            time_window_minutes: 何分以内に受信したメールを対象とするか（デフォルト: 2分）
        """
        try:
            logger.info("メールチェック開始")
            
            # INBOXを選択
            self.imap.select('INBOX')
            self.mailbox_selected = True
            
            # 現在時刻から time_window_minutes 分前の時刻を計算
            now = datetime.now(timezone.utc)
            time_threshold = now - timedelta(minutes=time_window_minutes)
            logger.info(f"受信時刻フィルター: {time_threshold.strftime('%Y-%m-%d %H:%M:%S UTC')} 以降")
            
            # 未読メールを検索（IMAPのSINCEは日付のみなので、後でDateヘッダーで厳密にチェック）
            # まずは今日の日付でフィルタリング
            search_date = time_threshold.strftime('%d-%b-%Y')
            status, messages = self.imap.search(None, f'UNSEEN SINCE {search_date}')
            if status != 'OK':
                logger.warning("未読メール検索が失敗しました")
                return False
            
            mail_ids = messages[0].split()
            logger.info(f"未読メール数（{search_date}以降）: {len(mail_ids)}")
            
            if not mail_ids:
                logger.info("未読メールはありません")
                return False
            
            # フィルター条件を取得
            sender_filter = self.config_manager.get('Monitor', 'sender_filter').strip()
            keyword_filter = self.config_manager.get('Monitor', 'keyword_filter').strip()
            logger.info(f"フィルター条件 - 送信者: '{sender_filter}', キーワード: '{keyword_filter}'")
            
            # 各メールをチェック
            for i, mail_id in enumerate(mail_ids, 1):
                logger.info(f"メール {i}/{len(mail_ids)} をチェック中")
                
                status, msg_data = self.imap.fetch(mail_id, '(RFC822)')
                if status != 'OK':
                    logger.warning(f"メール {i} の取得に失敗")
                    continue
                
                # メールをパース
                msg = email.message_from_bytes(msg_data[0][1])
                
                # 受信時刻をチェック
                date_header = msg.get('Date', '')
                if date_header:
                    try:
                        mail_date = parsedate_to_datetime(date_header)
                        # タイムゾーンを考慮して比較
                        if mail_date.tzinfo is None:
                            mail_date = mail_date.replace(tzinfo=timezone.utc)
                        
                        logger.info(f"  受信時刻: {mail_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                        
                        # 時間範囲外のメールはスキップ
                        if mail_date < time_threshold:
                            logger.info(f"  → 受信時刻が範囲外（{time_window_minutes}分以上前）のためスキップ")
                            continue
                    except Exception as e:
                        logger.warning(f"  受信時刻の解析エラー: {e}")
                        # 受信時刻が解析できない場合は処理を続行
                
                # 送信者をチェック
                from_header = msg.get('From', '')
                subject = msg.get('Subject', '')
                
                # ヘッダーをデコード
                from_decoded = self._decode_header(from_header)
                subject_decoded = self._decode_header(subject)
                
                logger.info(f"  送信者: {from_decoded}")
                logger.info(f"  件名: {subject_decoded}")
                
                if sender_filter and sender_filter.lower() not in from_header.lower():
                    logger.info("  → 送信者フィルターに一致せず")
                    continue
                
                # 本文をチェック
                body = self._get_email_body(msg)
                if body:
                    body_length = len(body)
                    body_preview = body[:100].replace('\n', ' ')
                    logger.info(f"  本文: {body_length}文字")
                    logger.info(f"  本文プレビュー: {body_preview}...")
                else:
                    logger.info("  本文: (取得できませんでした)")
                
                if keyword_filter and keyword_filter.lower() not in body.lower():
                    logger.info("  → キーワードフィルターに一致せず")
                    continue
                
                # 条件に合致
                logger.info("  ✓ 条件に合致しました！")
                return True
            
            logger.info("条件に合致するメールはありませんでした")
            return False
            
        except Exception as e:
            logger.error(f"メールチェックエラー: {str(e)}")
            raise Exception(f"メールチェックエラー: {str(e)}")
    
    def _decode_header(self, header_value):
        """メールヘッダーをデコード"""
        if not header_value:
            return ""
        
        decoded_parts = []
        for part, encoding in decode_header(header_value):
            if isinstance(part, bytes):
                # エンコーディングが指定されている場合はそれを使用、なければutf-8
                decoded_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
            else:
                decoded_parts.append(str(part))
        
        return ''.join(decoded_parts)
    
    def _get_email_body(self, msg):
        """メール本文を取得"""
        body = ""
        
        if msg.is_multipart():
            logger.debug("  メールはマルチパート形式です")
            for part in msg.walk():
                content_type = part.get_content_type()
                logger.debug(f"    パート: {content_type}")
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or 'utf-8'
                            decoded_text = payload.decode(charset, errors='ignore')
                            body += decoded_text
                            logger.debug(f"    text/plain パートを取得: {len(decoded_text)} 文字")
                    except Exception as e:
                        logger.debug(f"    text/plain パートのデコードエラー: {e}")
        else:
            logger.debug("  メールはシングルパート形式です")
            try:
                content_type = msg.get_content_type()
                logger.debug(f"  コンテンツタイプ: {content_type}")
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='ignore')
                    logger.debug(f"  本文を取得: {len(body)} 文字")
            except Exception as e:
                logger.debug(f"  本文のデコードエラー: {e}")
        
        if not body:
            logger.debug("  本文が取得できませんでした")
        
        return body


