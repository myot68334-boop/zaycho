# Android Signed AAB Setup

Default package ID:

- `com.myot68334.zaycho`

## Keystore setup

Copy the example file:

```bash
cp "/Users/myothant/Documents/New project/mobile/android/keystore.properties.example" "/Users/myothant/Documents/New project/mobile/android/keystore.properties"
```

Fill in:

- `storeFile`
- `storePassword`
- `keyAlias`
- `keyPassword`

You can also provide the same values through environment variables:

- `ZAYCHO_KEYSTORE_PATH`
- `ZAYCHO_KEYSTORE_PASSWORD`
- `ZAYCHO_KEY_ALIAS`
- `ZAYCHO_KEY_PASSWORD`

Generate a release keystore:

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

## Build

Open the Android project in Android Studio and build a signed release App Bundle.

If Gradle wrapper is available:

```bash
cd "/Users/myothant/Documents/New project/mobile/android"
./gradlew bundleRelease
```

Recommended output:

- `app-release.aab`

## Store URLs

- Support URL: `https://zaycho.onrender.com/support`
- Privacy Policy URL: `https://zaycho.onrender.com/privacy`
