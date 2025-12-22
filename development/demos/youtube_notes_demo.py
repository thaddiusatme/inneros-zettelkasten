#!/usr/bin/env python3
"""
YouTube Notes Processing Test

Tests daemon processing of YouTube literature notes with AI enhancement.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from automation.daemon import AutomationDaemon
from automation.config import DaemonConfig, FileWatchConfig
from automation.event_handler import AutomationEventHandler, FileEvent


def main():
    print("=" * 70)
    print("🎬 YouTube Notes Processing Test")
    print("=" * 70)
    print()

    # Test files
    test_files = [
        Path("knowledge/Inbox/lit-20251007-1047-ai-slop-is-killing-our-channel.md.md"),
        Path(
            "knowledge/Inbox/lit-20251007-2227-don-t-start-an-ai-agency-do-this-instead.md.md"
        ),
    ]

    vault_path = Path("knowledge")

    print("📁 Test Files:")
    for f in test_files:
        exists = f.exists()
        print(f"  {'✅' if exists else '❌'} {f.name}")
        if exists:
            size = f.stat().st_size
            print(f"      Size: {size:,} bytes")
    print()

    # Create minimal config
    config = DaemonConfig(
        check_interval=60,
        log_level="INFO",
        file_watching=FileWatchConfig(enabled=False),  # Manual processing
    )

    # Create event handler (this is what processes files)
    print("🔧 Creating event handler...")
    handler = AutomationEventHandler(vault_path=vault_path, config=config)
    print("✅ Event handler created")
    print()

    # Process each file
    for test_file in test_files:
        if not test_file.exists():
            print(f"⚠️  Skipping {test_file.name} - file not found")
            continue

        print(f"📝 Processing: {test_file.name}")
        print("-" * 70)

        # Create file event
        event = FileEvent(path=test_file, event_type="modified", timestamp=None)

        # Process the event
        try:
            result = handler.handle_event(event)

            if result and result.get("success"):
                print(f"✅ Processing successful!")

                if "metadata_validated" in result:
                    print(f"   Metadata validated: {result['metadata_validated']}")

                if "tags_suggested" in result:
                    tags = result.get("tags_suggested", [])
                    print(f"   Tags suggested: {len(tags)} tags")
                    if tags:
                        print(f"      {', '.join(tags[:5])}")

                if "connections_found" in result:
                    conns = result.get("connections_found", 0)
                    print(f"   Connections found: {conns}")

                if "quality_score" in result:
                    score = result.get("quality_score", 0)
                    print(f"   Quality score: {score:.2f}")

            else:
                error = result.get("error", "Unknown error") if result else "No result"
                print(f"❌ Processing failed: {error}")

        except Exception as e:
            print(f"❌ Exception during processing: {e}")
            import traceback

            traceback.print_exc()

        print()

    print("=" * 70)
    print("✅ Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
