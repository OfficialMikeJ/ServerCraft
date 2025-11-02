# ServerCraft Plugin & Theme Security Guidelines

## Overview
This document outlines the security restrictions and best practices for developing plugins and themes for ServerCraft. These guidelines ensure the safety and integrity of the game server panel while allowing community extensions.

---

## ✅ ALLOWED Features

### Plugins CAN:

1. **UI Extensions**
   - Add custom dashboard widgets
   - Create new menu items
   - Add custom pages and views
   - Modify existing UI components (within bounds)
   - Add custom forms and input fields

2. **API Integration**
   - Register custom API endpoints (sandboxed)
   - Use provided SDK methods
   - Access plugin-specific database collections
   - Make HTTP requests to external services (with user consent)
   - Subscribe to panel events/webhooks

3. **Data Visualization**
   - Create custom charts and graphs
   - Display server statistics
   - Show monitoring data
   - Generate reports

4. **Notifications & Alerts**
   - Send toast notifications
   - Create email alerts (using panel's email service)
   - Discord/Slack webhooks
   - Custom alert conditions

5. **Server Extensions**
   - Add support for new game servers
   - Custom server configuration templates
   - Server monitoring scripts
   - Backup automation

6. **Theme Customization**
   - Custom color schemes
   - Font selections
   - Layout modifications
   - CSS/styling changes
   - Logo and branding

---

## ❌ PROHIBITED Actions

### Plugins MUST NOT:

1. **Database Access**
   - ❌ Direct MongoDB connections
   - ❌ Raw database queries
   - ❌ Access to other plugins' data
   - ❌ Modification of core tables
   - ✅ ONLY use Plugin SDK for data operations

2. **System-Level Operations**
   - ❌ File system access outside plugin directory
   - ❌ Execute shell commands
   - ❌ Modify system files
   - ❌ Access environment variables
   - ❌ Spawn processes
   - ❌ Docker socket access (unless explicitly granted)

3. **Security Violations**
   - ❌ Credential harvesting
   - ❌ Token stealing
   - ❌ Password logging
   - ❌ Session hijacking
   - ❌ XSS injection
   - ❌ SQL injection attempts

4. **Network Operations**
   - ❌ Port scanning
   - ❌ Network sniffing
   - ❌ Unauthorized API calls to panel endpoints
   - ❌ DDoS or flooding attempts
   - ❌ Proxy/VPN establishment

5. **Resource Abuse**
   - ❌ Cryptocurrency mining
   - ❌ Excessive CPU/memory consumption
   - ❌ Infinite loops
   - ❌ Memory leaks
   - ❌ Background processes without disclosure

6. **Code Execution**
   - ❌ eval() or similar dynamic code execution
   - ❌ Arbitrary code from external sources
   - ❌ Unsafe deserialization
   - ❌ Code injection

---

## 🔒 Plugin Security Requirements

### 1. Sandboxing
All plugins run in an isolated environment with:
- Limited filesystem access (only `/plugins/<plugin-name>/` directory)
- Restricted API access (only SDK-provided methods)
- Memory and CPU limits
- Network request monitoring

### 2. Permission System
Plugins must declare required permissions in `plugin.json`:
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "permissions": [
    "api.read_servers",
    "api.write_servers",
    "ui.add_menu_item",
    "network.external_requests"
  ]
}
```

### 3. Code Review Process
**Community Plugins (Free):**
- Automated security scanning
- Community peer review
- Manual review for high-risk permissions

**Premium Plugins (Paid by Mike):**
- Comprehensive security audit
- Penetration testing
- Code signing with certificate
- Guaranteed security standards

### 4. Digital Signing
All marketplace plugins must be digitally signed:
- Ensures code integrity
- Prevents tampering
- Verifies publisher identity

---

## 🎨 Theme Restrictions

### Themes CAN:
- Modify CSS stylesheets
- Change color schemes
- Adjust layouts using CSS Grid/Flexbox
- Add custom fonts (hosted or Google Fonts)
- Include background images/patterns
- Customize component styles

### Themes CANNOT:
- Include JavaScript code
- Modify HTML structure beyond CSS
- Access local storage/cookies
- Make network requests
- Execute any code
- Inject iframes or embeds

---

## 📦 Plugin Marketplace Rules

### Free Community Plugins:
- Open source on GitHub required
- Community voting/rating system
- Free to download and use
- Creator attribution mandatory
- No ads or tracking

### Premium Plugins by Mike:
- One-time purchase fee (set by Mike)
- Closed source allowed
- Priority support included
- Update guarantee
- Money-back option for critical bugs

### Review Process:
1. **Submission** - Developer uploads plugin with documentation
2. **Automated Scan** - Security scanner checks for violations
3. **Manual Review** - Team reviews code (48-72 hours)
4. **Testing** - QA tests functionality
5. **Approval/Rejection** - Decision with feedback
6. **Publication** - Live on marketplace

---

## 🛠️ Plugin SDK (Planned)

The Plugin SDK will provide safe methods for:

```javascript
// Example SDK usage
import { ServerCraftSDK } from '@servercraft/plugin-sdk';

const plugin = new ServerCraftSDK({
  name: 'my-plugin',
  version: '1.0.0'
});

// Safe data operations
plugin.data.get('key');
plugin.data.set('key', 'value');

// UI extensions
plugin.ui.addMenuItem({
  label: 'My Plugin',
  icon: 'puzzle',
  route: '/plugins/my-plugin'
});

// Server operations (with permissions)
plugin.servers.list();
plugin.servers.getStatus(serverId);

// Notifications
plugin.notify.success('Operation completed!');
plugin.notify.error('Something went wrong');

// Events
plugin.on('server.started', (data) => {
  console.log('Server started:', data.serverId);
});
```

---

## 🚨 Violation Consequences

### First Offense:
- Plugin suspension
- Developer warning
- 7-day correction period

### Second Offense:
- Plugin permanent removal
- Developer account restriction
- 30-day marketplace ban

### Critical Violation:
- Immediate permanent ban
- Legal action if malicious
- Report to authorities if criminal

---

## 📋 Submission Checklist

Before submitting a plugin:

- [ ] Code follows security guidelines
- [ ] All permissions declared in manifest
- [ ] Documentation includes setup instructions
- [ ] No prohibited actions used
- [ ] Tested in isolated environment
- [ ] Version number follows semver
- [ ] License specified
- [ ] Contact information provided
- [ ] Privacy policy (if collecting data)
- [ ] Open source link (for free plugins)

---

## 🔐 Best Practices

1. **Principle of Least Privilege**
   - Request only necessary permissions
   - Minimize external dependencies

2. **Input Validation**
   - Sanitize all user inputs
   - Validate data types
   - Prevent injection attacks

3. **Error Handling**
   - Graceful degradation
   - No sensitive data in error messages
   - Log errors appropriately

4. **Data Privacy**
   - Never collect personal data without consent
   - Encrypt sensitive information
   - GDPR compliance

5. **Performance**
   - Optimize database queries
   - Lazy load resources
   - Cache when appropriate
   - Clean up resources

---

## 📞 Support & Questions

- **Security Concerns:** security@servercraft.com
- **Plugin Development:** developers@servercraft.com
- **Marketplace Issues:** marketplace@servercraft.com

---

## 📄 License & Legal

By submitting a plugin to ServerCraft:
- You retain ownership of your code
- You grant ServerCraft right to distribute
- You accept responsibility for security
- You agree to these guidelines
- You accept marketplace terms

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Author:** Mike - ServerCraft Team

---

## Summary

**YES:** UI extensions, safe APIs, themes, notifications, monitoring  
**NO:** Direct DB access, system commands, credential theft, code injection, resource abuse

Security is paramount. When in doubt, ask the ServerCraft team before implementing.
