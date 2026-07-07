import base64
import numpy as np


def main():
    x = np.random.randn(32000).astype(np.float32)
    b64 = base64.b64encode(x.tobytes()).decode("utf-8")

    raw = base64.b64decode(b64)
    y = np.frombuffer(raw, dtype=np.float32)

    print("equal:", np.allclose(x, y))
    print("len_x:", len(x), "len_y:", len(y))
    print("dtype:", y.dtype)


if __name__ == "__main__":
    main()

