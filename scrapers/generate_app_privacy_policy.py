privacy_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - CampFind</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; line-height: 1.6; color: #1A1A2E; max-width: 800px; margin: 0 auto; padding: 30px 20px; background-color: #FAFAFD; }
        h1 { color: #FF6B6B; border-bottom: 2px solid #FF6B6B; padding-bottom: 10px; }
        h2 { color: #4ECDC4; margin-top: 25px; }
        p, li { color: #5A6A7C; }
        .box { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    </style>
</head>
<body>
    <div class="box">
        <h1>CampFind Privacy Policy</h1>
        <p><strong>Effective Date:</strong> July 29, 2026</p>
        <p>Welcome to <strong>CampFind</strong> ("we," "our," or "us"), owned and operated by Wingsoar Studio. We are committed to protecting your privacy while helping parents discover and compare ACA-accredited summer and winter camps across North America.</p>
        
        <h2>1. Information We Collect</h2>
        <p>CampFind collects minimal information required to provide location-based camp search services:</p>
        <ul>
            <li><strong>Location Data:</strong> Optional ZIP Code or city search parameters entered by the user to calculate camp distance.</li>
            <li><strong>Account Information:</strong> Account email address when opting into Pro Subscriptions via Google Play Store.</li>
        </ul>

        <h2>2. How We Use Information</h2>
        <p>We use collected information solely to:</p>
        <ul>
            <li>Provide relevant camp search results and side-by-side comparisons.</li>
            <li>Process subscription status via official Google Play Billing API.</li>
        </ul>

        <h2>3. Third-Party Services</h2>
        <p>CampFind integrates official third-party SDKs including Google Play Billing and Firebase Analytics, which handle user authentication and in-app purchases securely in compliance with Google Play Developer Policies.</p>

        <h2>4. Contact Us</h2>
        <p>If you have any questions regarding this Privacy Policy, please contact Wingsoar Studio at <strong>wingsoar2023@gmail.com</strong>.</p>
    </div>
</body>
</html>
"""

with open('app/privacy.html', 'w', encoding='utf-8') as f:
    f.write(privacy_html)

print("Created app/privacy.html Privacy Policy document.")
