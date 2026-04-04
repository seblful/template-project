"""Script to set up the project structure and initial configuration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from {{ package_name }}.settings import settings
from {{ package_name }}.logging import setup_logging
import structlog


def main():
    """Set up the project."""
    print("Setting up {{ project_name }}...")

    for dir_path in [settings.paths.data_dir, settings.paths.logs_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    print(f"✓ Created directories:")
    print(f"  - {settings.paths.data_dir}")
    print(f"  - {settings.paths.logs_dir}")

    setup_logging()

    logger = structlog.get_logger(__name__)
    logger.info("Project setup completed successfully")

    print(f"\n✓ Project setup completed!")
    print(f"  Application: {settings.app.app_name}")
    print(f"  Version: {settings.app.app_version}")
    print(f"  Environment: {settings.app.environment}")
    print(f"  Log Level: {settings.logging.log_level}")

    env_file = Path(".env")
    if not env_file.exists():
        print(f"\n⚠ Warning: No .env file found.")
        print(f"  Copy .env.example to .env and configure as needed:")
        print(f"  cp .env.example .env")

    return 0


if __name__ == "__main__":
    sys.exit(main())
