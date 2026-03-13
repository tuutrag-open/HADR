# TensorBoard Embedding Visualizer for tuutrag-open

Interactive 3D visualization of branch and leaf embeddings using TensorBoard's Embedding Projector. Clusters can be color-segmented by artifact **type** (`supplemental`, `requirement`, `test`, etc.) via cross-referencing against `fixed_sized_chunks.json`.

> **Validated on macOS Sequoia — Apple M4 (arm64).**

---

## Prerequisites

| Requirement | Notes |
|---|---|
| macOS with Apple Silicon (M4 / M-series) | Must run natively — **not** under Rosetta |
| [Homebrew](https://brew.sh) | Package manager for macOS |
| Python 3.10 – 3.11 | Recommended for best TensorFlow compatibility on ARM |

---

## Step-by-Step Setup

### 1. Install Python via Homebrew

```sh
brew install python@3.11
```

Confirm the version:

```sh
python3.11 --version
```

### 2. Create & activate a virtual environment

From the **repository root** (or from `tensorboard-viz/`):

```sh
cd tensorboard-viz
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Upgrade pip & core build tools

```sh
pip install --upgrade pip setuptools wheel
```

### 4. Install TensorFlow (native ARM)

```sh
pip install tensorflow
```

> If you hit architecture errors, try: `pip install tensorflow-macos`

#### (Optional) Metal GPU acceleration

```sh
pip install tensorflow-metal
```

### 5. Install TensorBoard & NumPy

```sh
pip install tensorboard numpy
```

### 6. Verify the installation

```sh
python -c "import tensorflow as tf; print('TF', tf.__version__); print('GPUs:', len(tf.config.list_physical_devices('GPU')))"
```

Confirm you are on native ARM:

```sh
python -c "import platform; print(platform.machine())"
# Expected output: arm64
```

---

## Usage

All paths below assume you are inside `tensorboard-viz/`.

**Branch embeddings (default):**

```sh
python main.py ../../data/branch_embed.json
```

**Leaf embeddings:**

```sh
python main.py ../../data/leaf_embed.json
```

**Custom port:**

```sh
python main.py ../../data/branch_embed.json --port 8080
```

**With chunk-type coloring (color clusters by artifact type):**

```sh
python main.py ../../data/branch_embed.json --chunks ../../data/processed/fixed_sized_chunks.json
```

**Write projector files only (no auto-launch):**

```sh
python main.py ../../data/branch_embed.json --chunks ../../data/processed/fixed_sized_chunks.json --no-launch
```

Once TensorBoard is running, open the **Projector** tab and use the **"Color by"** dropdown → select **`type`** to see clusters segmented by artifact type.

---

## Data Files

| File | Description | UUID Format |
|---|---|---|
| `data/branch_embed.json` | Branch-level embeddings (Gemini `gemini-embedding-001`) | `UUID-BASE.#` (e.g. `041f16b3-…d300.1`) |
| `data/leaf_embed.json` | Leaf-level embeddings (OpenAI decomposition) | `UUID-BASE.#.#` (e.g. `041f16b3-…d300.1.1`) |
| `data/processed/fixed_sized_chunks.json` | Chunk metadata with `"type"` field used for color segmentation | `UUID-BASE.#` |

### Type-coloring cross-reference

Each embedding UUID is resolved to its **branch-level** UUID (`UUID-BASE.#`) and matched against the `"uuid"` field in `fixed_sized_chunks.json`. The `"type"` value from the matched entry (e.g. `"supplemental"`) is written into the TensorBoard metadata so the Projector can color points accordingly.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `platform.machine()` returns `x86_64` | You are running under Rosetta. Re-open Terminal natively (check "Open using Rosetta" is **unchecked** in Finder → Get Info on Terminal.app). |
| Mixed architecture errors | `pip cache purge` then reinstall inside a fresh venv to avoid mixing ARM64 / x86_64 wheels. |
| TensorBoard won't start | `pip install tensorboard --force-reinstall` |
| Missing `tensorflow` wheel for your Python | Use Python 3.10 or 3.11 — these have the widest TF wheel support on Apple Silicon. |

For the latest compatibility info, see the official [TensorFlow installation guide](https://www.tensorflow.org/install).