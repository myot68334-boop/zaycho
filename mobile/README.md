# Mobile Packaging

This folder contains native wrapper scaffolds for publishing ZayCho as mobile apps.

## iOS

Location:

- [`mobile/ios`](/Users/myothant/Documents/New%20project/mobile/ios)

Notes:

- Built as a lightweight `WKWebView` container around the live app.
- Recommended deployment target can be adjusted in `project.yml`.
- Generate the Xcode project with `xcodegen generate`.

## Android

Location:

- [`mobile/android`](/Users/myothant/Documents/New%20project/mobile/android)

Notes:

- Built as a `WebView` app with pull-to-refresh and back navigation handling.
- Open in Android Studio and let it generate the Gradle wrapper if needed.
- Build a signed release App Bundle for Play upload.
