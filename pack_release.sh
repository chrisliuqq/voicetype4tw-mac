#!/usr/bin/env bash
set -e

echo "清理舊的構建檔案..."
rm -rf build dist
rm -f Release.zip

echo "使用 py2app 進行打包..."
python3 setup.py py2app

echo "移除本機已知的 Quarantine 標籤（減少打包殘留）..."
xattr -cr dist/VoiceType4TW-Mac.app

echo "建立發布資料夾..."
mkdir -p release_pack
mv dist/VoiceType4TW-Mac.app release_pack/
cp 首次開啟必看_解除損毀警告.md release_pack/

echo "將應用程式打包成 ZIP..."
cd release_pack
zip -r ../VoiceType4TW-Mac-Release.zip *
cd ..
rm -rf release_pack

echo "打包完成！檔案位於 VoiceType4TW-Mac-Release.zip"
