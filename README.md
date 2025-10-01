# Gmail監視ビープアプリ

imaplibとTkinterを使用した、Gmailの未読メール監視アプリケーションです。特定の条件（送信者・本文キーワード）に合致したメールを受信すると、警告音で通知します。

**GUI版とCLI版の両方が利用可能です。**

## 機能

- **Gmail監視**: 定期的にGmailの未読メールをチェック
- **時間範囲フィルタリング**: 指定した時間範囲内に受信したメールのみを対象
- **送信者・キーワードフィルタリング**: 特定の送信者と本文キーワードでフィルタリング
- **警告音通知**: 条件に合致したメール受信時にカスタマイズ可能な警告音で通知
- **ビープ回数カウンター**: アプリ起動からの通知回数を表示
- **GUIモード**: シンプルで使いやすいTkinter GUI
- **CLIモード**: サーバーやバックグラウンド実行に最適なコマンドライン版
- **設定管理**: config.iniまたはコマンドライン引数で設定を管理

## 必要要件

- Python 3.11以上
- Gmailアカウント
- Googleアカウントの2段階認証とアプリパスワード
- 外部ライブラリ:
  - numpy (音声波形生成用)
  - simpleaudio (音声再生用)

## セットアップ

### 1. Gmailアプリパスワードの取得

このアプリを使用するには、Googleアカウントでアプリパスワードを生成する必要があります。

1. [Googleアカウント](https://myaccount.google.com/)にログイン
2. 「セキュリティ」→「2段階認証プロセス」を有効化（まだの場合）
3. 「アプリパスワード」を検索して開く
4. 「アプリを選択」→「その他（カスタム名）」を選択
5. 適当な名前（例：Gmail監視アプリ）を入力して「生成」
6. 表示された16桁のパスワードをコピー（スペースなし）

### 2. 依存関係のインストール

```bash
# プロジェクトディレクトリに移動
cd /Users/koizumi/workspace/mail_beep_sound

# uvを使用している場合（推奨）
uv sync

# pipを使用する場合
pip install numpy simpleaudio
```

### 3. アプリの起動

#### GUIモード（デフォルト）

```bash
# uvを使用している場合
uv run python main.py

# または明示的にGUIモードを指定
uv run python main.py gui

# インストール後のコマンド（uv sync後）
uv run mail-beep
uv run mail-beep gui
```

#### CLIモード

```bash
# uvを使用している場合
uv run python main.py cli

# インストール後のコマンド（uv sync後）
uv run mail-beep cli

# CLIモードで追加オプションを指定
uv run mail-beep cli --config /path/to/config.ini --debug

# CLIモードのヘルプを表示
uv run mail-beep cli --help
```

#### ヘルプの表示

```bash
# 全体のヘルプ
uv run mail-beep --help

# CLIモードのヘルプ
uv run mail-beep cli --help
```

### 4. 初回設定

#### GUIモードの設定

初回起動時、設定画面が自動的に開きます：

1. **Gmailアドレス**: あなたのGmailアドレスを入力
2. **アプリパスワード**: 上記で取得した16桁のアプリパスワードを入力
3. **チェック間隔（秒）**: メールボックスをチェックする間隔（デフォルト: 60秒）
4. **時間範囲（分）**: 何分以内に受信したメールを対象とするか（デフォルト: 2分）
5. **送信者フィルター**: 監視したい送信者のメールアドレス（部分一致、任意）
6. **キーワードフィルター**: メール本文に含まれるべきキーワード（部分一致、任意）
7. **ビープ音の秒数**: 警告音の持続時間（デフォルト: 10秒）

設定を入力したら「保存」ボタンをクリックします。

#### CLIモードの設定

CLIモードでは2つの方法で設定できます：

##### 方法1: 設定ファイル（config.ini）を使用

```bash
# 最初にGUIモードで設定を作成するか、手動でconfig.iniを作成
uv run mail-beep cli --config config.ini
```

##### 方法2: コマンドライン引数で指定

```bash
# 基本的な使い方
uv run mail-beep cli \
  --email your-email@gmail.com \
  --password 'your-app-password' \
  --interval 60 \
  --time-window 2

# フィルターを追加
uv run mail-beep cli \
  --email your-email@gmail.com \
  --password 'your-app-password' \
  --sender-filter 'example@example.com' \
  --keyword-filter '重要'

# デバッグモードで実行
uv run mail-beep cli --debug

# 一度だけチェック（テスト用）
uv run mail-beep cli --once
```

## 使用方法

### GUIモード

#### メイン画面

- **開始ボタン**: メール監視を開始します
- **停止ボタン**: メール監視を停止します
- **設定ボタン**: 設定画面を開きます（監視停止中のみ）
- **ステータス表示**: 現在の監視状態を表示
- **ビープ回数**: アプリ起動からビープ音を鳴らした回数

#### GUIでの監視の流れ

1. 「開始」ボタンをクリック
2. 設定したチェック間隔でGmailの未読メールを確認
3. 以下の条件をすべて満たすメールがあれば警告音を鳴らします：
   - 未読メールである
   - 設定した時間範囲内に受信したメールである（デフォルト: 2分以内）
   - 送信者フィルターに一致する（設定している場合）
   - 本文にキーワードフィルターが含まれる（設定している場合）
4. ビープ回数カウンターが増加

### CLIモード

#### コマンドライン引数

```bash
# CLIモードのヘルプを表示
uv run mail-beep cli --help
```

利用可能なオプション：

- `--config PATH`: 設定ファイルのパス（デフォルト: config.ini）
- `--email EMAIL`: Gmailアドレス
- `--password PASSWORD`: Gmailアプリパスワード
- `--interval SECONDS`: チェック間隔（秒）
- `--time-window MINUTES`: 受信時刻の範囲（分）
- `--sender-filter TEXT`: 送信者フィルター
- `--keyword-filter TEXT`: キーワードフィルター
- `--beep-duration SECONDS`: ビープ音の秒数
- `--debug`: デバッグモードで実行
- `--once`: 一度だけチェックして終了（テスト用）

#### CLIでの監視の流れ

1. アプリを起動（バックグラウンドで実行する場合は `&` や `nohup` を使用）
2. 設定したチェック間隔でGmailの未読メールを確認
3. 条件に合致するメールがあれば警告音を鳴らし、ログに記録
4. 停止するには以下のいずれかの方法：
   - **Enterキーを押す**（推奨）
   - **'q' + Enter を押す**
   - **Ctrl+C を押す**

#### 実行例

##### フォアグラウンドで実行（推奨）

```bash
# 通常実行
uv run mail-beep cli

# 監視が開始されます...
# 停止するには Enter キーを押すだけ！
```

##### バックグラウンドで実行

```bash
# バックグラウンドで実行
uv run mail-beep cli > mail-beep.log 2>&1 &

# ジョブ番号を確認
jobs

# フォアグラウンドに戻して停止
fg              # または fg %1
# Enter キーを押す

# または、プロセスを直接停止
pkill -f "mail-beep"
```

##### nohupで実行（ターミナルを閉じても継続）

```bash
# nohupで実行
nohup uv run mail-beep cli > mail-beep.log 2>&1 &

# プロセスIDを確認
ps aux | grep mail-beep

# ログをリアルタイムで確認
tail -f mail-beep.log

# 停止する場合
pkill -f "mail-beep"
# または
kill <プロセスID>
```

##### systemdサービスとして実行（Linux）

```bash
# サービスファイルを作成: /etc/systemd/system/mail-beep.service
[Unit]
Description=Gmail Monitor Beep Service
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/mail_beep_sound
ExecStart=/usr/bin/uv run mail-beep cli
Restart=always
StandardOutput=append:/var/log/mail-beep.log
StandardError=append:/var/log/mail-beep.log

[Install]
WantedBy=multi-user.target

# サービスを有効化して起動
sudo systemctl enable mail-beep
sudo systemctl start mail-beep

# ステータス確認
sudo systemctl status mail-beep

# 停止
sudo systemctl stop mail-beep
```

##### macOS LaunchAgentとして実行（macOS）

```bash
# LaunchAgentファイルを作成: ~/Library/LaunchAgents/com.mailbeep.monitor.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mailbeep.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/uv</string>
        <string>run</string>
        <string>mail-beep</string>
        <string>cli</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/yourusername/workspace/mail_beep_sound</string>
    <key>StandardOutPath</key>
    <string>/Users/yourusername/Library/Logs/mail-beep.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/yourusername/Library/Logs/mail-beep-error.log</string>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>

# サービスを読み込んで起動
launchctl load ~/Library/LaunchAgents/com.mailbeep.monitor.plist

# サービスを停止
launchctl unload ~/Library/LaunchAgents/com.mailbeep.monitor.plist

# ログを確認
tail -f ~/Library/Logs/mail-beep.log
```

### 共通の注意事項

- **未読メールのみ**: 既読メールは監視対象外です
- **時間範囲フィルター**: 設定した時間範囲内に受信したメールのみが対象です。これにより、古い未読メールでは何度も通知が鳴ることを防ぎます
- **フィルターの動作**:
  - 送信者フィルターとキーワードフィルターの両方が設定されている場合、両方に一致する必要があります
  - フィルターを空欄にすると、その条件はチェックされません（時間範囲内のすべての未読メールが対象）
- **警告音**: 音量変動のある低音の警告音（300Hz、6Hzで変動）が設定した秒数再生されます

## 設定ファイル

設定は `config.ini` に保存されます：

```ini
[Gmail]
email = your-email@gmail.com
password = your-app-password

[Monitor]
check_interval = 60
time_window_minutes = 2
sender_filter = example@example.com
keyword_filter = 重要

[Sound]
beep_duration = 10
```

**セキュリティ警告**: `config.ini`にはパスワードが平文で保存されます。ファイルの取り扱いには十分注意してください。

## トラブルシューティング

### 「接続エラー」が表示される

- Gmailアドレスとアプリパスワードが正しいか確認
- インターネット接続を確認
- Googleアカウントの2段階認証が有効か確認

### 警告音が鳴らない

- 条件に合致する未読メールがあるか確認
- 時間範囲フィルターの設定を確認（メールが時間範囲内に受信されているか）
- 送信者フィルター・キーワードフィルターの設定を確認
- チェック間隔を短くして再度テスト

### macOSで警告音が聞こえない

- システム環境設定で音量を確認
- `simpleaudio`が正しくインストールされているか確認
- ターミナルから実行している場合、ターミナルに音声出力権限があるか確認

### 警告音の再生エラー

- `simpleaudio`と`numpy`が正しくインストールされているか確認
- エラーが発生した場合、フォールバックとしてターミナルベル（`\a`）が使用されます

## ライセンス

このプロジェクトはオープンソースです。自由に使用・改変してください。

## 開発者向け

### 依存関係

**標準ライブラリ:**

- `tkinter`: GUI
- `imaplib`: Gmail IMAP接続
- `email`: メール解析
- `configparser`: 設定管理
- `threading`: バックグラウンド監視
- `logging`: ロギング

**外部ライブラリ:**

- `numpy`: 音声波形生成
- `simpleaudio`: 音声再生

**開発用依存関係:**

- `pyinstaller`: スタンドアロン実行ファイルのビルド
- `ruff`: リンター/フォーマッター

### プロジェクト構造

```bash
mail_beep_sound/
├── main.py              # 統一されたエントリーポイント（GUI/CLI切り替え）
├── cli.py               # CLI機能の実装
├── config_manager.py    # 設定ファイル管理
├── gmail_monitor.py     # Gmail監視機能
├── utils.py             # ユーティリティ関数（ロギング、警告音生成）
├── ui/
│   ├── __init__.py      # UIモジュール
│   ├── main_window.py   # メインウィンドウ
│   └── settings_window.py # 設定ウィンドウ
├── config.ini           # 設定ファイル（自動生成）
├── pyproject.toml       # プロジェクト設定
├── uv.lock              # uvの依存関係ロックファイル
└── README.md            # このファイル
```

### 警告音について

警告音は`utils.py`の`play_beep()`関数で生成されます：

- 基本周波数: 300Hz（低音）
- 倍音: 600Hz（2倍音）を30%ミックス
- トレモロ効果: 6Hzで音量変動（サイレン効果）
- フェードアウト: 最後の0.3秒でフェードアウト
- 音量: 40%
