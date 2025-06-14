# CSS to hide password visibility toggles across social media platforms
HIDE_PASSWORD_BUTTON_CSS = """
        /* Hide password visibility buttons across social media platforms */

        /* Instagram */
        button[aria-label*="Show password" i],
        button[aria-label*="Hide password" i],
        button[aria-label*="Reveal password" i],
        button[aria-label*="Toggle password visibility" i],
        button[aria-label*="Show" i],
        button[title*="Show password" i],
        button[title*="Hide password" i],
        button[title*="Reveal password" i],
        button[title*="Show" i],
        div[role="button"][aria-label*="Show password" i],
        div[role="button"][aria-label*="Hide password" i],
        svg[aria-label*="Show password" i],
        svg[aria-label*="Hide password" i],
        svg[aria-label*="Reveal password" i],
        [class*="showPassword" i],
        [class*="hidePassword" i],
        [class*="togglePassword" i],
        [class*="password-toggle" i],
        [class*="password-reveal" i],
        [data-testid*="password-toggle" i],
        [data-testid*="show-password" i],
        [data-testid*="PasswordToggle" i],
        .eye-icon,
        .password-eye,
        .show-password-btn,
        ._acao,
        ._aswq {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* Additional selectors for other platforms */
        input[type="password"] + button,
        input[type="password"] + div[role="button"],
        .password-field button,
        .password-input button,
        .form-control + button[type="button"],
        button[aria-describedby*="password"],
        [data-role="password-toggle"],
        [data-testid*="eye"],
        [aria-label*="eye" i] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
    """
