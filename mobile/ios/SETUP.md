# iOS Bundle ID and Signing Setup

Current default values:

- Bundle ID: `com.myot68334.zaycho`
- Team ID placeholder: `YOUR_TEAM_ID`

## Before archive

1. Open [`project.yml`](/Users/myothant/Documents/New%20project/mobile/ios/project.yml)
2. Replace `YOUR_TEAM_ID` with your Apple Developer Team ID
3. If needed, change `PRODUCT_BUNDLE_IDENTIFIER` to your preferred unique identifier
4. Run:

```bash
cd "/Users/myothant/Documents/New project/mobile/ios"
xcodegen generate
```

5. Open `ZayCho.xcodeproj` in Xcode
6. Under Signing & Capabilities:
   - choose your team
   - confirm bundle identifier
   - let Xcode manage provisioning
7. Archive and upload through Organizer

## Notes

- Apple submission still requires a paid Apple Developer account.
- Use the support URL `https://zaycho.onrender.com/support`
- Use the privacy URL `https://zaycho.onrender.com/privacy`
