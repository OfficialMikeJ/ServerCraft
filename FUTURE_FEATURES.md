# ServerCraft - 1.0 & Later Development

This document tracks features deferred for post-1.0 development.

---

## 🔐 Security & Compliance

### Advanced Audit Logging & Compliance
**Priority:** Medium | **Complexity:** Medium | **Timeline:** 2-3 days

**Description:**
Enhanced audit logging system with comprehensive tracking and compliance tools.

**Features:**
- Comprehensive action logging (all CRUD operations, logins, config changes)
- Advanced log filtering & search capabilities
- Export logs (JSON, CSV, PDF formats)
- Log retention policies (30/60/90 days, custom)
- Tamper-proof logs with hash chain
- GDPR/CCPA compliance tools (data export, deletion)

**Technical Requirements:**
- Enhanced AuditLogger class
- Log indexing for fast search
- Hash chain for tamper detection
- Export functionality (multiple formats)

**Deferred Reason:**
Not critical for initial home lab deployment. Basic audit logging already in place from security implementation.

---

## 🔒 Network Security

### IP Whitelist/Blacklist System
**Priority:** Low | **Complexity:** Medium | **Timeline:** 3-4 days

**Description:**
IP-based access control with geographic blocking.

**Features:**
- Per-user IP whitelist
- Global IP blacklist
- CIDR notation support
- Geographic IP blocking (by country)
- Auto-ban after failed login attempts
- VPN/Proxy detection

**Technical Requirements:**
- ipaddress library for validation
- GeoIP database (MaxMind GeoLite2)
- IP middleware for request filtering

**Deferred Reason:**
Not required for home lab environment. Home networks typically use router-level firewall rules.

---

## 📊 Future Categories (To Be Added)

- Monitoring & Analytics
- Automation & Scheduling
- Integration & Connectivity
- Infrastructure Scaling

---

**Last Updated:** Phase 1 - Two-Factor Authentication Complete
**Next Review:** After reaching 1.0 milestone
