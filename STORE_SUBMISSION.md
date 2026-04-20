# Microsoft Store submission walkthrough

This guide takes you from "I have built `dist\CyberpunkClock.msix`" to a live
Store listing. Read it once before your first submission.

---

## 1. Register a Microsoft Partner Center account

1. Go to <https://partner.microsoft.com/dashboard/registration> and sign in
   with the Microsoft account you want to publish under.
2. Choose the **Individual** account type unless you publish for a company.
3. Pay the one-time registration fee. Microsoft has lowered or waived this
   fee for individuals in some regions; the price will be shown at signup.
4. Wait for verification (usually a few hours, sometimes a few days).

After approval you will see a **Publisher display name**, **Publisher ID**
(`CN=...`), and your account dashboard.

## 2. Reserve the app name

1. In Partner Center: **Apps and games -> New product -> MSIX or PWA app**.
2. Reserve the name `Cyberpunk World Clock` (or another name if taken).
3. Open the new product, then **Product identity** in the left nav.
4. Copy the three values shown there:
    * `Package/Identity/Name`            -> `PACKAGE_IDENTITY_NAME`
    * `Package/Identity/Publisher`       -> `PUBLISHER_ID`           (the bit after `CN=`)
    * `Package/Properties/PublisherDisplayName` -> `PUBLISHER_DISPLAY_NAME`

## 3. Edit the manifest

Open `build/AppxManifest.xml` and replace the three placeholders:

```xml
<Identity Name="PACKAGE_IDENTITY_NAME"
          Publisher="CN=PUBLISHER_ID"
          Version="1.0.0.0"
          ProcessorArchitecture="x64" />
...
<PublisherDisplayName>PUBLISHER_DISPLAY_NAME</PublisherDisplayName>
```

Commit this file - you only need to do it once.

## 4. Build the MSIX

```powershell
powershell -ExecutionPolicy Bypass -File build\build_msix.ps1 -Version 1.0.0.0
```

Output: `dist\CyberpunkClock.msix`. The Store re-signs the package, so you do
NOT need a code-signing certificate for submission.

Bump `-Version` (e.g. `1.0.1.0`) for every new submission; the last
segment must stay `0`.

## 5. Submit in Partner Center

1. In your reserved app, open **Submissions -> Start your submission**.
2. **Pricing and availability**: choose `Free` and the markets you want.
3. **Properties**: pick `Utilities` as the category, accept default age
   rating questionnaire (this app has no user-generated content, ads, or
   data collection - all answers are "No").
4. **Age ratings**: complete the IARC questionnaire. For a clock widget
   the result will be 3+ in every market.
5. **Packages**: drag and drop `dist\CyberpunkClock.msix`. Wait for the
   automated validation to pass (a few minutes).
6. **Store listings -> English (United States)**:
    * Description: paste from `README.md` or rewrite.
    * Screenshots: at least one 1366x768 or larger PNG. Take a screenshot
      of the running widget on your desktop with **Win + Shift + S** and
      crop.
    * Store logos are pulled from the MSIX automatically.
7. **Submit for certification**.

Certification typically takes a few hours to 1-2 business days. If
something fails, Partner Center will tell you exactly which test failed
and what to fix.

## 6. Updates

For every release:

1. Update version: `git tag v1.0.1` (this also triggers the GitHub
   Release for the .exe build).
2. Build a new MSIX: `build\build_msix.ps1 -Version 1.0.1.0`.
3. In Partner Center: **Update** on the existing app, drop the new MSIX.

---

## Common gotchas

| Problem                                                | Fix                                                                   |
|--------------------------------------------------------|-----------------------------------------------------------------------|
| `Identity name does not match`                         | Re-copy `PACKAGE_IDENTITY_NAME` from Partner Center -> Product identity. |
| `Publisher does not match`                             | The `CN=` value must match exactly, including spaces and quoting.     |
| `Version segment 4 must be 0`                          | Use `1.2.3.0`, never `1.2.3.1`.                                       |
| Cert validation fails                                  | Don't sign for Store submission. Pass `-Sign` only for sideload.      |
| `runFullTrust capability requires approval`            | Mention in the submission notes that this is a packaged Win32 (PyQt6) app. Approval is automatic for desktop apps. |
| Startup toggle does not appear                         | Users enable it themselves in **Settings -> Apps -> Startup**.        |

## Optional: sideload-test the MSIX before submitting

```powershell
# one-time: create a self-signed cert
$cert = New-SelfSignedCertificate -Type Custom -Subject "CN=PUBLISHER_ID" `
        -KeyUsage DigitalSignature -FriendlyName "CyberpunkClock Sideload" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3","2.5.29.19={text}")
$pwd = ConvertTo-SecureString -String "test" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath build\testcert.pfx -Password $pwd

# then on every build:
powershell -ExecutionPolicy Bypass -File build\build_msix.ps1 -Sign -CertPassword test
```

Trust the cert (Local Machine -> Trusted People), then double-click the
`.msix` to install.
