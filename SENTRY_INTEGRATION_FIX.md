# Sentry Integration Fix

## Issue
The backend application was failing to start with the following error:
```
TypeError: StarletteIntegration.__init__() got an unexpected keyword argument 'auto_enabling'
```

This error occurred in `/app/main.py` at line 30 when trying to initialize the FastApiIntegration with an unsupported parameter.

## Root Cause
The `FastApiIntegration` class (which inherits from `StarletteIntegration`) does not support the `auto_enabling` parameter. This parameter was incorrectly used in the initialization.

## Fix Applied
Removed the unsupported `auto_enabling` parameter from the FastApiIntegration initialization in `backend/main.py`.

### Changed from:
```python
FastApiIntegration(auto_enabling=True),
```

### Changed to:
```python
FastApiIntegration(),
```

## Technical Details
- **File Modified**: `backend/main.py` (line 29)
- **Sentry SDK Version**: `sentry-sdk[fastapi]==1.38.0`
- **Fix Type**: Parameter removal - the integration works correctly without any parameters

## Verification
After this fix, the backend service should start successfully without the TypeError. The Sentry integration will still function properly for error tracking and monitoring.

## Date
Fix applied on: $(date)