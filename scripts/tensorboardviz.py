# ================================================================
# path: scripts/tensorboardviz.py
# brief: Launches TensorBoard Embedding Projector from branch_embed.json
# usage: python scripts/tensorboardviz.py [--embed PATH] [--logdir DIR] [--port PORT]
# ================================================================
import json
import argparse
import subprocess
import sys
import numpy as np
import tensorflow as tf

from pathlib import Path
from tensorboard.plugins import projector


# ── Defaults ──────────────────────────────────────────────────────
SCRIPT_DIR: Path = Path(__file__).parent
PROJECT_ROOT: Path = SCRIPT_DIR.parent
DEFAULT_EMBED: Path = PROJECT_ROOT / "data" / "branch_embed.json"
DEFAULT_LOGDIR: Path = PROJECT_ROOT / "runs" / "embedding_viz"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate TensorBoard Embedding Projector from a JSON embedding file."
    )
    parser.add_argument(
        "--embed",
        type=Path,
        default=DEFAULT_EMBED,
        help=f"Path to embedding JSON file (default: {DEFAULT_EMBED})",
    )
    parser.add_argument(
        "--logdir",
        type=Path,
        default=DEFAULT_LOGDIR,
        help=f"TensorBoard log directory (default: {DEFAULT_LOGDIR})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6006,
        help="Port for TensorBoard server (default: 6006)",
    )
    parser.add_argument(
        "--no-launch",
        action="store_true",
        help="Prepare files only; don't start TensorBoard.",
    )
    return parser.parse_args()


def load_embeddings(embed_path: Path) -> list[dict]:
    """Load the JSON embedding file. Each object must have: uuid, chunk, path, embedding, qdrant-id."""
    if not embed_path.exists():
        raise FileNotFoundError(f"Embedding file not found: {embed_path}")

    with open(embed_path, "r", encoding="utf-8") as f:
        data: list[dict] = json.load(f)

    if not data:
        raise ValueError(f"Embedding file is empty: {embed_path}")

    # Validate first record
    required_keys = {"uuid", "chunk", "embedding"}
    missing = required_keys - data[0].keys()
    if missing:
        raise KeyError(f"First record is missing keys: {missing}")

    print(f"Loaded {len(data):,} records from {embed_path}")
    return data


def write_metadata(data: list[dict], logdir: Path) -> Path:
    """Write metadata.tsv for the TensorBoard projector."""
    metadata_path: Path = logdir / "metadata.tsv"

    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write("uuid\tuuid_prefix\tpath\tlabel\n")

        for record in data:
            uuid: str = record.get("uuid", "")
            uuid_prefix: str = uuid.split(".")[0] if "." in uuid else uuid
            path: str = record.get("path", "").replace("\t", " ").replace("\n", " ")
            label: str = record["chunk"][:200].replace("\t", " ").replace("\n", " ")

            f.write(f"{uuid}\t{uuid_prefix}\t{path}\t{label}\n")

    print(f"Wrote metadata  → {metadata_path}  ({len(data):,} rows)")
    return metadata_path


def write_checkpoint(data: list[dict], logdir: Path) -> Path:
    """Create a TF checkpoint containing the embedding variable."""
    embeddings = np.array(
        [record["embedding"] for record in data],
        dtype=np.float32,
    )
    print(f"Embedding matrix → {embeddings.shape[0]:,} × {embeddings.shape[1]}")

    embedding_var = tf.Variable(embeddings, name="embeddings")
    checkpoint = tf.train.Checkpoint(embeddings=embedding_var)
    checkpoint_path: str = checkpoint.save(file_prefix=str(logdir / "embedding.ckpt"))

    print(f"Saved checkpoint → {checkpoint_path}")
    return Path(checkpoint_path)


def write_projector_config(logdir: Path) -> Path:
    """Write projector_config.pbtxt linking the checkpoint to metadata."""
    config = projector.ProjectorConfig()

    embedding_config = config.embeddings.add()
    embedding_config.tensor_name = "embeddings/.ATTRIBUTES/VARIABLE_VALUE"
    embedding_config.metadata_path = "metadata.tsv"

    projector.visualize_embeddings(logdir, config)

    config_path: Path = logdir / "projector_config.pbtxt"
    print(f"Projector config → {config_path}")
    return config_path


def launch_tensorboard(logdir: Path, port: int) -> None:
    """Start TensorBoard as a subprocess."""
    cmd = [sys.executable, "-m", "tensorboard", "--logdir", str(logdir), "--port", str(port)]
    print(f"\nStarting TensorBoard on http://localhost:{port}")
    print(f"  → Projector tab: http://localhost:{port}/#projector")
    print(f"  → Press Ctrl+C to stop.\n")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nTensorBoard stopped.")


def main() -> None:
    args = parse_args()
    logdir: Path = args.logdir
    logdir.mkdir(parents=True, exist_ok=True)

    # 1. Load
    data = load_embeddings(args.embed)

    # 2. Write metadata TSV
    write_metadata(data, logdir)

    # 3. Write TF checkpoint
    write_checkpoint(data, logdir)

    # 4. Write projector config
    write_projector_config(logdir)

    print(f"\nAll files written to {logdir}/")

    # 5. Launch
    if not args.no_launch:
        launch_tensorboard(logdir, args.port)
    else:
        print(f"Run manually:  tensorboard --logdir {logdir} --port {args.port}")


if __name__ == "__main__":
    main()