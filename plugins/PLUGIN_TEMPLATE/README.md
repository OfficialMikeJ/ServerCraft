# ServerCraft Plugin Template

## Overview
This template provides the structure for creating ServerCraft plugins. Plugins extend the panel with custom features while maintaining security and compatibility.

## Plugin Structure
```
plugin-name/
├── manifest.json       # Plugin metadata and configuration
├── main.py            # Backend API endpoints and logic
├── frontend/          # React components (optional)
│   └── PluginPage.jsx
└── README.md          # Plugin documentation
```

## Getting Started

### 1. Configure manifest.json
- **id**: Unique identifier (lowercase, hyphens only)
- **name**: Display name
- **version**: Semantic versioning (1.0.0)
- **permissions**: Required API access levels
- **routes**: API endpoints your plugin exposes
- **ui**: Frontend integration settings

### 2. Implement Backend (main.py)
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/your-endpoint")
async def your_handler():
    return {"status": "ok"}
```

### 3. Create Frontend (optional)
```jsx
import React from 'react';

const PluginPage = () => {
  return (
    <div>
      <h1>Your Plugin</h1>
    </div>
  );
};

export default PluginPage;
```

## Security Guidelines

### DO:
- ✅ Use ServerCraft API endpoints for data access
- ✅ Validate all user inputs
- ✅ Request minimal permissions needed
- ✅ Handle errors gracefully
- ✅ Log important actions
- ✅ Use environment variables for secrets

### DON'T:
- ❌ Access database directly
- ❌ Store sensitive data in manifest.json
- ❌ Execute system commands without validation
- ❌ Trust user input without sanitization
- ❌ Bypass authentication/authorization

## API Access

Plugins can access ServerCraft API through the provided helper:

```python
# Get servers
servers = await call_servercraft_api('/api/servers', 'GET')

# Create user
result = await call_servercraft_api('/api/users', 'POST', {'email': 'user@example.com'})
```

## Available Permissions

- `servers:read` - View server information
- `servers:write` - Create/modify/delete servers
- `users:read` - View user information
- `users:write` - Manage users
- `files:read` - Read server files
- `files:write` - Upload/modify files
- `settings:read` - View panel settings
- `settings:write` - Modify panel settings

## Testing Your Plugin

1. Package your plugin:
   ```bash
   zip -r my-plugin.zip plugin-name/
   ```

2. Upload via ServerCraft panel:
   - Go to Settings → Themes & Plugins
   - Click "Upload Plugin"
   - Select your .zip file
   - Enable the plugin

3. Test your endpoints:
   ```bash
   curl http://localhost:8001/api/plugins/your-plugin-id/your-endpoint
   ```

## Lifecycle Hooks

```python
def init_plugin(db, config):
    """Called when plugin is enabled"""
    pass

def cleanup_plugin():
    """Called when plugin is disabled"""
    pass
```

## Example Plugins

See the included examples:
- `example-billing-plugin` - Server billing and subscriptions
- `example-subuser-plugin` - Enhanced sub-user management

## Troubleshooting

### Plugin won't load
- Check manifest.json syntax
- Verify all required fields are present
- Check server logs for errors

### API calls failing
- Ensure correct permissions in manifest
- Verify endpoint paths
- Check authentication token

## Support

For plugin development help:
- Check ServerCraft documentation
- Review example plugins
- Contact support team
