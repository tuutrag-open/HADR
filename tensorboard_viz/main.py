import json
import re
import shutil
import argparse
import subprocess
import sys
import numpy as np
import tensorflow as tf

from pathlib import Path
from tensorboard.plugins import projector


DEFAULT_LOGDIR: Path = Path(__file__).parent / "runs" / "embedding_viz"

# Regex to extract the branch-level UUID: UUID-BASE.FIRST_NUMBER
# e.g. "041f16b3-f3b7-488f-a27c-074e63a9d300.1.1" -> "041f16b3-f3b7-488f-a27c-074e63a9d300.1"
_BRANCH_RE = re.compile(
    r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.\d+)"
)


# CLI
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="TensorBoard Embedding Projector from a JSON embedding file.",
    )
    parser.add_argument(
        "embed",
        type=Path,
        help="Path to embedding JSON file (e.g. data/branch_embed.json or data/leaf_embed.json)",
    )
    parser.add_argument(
        "--chunks",
        type=Path,
        default=None,
        help="Path to fixed_sized_chunks.json for type-based color labels.",
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
        help="Write projector files only; don't start TensorBoard.",
    )
    return parser.parse_args()


# UUID resolution
def resolve_branch_uuid(uuid: str) -> str:
    """
    Resolve any UUID to its branch-level form.

    '041f16b3-f3b7-488f-a27c-074e63a9d300.1.1' -> '041f16b3-f3b7-488f-a27c-074e63a9d300.1'
    '041f16b3-f3b7-488f-a27c-074e63a9d300.1' -> '041f16b3-f3b7-488f-a27c-074e63a9d300.1'
    """
    m = _BRANCH_RE.match(uuid)
    return m.group(1) if m else uuid


# Load chunks (type lookup)
def load_chunks(chunks_path: Path) -> dict[str, str]:
    """
    Load fixed_sized_chunks.json and build a uuid -> type lookup dict.

    Each entry looks like:
        {"uuid": "041f16b3-…d300.1", "chunk": "…", "path": "…", "type": "supplemental"}
    """
    if not chunks_path.exists():
        print(f"Warning: Chunks file not found → {chunks_path}")
        print("         All points will be labeled type='unknown'.")
        return {}

    with open(chunks_path, "r", encoding="utf-8") as f:
        data: list[dict] = json.load(f)

    lookup: dict[str, str] = {}
    for record in data:
        uuid = record.get("uuid", "")
        chunk_type = record.get("type", "unknown")
        lookup[uuid] = chunk_type

    print(f"       Loaded {len(lookup):,} chunk-type mappings from {chunks_path.name}")
    return lookup


# Load embeddings
def load_embeddings(embed_path: Path) -> list[dict]:
    """
    Load JSON embedding file.

    Supports two formats:
      - branch_embed.json -> keys: uuid, chunk, path, embedding
      - leaf_embed.json -> keys: uuid, text, embedding
    """
    if not embed_path.exists():
        print(f"Error: File not found → {embed_path}")
        sys.exit(1)

    with open(embed_path, "r", encoding="utf-8") as f:
        data: list[dict] = json.load(f)

    if not data:
        print(f"Error: File is empty -> {embed_path}")
        sys.exit(1)

    first_keys = set(data[0].keys())

    # Accept either branch format {uuid, chunk, embedding} or leaf format {uuid, text, embedding}
    has_uuid = "uuid" in first_keys
    has_embedding = "embedding" in first_keys
    has_content = "chunk" in first_keys or "text" in first_keys

    if not (has_uuid and has_embedding and has_content):
        print(
            f"Error: First record must have 'uuid', 'embedding', and either 'chunk' or 'text'.\n"
            f"       Found keys: {first_keys}"
        )
        sys.exit(1)

    print(f"[1/4] Loaded {len(data):,} records from {embed_path}")
    return data


# Metadata
def write_metadata(
    data: list[dict],
    logdir: Path,
    chunk_types: dict[str, str] | None = None,
) -> None:
    """
    Write metadata.tsv — one row per embedding point.

    Columns: uuid, uuid_prefix, path, type, label
    The 'type' column allows TensorBoard's "Color by" to segment clusters.
    """
    metadata_path: Path = logdir / "metadata.tsv"
    type_lookup = chunk_types or {}

    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write("uuid\tuuid_prefix\tpath\ttype\tlabel\n")

        for record in data:
            uuid: str = record.get("uuid", "")
            uuid_prefix: str = uuid.split(".")[0] if "." in uuid else uuid
            path: str = record.get("path", "").replace("\t", " ").replace("\n", " ")

            # Resolve branch UUID and look up type
            branch_uuid = resolve_branch_uuid(uuid)
            chunk_type = type_lookup.get(branch_uuid, "unknown")

            # Support both 'chunk' (branch) and 'text' (leaf) keys
            content: str = record.get("chunk") or record.get("text", "")
            label: str = content[:200].replace("\t", " ").replace("\n", " ")

            f.write(f"{uuid}\t{uuid_prefix}\t{path}\t{chunk_type}\t{label}\n")

    print(f"[2/4] Wrote metadata -> {metadata_path}")


# Checkpoint
def write_checkpoint(data: list[dict], logdir: Path) -> None:
    """Save embedding matrix as a TF checkpoint."""
    embeddings = np.array(
        [record["embedding"] for record in data],
        dtype=np.float32,
    )
    print(f"[3/4] Embedding matrix: {embeddings.shape[0]:,} x {embeddings.shape[1]}")

    embedding_var = tf.Variable(embeddings, name="embeddings")
    checkpoint = tf.train.Checkpoint(embeddings=embedding_var)
    checkpoint.save(file_prefix=str(logdir / "embedding.ckpt"))


# Projector config
def write_projector_config(logdir: Path) -> None:
    """Write projector_config.pbtxt linking tensor -> metadata."""
    config = projector.ProjectorConfig()

    embedding_config = config.embeddings.add()
    embedding_config.tensor_name = "embeddings/.ATTRIBUTES/VARIABLE_VALUE"
    embedding_config.metadata_path = "metadata.tsv"

    projector.visualize_embeddings(logdir, config)
    print(f"[4/4] Projector config -> {logdir / 'projector_config.pbtxt'}")


# Launch
def launch_tensorboard(logdir: Path, port: int) -> None:
    """Start TensorBoard as a blocking subprocess."""
    tb_bin = shutil.which("tensorboard")
    if tb_bin is None:
        print("Error: 'tensorboard' command not found in PATH.")
        print(f"Run manually:  tensorboard --logdir {logdir} --port {port}")
        sys.exit(1)

    cmd = [tb_bin, "--logdir", str(logdir), "--port", str(port)]

    print(f"\n{'=' * 60}")
    print(f"  TensorBoard:  http://localhost:{port}")
    print(f"  Projector:    http://localhost:{port}/#projector")
    print(f"  Press Ctrl+C to stop.")
    print(f"{'=' * 60}\n")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nTensorBoard stopped.")


def main() -> None:
    args = parse_args()

    logdir: Path = args.logdir.resolve()
    logdir.mkdir(parents=True, exist_ok=True)

    data = load_embeddings(args.embed.resolve())

    # Load chunk-type mappings if --chunks was provided
    chunk_types: dict[str, str] | None = None
    if args.chunks is not None:
        chunk_types = load_chunks(args.chunks.resolve())

    write_metadata(data, logdir, chunk_types)
    write_checkpoint(data, logdir)
    write_projector_config(logdir)

    print(f"\nAll files written to {logdir}/")

    if args.no_launch:
        print(f"Run manually:  tensorboard --logdir {logdir} --port {args.port}")
    else:
        launch_tensorboard(logdir, args.port)


if __name__ == "__main__":
    main()