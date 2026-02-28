#!/usr/bin/env bash
set -e

APP="dist/VoiceType4TW-Mac.app"
FRAMEWORKS="$APP/Contents/Frameworks"
PYFW="/Library/Frameworks/Python.framework/Versions/3.12/lib"

echo "=== [1/8] 清理舊的構建檔案 ==="
rm -rf build dist
rm -f VoiceType4TW-Mac-Release.zip

echo "=== [2/8] 使用 py2app 進行打包 ==="
python3 setup.py py2app

echo "=== [3/8] 修復 _ssl.so 的 dylib 連結路徑 ==="
# py2app 會把 _ssl.so 的連結從絕對路徑改成 @executable_path，
# 但複製進 bundle 的 libssl/libcrypto 經常變成 x86_64，無法在 arm64 上運行。
# 解法：用 install_name_tool 把連結改回系統 Python Framework 的絕對路徑，
#       然後刪除 bundle 內多餘的副本，保持 bundle 簽名完整性。
SSL_SO=$(find "$APP" -name "_ssl*.so" | head -1)
if [ -n "$SSL_SO" ]; then
    echo "  找到 _ssl: $SSL_SO"
    install_name_tool -change @executable_path/../Frameworks/libssl.3.dylib "$PYFW/libssl.3.dylib" "$SSL_SO" 2>/dev/null || true
    install_name_tool -change @executable_path/../Frameworks/libcrypto.3.dylib "$PYFW/libcrypto.3.dylib" "$SSL_SO" 2>/dev/null || true
    echo "  驗證連結:"
    otool -L "$SSL_SO" | grep -E "ssl|crypto"
fi

echo "=== [4/8] 刪除 bundle 內不需要的副本 ==="
rm -f "$FRAMEWORKS/libssl.3.dylib" "$FRAMEWORKS/libcrypto.3.dylib"
# 刪除 X11 相關的 dylib（macOS 不需要 X11 顯示系統）
rm -f "$FRAMEWORKS"/libxcb* "$FRAMEWORKS"/libXau* "$FRAMEWORKS"/libX11*

echo "=== [5/8] 逐一簽名所有 dylib ==="
SIGN_FAIL=0
for f in "$FRAMEWORKS"/*.dylib; do
    codesign --force --sign - --timestamp=none "$f" 2>/dev/null && true || {
        echo "  ⚠️ 無法簽名: $(basename $f)，嘗試刪除..."
        rm -f "$f"
        SIGN_FAIL=$((SIGN_FAIL+1))
    }
done
echo "  已排除 $SIGN_FAIL 個問題 dylib"

echo "=== [6/8] 簽名 .so 與 Framework ==="
find "$APP" -name '*.so' -exec codesign --force --sign - --timestamp=none {} \; 2>/dev/null || true
codesign --force --sign - --timestamp=none "$FRAMEWORKS/Python.framework" 2>/dev/null || true

echo "=== [7/8] 使用 entitlements 簽名整個 App bundle ==="
codesign --force --sign - --timestamp=none --entitlements entitlements.plist "$APP" 2>&1

echo "=== [7b/8] 驗證簽名 ==="
codesign -dvvv "$APP" 2>&1 | grep -E "Identifier|Format|Signature|Sealed|Entitlements"

echo "=== [8/8] 建立發布 ZIP ==="
xattr -cr "$APP"
mkdir -p release_pack
mv "$APP" release_pack/
cp 首次開啟必看_解除損毀警告.md release_pack/

cd release_pack
zip -ry ../VoiceType4TW-Mac-Release.zip *
cd ..
rm -rf release_pack

ls -lh VoiceType4TW-Mac-Release.zip
echo "✅ 打包完成！"
