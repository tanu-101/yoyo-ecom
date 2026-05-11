# Security Best Practices

## Authentication

### JWT Configuration

```python
# settings/base.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}
```

### Password Validation

```python
# settings/base.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

## Authorization

### Permission Classes

```python
from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'staff']
```

### Object-Level Permissions

```python
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False
```

## Input Validation

### Serializer Validation

```python
from rest_framework import serializers

class OrderCreateSerializer(serializers.Serializer):
    items = serializers.ListField(min_length=1)
    shipping_address = serializers.DictField()

    def validate_items(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Maximum 100 items per order")
        return value

    def validate_shipping_address(self, value):
        required_fields = ['street', 'city', 'country', 'postal_code']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing field: {field}")
        return value
```

## SQL Injection Prevention

Django ORM is protected against SQL injection. Avoid raw SQL:

```python
# SAFE - Using ORM
products = Product.objects.filter(name__icontains=query)

# SAFE - Using parameterized query
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM products WHERE name = %s", [query])

# DANGEROUS - Raw string interpolation (never do this)
Product.objects.raw(f"SELECT * FROM products WHERE name = '{query}'")
```

## XSS Prevention

Django templates auto-escape output. DRF serializers also escape output:

```python
# Template: {{ user_name }} - automatically escaped
# Serializer: automatically escaped
```

## CSRF Protection

```python
# settings/base.py
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
]

# For API with JWT, disable CSRF for stateless endpoints
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

## CORS Configuration

```python
# settings/base.py
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://app.yourdomain.com',
]

CORS_ALLOW_CREDENTIALS = True
```

## Data Privacy

### Sensitive Fields

Never log or expose sensitive data:

```python
# BAD - Logging sensitive data
logger.info(f"User {user.email} logged in with password {password}")

# GOOD - Log without sensitive data
logger.info(f"User {user.email} login attempt")
```

### Environment Variables

Never commit secrets to version control:

```bash
# .gitignore
.env
.env.local
*.pem
*.key
credentials.json
```

## Stripe Webhook Security

```python
# apps/payments/webhooks.py
import stripe
from django.conf import settings

def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Process event
    return HttpResponse(status=200)
```

## Rate Limiting

```python
# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute',
    }
}
```

## Security Headers

```python
# settings/base.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## File Upload Security

```python
# Validate file uploads
def validate_image(image):
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError("Unsupported file extension")

    # Check file size (max 5MB)
    if image.size > 5 * 1024 * 1024:
        raise ValidationError("File size exceeds 5MB")

    # Validate content type
    if image.content_type not in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
        raise ValidationError("Invalid content type")

    return image
```

## Dependency Security

```bash
# Check for vulnerabilities
pip audit

# Update dependencies
pip list --outdated
pip install -U package_name
```

## Common Security Checklist

- [ ] Use HTTPS in production
- [ ] Enable secure cookies (HTTPS only)
- [ ] Set appropriate session timeout
- [ ] Implement rate limiting
- [ ] Validate all user input
- [ ] Use parameterized queries
- [ ] Implement proper authentication
- [ ] Set up proper authorization
- [ ] Enable CSRF protection
- [ ] Configure CORS properly
- [ ] Don't log sensitive data
- [ ] Use environment variables for secrets
- [ ] Keep dependencies updated
- [ ] Run security audits regularly