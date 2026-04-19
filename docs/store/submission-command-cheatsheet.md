# ZayCho Submission Command Cheat Sheet

This file is the quickest path for local packaging work before App Store Connect or Play Console upload.

## iOS

### 1. Regenerate the Xcode project

```bash
cd "/Users/myothant/Documents/New project/mobile/ios"
xcodegen generate
```

### 2. Open the project in Xcode

```bash
open "/Users/myothant/Documents/New project/mobile/ios/ZayCho.xcodeproj"
```

### 3. Archive build from terminal

Use this after you set your Apple Team ID and signing in Xcode:

```bash
xcodebuild \
  -project "/Users/myothant/Documents/New project/mobile/ios/ZayCho.xcodeproj" \
  -scheme "ZayCho" \
  -configuration Release \
  -destination "generic/platform=iOS" \
  -archivePath "/Users/myothant/Documents/New project/mobile/ios/build/ZayCho.xcarchive" \
  archive
```

### 4. Export archive after creating an ExportOptions plist

Use the included file at [`mobile/ios/ExportOptions.plist`](/Users/myothant/Documents/New%20project/mobile/ios/ExportOptions.plist) after replacing `YOUR_TEAM_ID`.

```bash
xcodebuild \
  -exportArchive \
  -archivePath "/Users/myothant/Documents/New project/mobile/ios/build/ZayCho.xcarchive" \
  -exportOptionsPlist "/Users/myothant/Documents/New project/mobile/ios/ExportOptions.plist" \
  -exportPath "/Users/myothant/Documents/New project/mobile/ios/build/export"
```

## Android

### 1. Create a keystore

```bash
keytool -genkeypair \
  -v \
  -keystore "/Users/myothant/Documents/New project/mobile/android/release-keystore.jks" \
  -alias "zaycho-release" \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storetype JKS \
  -dname "CN=ZayCho, OU=Mobile, O=ZayCho, L=Tokyo, ST=Tokyo, C=JP"
```

### 2. Copy and edit the keystore config

```bash
cp "/Users/myothant/Documents/New project/mobile/android/keystore.properties.example" "/Users/myothant/Documents/New project/mobile/android/keystore.properties"
```

### 3. Build the signed App Bundle

If Gradle wrapper is available:

```bash
cd "/Users/myothant/Documents/New project/mobile/android"
./gradlew bundleRelease
```

If you are using Android Studio, open the project and build the signed bundle from the GUI.

## Render

### Push current main branch

```bash
cd "/Users/myothant/Documents/New project"
git push origin main
```

### Check live URLs after deploy

- https://zaycho.onrender.com
- https://zaycho.onrender.com/privacy
- https://zaycho.onrender.com/support
