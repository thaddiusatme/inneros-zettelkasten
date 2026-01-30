import logging
import argparse
import sys
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.indexer import VaultIndexer


def main():
    parser = argparse.ArgumentParser(description="Index Zettelkasten vault for RAG.")
    parser.add_argument(
        "--vault", type=str, default="knowledge", help="Path to vault root"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force re-indexing of all files"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    indexer = VaultIndexer(vault_path=args.vault)

    print(f"Indexing vault at: {args.vault}")
    stats = indexer.index_vault(incremental=not args.force)

    print("\n--- Summary ---")
    print(f"Processed: {stats['processed']}")
    print(f"Skipped:   {stats['skipped']}")
    print(f"Errors:    {stats['errors']}")


if __name__ == "__main__":
    main()
