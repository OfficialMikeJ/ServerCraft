# Enhanced Sub-User Management Plugin

Advanced sub-user management with granular permissions and security controls.

## Features

### Granular Permissions
- Server-specific access control
- Start/Stop/Restart permissions
- Console access and command execution
- File management (view, upload, edit, delete)
- Backup management
- Full access restriction option

### Account Management
- **Suspend Accounts**: Temporarily disable access
  - Set suspension duration or indefinite
  - Provide suspension reason
  - Auto-unsuspend after duration expires

- **Ban Accounts**: Permanently disable access
  - Specify ban reason
  - Admin can unban if needed

- **IP Blocking**: Block specific IP addresses
  - Add/remove IPs from block list
  - Prevent access from blocked IPs

### Security
- Admins retain full control
- Sub-users cannot receive admin privileges
- Admins can only manage their own sub-users
- Real-time access verification

## Setup

1. Upload and enable the plugin
2. Configure max sub-users per admin
3. Set default permissions
4. Create sub-user accounts

## API Endpoints

### Create Sub-User
```bash
POST /api/plugins/servercraft-enhanced-subuser/subusers
{
  "email": "subuser@example.com",
  "username": "subuser1",
  "permissions": {
    "server_access": ["server-id-1", "server-id-2"],
    "can_start": true,
    "can_stop": true,
    "can_restart": true,
    "can_view_console": true,
    "fully_restricted": false
  }
}
```

### Suspend Sub-User
```bash
PUT /api/plugins/servercraft-enhanced-subuser/subusers/{user_id}/suspend
{
  "reason": "Policy violation",
  "duration_days": 7
}
```

### Ban Sub-User
```bash
PUT /api/plugins/servercraft-enhanced-subuser/subusers/{user_id}/ban
{
  "reason": "Repeated violations"
}
```

### Block IP Address
```bash
POST /api/plugins/servercraft-enhanced-subuser/subusers/{user_id}/ip-block
{
  "ip_address": "192.168.1.100",
  "reason": "Suspicious activity"
}
```

### Update Permissions
```bash
PUT /api/plugins/servercraft-enhanced-subuser/subusers/{user_id}/permissions
{
  "permissions": {
    "can_start": false,
    "can_stop": false,
    "fully_restricted": true
  }
}
```

## Usage Examples

### Scenario 1: Temporary Restriction
A sub-user violated a policy. Suspend for 7 days:
```bash
PUT /subusers/user-123/suspend
{"reason": "Spam in console", "duration_days": 7}
```

### Scenario 2: Security Threat
Detected malicious activity. Ban immediately and block IP:
```bash
PUT /subusers/user-123/ban
{"reason": "Attempted exploit"}

POST /subusers/user-123/ip-block
{"ip_address": "1.2.3.4"}
```

### Scenario 3: Limited Access
Grant read-only access to specific servers:
```json
{
  "permissions": {
    "server_access": ["server-1"],
    "can_view_console": true,
    "can_view_files": true,
    "can_start": false,
    "can_stop": false
  }
}
```

## Permission Reference

| Permission | Description |
|------------|-------------|
| `server_access` | List of accessible server IDs |
| `can_start` | Start servers |
| `can_stop` | Stop servers |
| `can_restart` | Restart servers |
| `can_view_console` | View server console |
| `can_send_commands` | Execute console commands |
| `can_view_files` | Browse server files |
| `can_upload_files` | Upload files |
| `can_edit_files` | Modify files |
| `can_delete_files` | Delete files |
| `can_view_backups` | View backup list |
| `can_create_backups` | Create backups |
| `can_restore_backups` | Restore from backups |
| `fully_restricted` | Deny all access |

## Configuration

- `max_subusers_per_admin`: Maximum sub-users per admin (default: 50)
- `allow_subuser_file_upload`: Global file upload permission (default: false)
- `ban_duration_days`: Default ban duration (default: 30)
