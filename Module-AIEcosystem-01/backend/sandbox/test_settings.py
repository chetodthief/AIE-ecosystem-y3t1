import sys
from pathlib import Path

# เพิ่ม Path ให้ Python รู้จักโฟลเดอร์ backend จะได้ import core.config ได้
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.config import settings

def test_settings():
    print("=== Testing Project Settings ===")
    print(f"App Name:   {settings.app_name}")
    print(f"Debug Mode: {settings.debug_mode}")
    print(f"API Key:    {settings.api_key}")
    print("================================")

if __name__ == "__main__":
    test_settings()