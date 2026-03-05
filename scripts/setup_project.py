"""Script to set up the project structure and initial configuration."""

import sys
from pathlib import Path

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings, setup_logging, get_logger


def main():
    """Set up the project."""
    print("Setting up Template Project...")

    # Get settings and ensure directories exist
    settings = get_settings()
    settings.ensure_directories()

    print(f"✓ Created directories:")
    print(f"  - {settings.data_dir}")
    print(f"  - {settings.logs_dir}")
    print(f"  - {settings.models_dir}")

    # Setup logging
    setup_logging()

    # Get logger and log setup completion
    logger = get_logger(__name__)
    logger.info("Project setup completed successfully")

    print(f"\n✓ Project setup completed!")
    print(f"  Application: {settings.app_name}")
    print(f"  Version: {settings.app_version}")
    print(f"  Environment: {settings.environment}")
    print(f"  Log Level: {settings.log_level}")

    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print(f"\n⚠ Warning: No .env file found.")
        print(f"  Copy .env.example to .env and configure as needed:")
        print(f"  cp .env.example .env")

    return 0


if __name__ == "__main__":
    sys.exit(main())
