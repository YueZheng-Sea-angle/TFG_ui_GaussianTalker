import os
import subprocess

_tts = None


def _get_tts():
    global _tts
    if _tts is not None:
        return _tts
    import torch
    from TTS.api import TTS
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig
    import torch.serialization

    # Fix for PyTorch 2.6+ `weights_only=True` default
    # We need to explicitly allowlist the config class to be unpickled.
    try:
        torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig])
    except Exception:
        # If add_safe_globals is unavailable, continue; downstream may still work on older torch
        pass

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    try:
        tts = tts.to(device)
    except Exception:
        pass
    _tts = tts
    return _tts


def _ffmpeg_convert_to_wav_mono_22k(src_path: str, dst_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            src_path,
            "-ac",
            "1",
            "-ar",
            "22050",
            "-c:a",
            "pcm_s16le",
            dst_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0 and os.path.exists(dst_path) and os.path.getsize(dst_path) > 0
    except Exception:
        return False


def synthesize_with_clone(text: str, ref_audio_path: str, out_path: str, language: str = "zh-cn") -> str:
    if not text:
        raise ValueError("empty text")
    if not ref_audio_path or not os.path.exists(ref_audio_path):
        raise FileNotFoundError("reference audio not found")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    tmp_dir = os.path.dirname(ref_audio_path)
    norm_ref = os.path.join(tmp_dir, "__ref_norm__.wav")
    ok = _ffmpeg_convert_to_wav_mono_22k(ref_audio_path, norm_ref)
    use_ref = norm_ref if ok else ref_audio_path

    tts = _get_tts()
    tts.tts_to_file(text=text, speaker_wav=use_ref, language=language, file_path=out_path)

    try:
        if os.path.exists(norm_ref):
            os.remove(norm_ref)
    except Exception:
        pass

    return out_path
