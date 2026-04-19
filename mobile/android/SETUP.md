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

## Build

Open the Android project in Android Studio and build a signed release App Bundle.

Recommended output:

- `app-release.aab`

## Store URLs

- Support URL: `https://zaycho.onrender.com/support`
- Privacy Policy URL: `https://zaycho.onrender.com/privacy`
