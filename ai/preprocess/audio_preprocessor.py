"""Audio preprocessing and feature extraction."""
try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    np = None


class AudioPreprocessor:
    """Preprocess audio for AI models."""

    @staticmethod
    def normalize(audio):
        if np is not None:
            audio = audio - np.mean(audio)
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val
            return audio

        if not audio:
            return []
        mean_value = sum(audio) / len(audio)
        centered = [value - mean_value for value in audio]
        max_val = max(abs(value) for value in centered) if centered else 0.0
        if max_val > 0:
            return [value / max_val for value in centered]
        return centered

    @staticmethod
    def resample(audio, orig_sr: int, target_sr: int = 16000):
        if orig_sr == target_sr or len(audio) < 2:
            if np is not None:
                return audio.astype(np.float32)
            return list(audio)

        n_target = int(round(len(audio) * target_sr / orig_sr))
        if n_target < 1:
            if np is not None:
                return audio.astype(np.float32)
            return list(audio)

        if np is not None:
            x_old = np.linspace(0.0, 1.0, len(audio), endpoint=False)
            x_new = np.linspace(0.0, 1.0, n_target, endpoint=False)
            return np.interp(x_new, x_old, audio).astype(np.float32)

        if not audio:
            return []

        output = []
        for idx in range(n_target):
            old_index = idx * len(audio) / n_target
            lower = int(old_index)
            upper = min(lower + 1, len(audio) - 1)
            if upper == lower:
                output.append(audio[lower])
            else:
                frac = old_index - lower
                output.append(audio[lower] + (audio[upper] - audio[lower]) * frac)
        return output

    @staticmethod
    def to_mono(audio):
        if np is not None and hasattr(audio, "ndim") and audio.ndim > 1:
            return np.mean(audio, axis=1)

        if hasattr(audio, "__iter__") and not isinstance(audio, (str, bytes)):
            first = next(iter(audio), None)
            if isinstance(first, (list, tuple)):
                return [sum(values) / len(values) for values in audio]
        return audio

