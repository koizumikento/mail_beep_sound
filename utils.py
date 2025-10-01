"""ユーティリティ関数モジュール"""
import logging
import numpy as np
import simpleaudio as sa


def setup_logging(level=logging.INFO):
    """ロギング設定を初期化"""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # すでにハンドラーが設定されていたら追加しない
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)


logger = logging.getLogger(__name__)


def play_beep(duration=10.0):
    """警告音を生成して鳴らす（低音で音量が変動する警告を煽る音）
    
    Args:
        duration: 音の持続時間（秒）デフォルトは10秒
    """
    try:
        # サンプリングレート
        sample_rate = 44100
        
        # 基本周波数（Hz）- 300Hzの低めの警告音
        frequency = 300
        
        # 時間軸を生成
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 基本のサイン波を生成
        note = np.sin(frequency * t * 2 * np.pi)
        
        # 倍音を追加して厚みのある音に（2倍音を少し混ぜる）
        note += 0.3 * np.sin(2 * frequency * t * 2 * np.pi)
        
        # 音量を変動させる（6Hzで変動 = サイレンのような効果）
        tremolo_frequency = 6
        tremolo = 0.5 + 0.5 * np.sin(tremolo_frequency * t * 2 * np.pi)
        note = note * tremolo
        
        # 最後にフェードアウト
        fade_samples = int(sample_rate * 0.3)
        envelope = np.ones_like(note)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        note = note * envelope
        
        # 音量を調整（0.4 = 40%の音量）
        note = note * 0.4
        
        # 16ビット整数に変換
        audio = note * (2**15 - 1) / np.max(np.abs(note))
        audio = audio.astype(np.int16)
        
        # 再生
        logger.info("警告音を生成して再生します")
        play_obj = sa.play_buffer(audio, 1, 2, sample_rate)
        play_obj.wait_done()  # 再生が終わるまで待つ
        
    except Exception as e:
        logger.error(f"ビープ音の生成/再生エラー: {e}")
        # フォールバック: ターミナルベル
        print('\a', flush=True)


