# Forgot Password Feature - Implementation Guide

## Overview
A complete "Forgot Password" feature has been added to the Job Board application. This feature allows users to reset their account password using email verification codes.

## Features Implemented

### 1. **Email Verification Code System**
- 6-digit verification codes are generated automatically
- Codes expire after 1 hour (configurable via `PASSWORD_RESET_TIMEOUT` in settings)
- Codes can only be used once

### 2. **Password Reset Flow**
1. User clicks "Forgot password?" link on login page
2. Enters their email address
3. Receives an email with a 6-digit verification code
4. Returns to enter code and new password
5. Password is updated securely

### 3. **Security Features**
- Code expiration (1 hour by default)
- One-time use only
- Secure password validation
- CSRF protection on all forms
- Email verification

## Database Changes

### New Model: PasswordResetToken
Located in: `users/models.py`

```python
class PasswordResetToken(models.Model):
    user = models.OneToOneField(User, ...)
    code = models.CharField(max_length=10, unique=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
```

**Migration:** `users/migrations/0006_passwordresettoken.py`

## Configuration

### Email Settings (in `jobboard_project/settings.py`)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''  # Set via environment variable
EMAIL_HOST_PASSWORD = ''  # Set via environment variable
DEFAULT_FROM_EMAIL = 'noreply@jobboard.com'

PASSWORD_RESET_TIMEOUT = 3600  # 1 hour
PASSWORD_RESET_CODE_LENGTH = 6  # digits
```

### Environment Variables Needed
Add these to your `.env` file for production email sending:
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourcompany.com
```

For Gmail:
1. Enable 2-factor authentication
2. Generate an "App Password" at https://myaccount.google.com/apppasswords
3. Use the app password in `EMAIL_HOST_PASSWORD`

## URLs

### New Routes
- **`/forgot-password/`** - Request password reset
- **`/reset-password/`** - Reset password with verification code

### Updated Routes
- **`/login/`** - Now includes "Forgot password?" link

## Files Created/Modified

### Created Files
- `templates/users/forgot_password.html` - Request password reset form
- `templates/users/forgot_password_sent.html` - Confirmation page
- `templates/users/reset_password.html` - Reset password form
- `templates/users/reset_password_success.html` - Success confirmation
- `templates/emails/password_reset.html` - Email template
- `users/migrations/0006_passwordresettoken.py` - Database migration

### Modified Files
- `users/models.py` - Added `PasswordResetToken` model
- `users/forms.py` - Added `ForgotPasswordForm` and `ResetPasswordForm`
- `users/views.py` - Added `ForgotPasswordView` and `ResetPasswordView`
- `users/services.py` - Added `EmailService` class
- `users/urls.py` - Added new URL routes
- `jobboard_project/settings.py` - Added email configuration
- `templates/users/login.html` - Added "Forgot password?" link

## Testing the Feature

### Local Development (Console Email Backend)

1. Comment out `DATABASE_URL` in `.env` to use SQLite locally
2. Ensure `EMAIL_BACKEND` is set to `'django.core.mail.backends.console.EmailBackend'`
3. Run the server: `python manage.py runserver`
4. Visit `http://localhost:8000/login/`
5. Click "Forgot password?"
6. Enter your email address
7. Check the console output to see the verification code
8. Enter the code and new password

### Production Testing (Gmail/Email)

1. Set environment variables:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```
2. Ensure `EMAIL_BACKEND` is set to `'django.core.mail.backends.smtp.EmailBackend'`
3. Test the forgot password flow
4. Check your email for the verification code

## API Details

### ForgotPasswordView
**Endpoint:** `/forgot-password/`

**GET:**
Returns the forgot password request form

**POST:**
- **Parameters:**
  - `email` (required): User's email address
- **Responses:**
  - Success: Redirects to `forgot_password_sent.html`
  - Error: Redisplays form with error message

### ResetPasswordView
**Endpoint:** `/reset-password/`

**GET:**
Returns the password reset form

**POST:**
- **Parameters:**
  - `code` (required): 6-digit verification code
  - `new_password` (required): New password
  - `confirm_password` (required): Confirmation of new password
- **Responses:**
  - Success: Redirects to `reset_password_success.html`
  - Error: Redisplays form with error message

## Key Functions

### PasswordResetToken Methods

```python
@classmethod
def generate_code(cls) -> str
    """Generate a random 6-digit verification code"""

@classmethod
def create_for_user(cls, user) -> PasswordResetToken
    """Create a new password reset token for a user"""

def is_expired(self) -> bool
    """Check if the token is expired"""

def mark_as_used(self)
    """Mark the token as used"""
```

### EmailService Methods

```python
@staticmethod
def send_password_reset_email(user, code) -> bool
    """Send password reset email with verification code"""
    # Returns True if successful, False otherwise
```

## Error Handling

### Handled Scenarios
1. ✅ Email not found - Shows success message (security: doesn't reveal if email exists)
2. ✅ Code expired - Error message with option to request new code
3. ✅ Code already used - Error message with option to request new code
4. ✅ Invalid code - Error message
5. ✅ Passwords don't match - Error message
6. ✅ Weak password - Validation error message
7. ✅ Email delivery failure - Error message

## Customization Options

### Change Code Expiration Time
In `jobboard_project/settings.py`:
```python
PASSWORD_RESET_TIMEOUT = 1800  # 30 minutes instead of 1 hour
```

### Change Code Length
In `jobboard_project/settings.py`:
```python
PASSWORD_RESET_CODE_LENGTH = 8  # 8-digit code instead of 6
```

### Customize Email Template
Edit `templates/emails/password_reset.html` to match your brand

### Add Two-Factor Authentication
Extend the `ResetPasswordView` to require additional verification

## Security Considerations

1. **Codes are unique and one-time use only**
2. **Codes expire after configured timeout**
3. **No information revealed about whether email exists**
4. **Password validation enforced**
5. **CSRF protection on all forms**
6. **Secure email sending with TLS**

## Troubleshooting

### Emails not sending?
- Check `EMAIL_BACKEND` setting
- Verify email credentials in `.env`
- Check Firebase/Gmail app password settings
- Enable "Less secure app access" (if using basic Gmail)

### Code not generating?
- Ensure `secrets` module is available (Python built-in)
- Check `PASSWORD_RESET_CODE_LENGTH` setting

### Migration errors?
- Ensure database is properly configured
- Run: `python manage.py migrate users`
- For local dev: Comment out `DATABASE_URL` to use SQLite

## Next Steps

1. **Configure email settings** in `.env` for production
2. **Test the feature** thoroughly
3. **Customize templates** to match your branding
4. **Consider adding rate limiting** to prevent abuse
5. **Add email logging** for audit purposes
6. **Monitor password reset requests** for security

## References

- Django Password Validation: https://docs.djangoproject.com/en/stable/topics/auth/
- Django Email: https://docs.djangoproject.com/en/stable/topics/email/
- OWASP Password Reset: https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
