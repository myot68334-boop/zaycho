# Mobile Packaging

This folder contains native wrapper scaffolds for publishing Lyra Shop as mobile apps.

## iOS

Location:

- [`mobile/ios`](/Users/myothant/Documents/New%20project/mobile/ios)

Notes:

- Built as a lightweight `WKWebView` container around the live app.
- Set `APP_BASE_URL` in [`mobile/ios/project.yml`](/Users/myothant/Documents/New%20project/mobile/ios/project.yml) before archiving.
- Recommended deployment target can be adjusted in `project.yml`.
- Generate the Xcode project with `xcodegen generate`.

## Android

Location:

- [`mobile/android`](/Users/myothant/Documents/New%20project/mobile/android)

Notes:

- Built as a `WebView` app with pull-to-refresh, back navigation handling, and file chooser support for admin image upload.
- Set `APP_URL` as a Gradle property or `PUBLIC_BASE_URL` environment variable before release build.
- Open in Android Studio and let it generate the Gradle wrapper if needed.
- Build a signed release App Bundle for Play upload.
