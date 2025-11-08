# Server Billing Plugin

Monetize your game servers with flexible billing options.

## Features

- **Per-Slot Pricing**: Charge based on number of player slots
- **Per-Server Pricing**: Fixed price per server
- **Multiple Billing Periods**: 1, 3, 6, and 12-month subscriptions
- **Automatic Renewals**: Optional auto-renewal for subscriptions
- **Subscription Management**: Track active, suspended, and cancelled subscriptions

## Setup

1. Upload and enable the plugin
2. Configure payment gateway settings
3. Create billing plans
4. Users can subscribe to plans for their servers

## API Endpoints

### Get Billing Plans
```bash
GET /api/plugins/servercraft-billing/billing/plans
```

### Create Billing Plan (Admin)
```bash
POST /api/plugins/servercraft-billing/billing/plans
{
  "name": "Basic Plan",
  "pricing_type": "per_slot",
  "price_monthly": 0.50,
  "price_12months": 5.00
}
```

### Subscribe to Plan
```bash
POST /api/plugins/servercraft-billing/billing/subscribe
{
  "server_id": "server-uuid",
  "plan_id": "plan-uuid",
  "billing_period": "3months",
  "slots": 50
}
```

## Usage Example

1. Admin creates a plan:
   - Name: "Premium Server"
   - Type: Per-slot
   - $0.50/month per slot
   - $5/year per slot (bulk discount)

2. User subscribes:
   - Server with 50 slots
   - 12-month period
   - Total: $5 × 50 = $250/year

## Configuration

- `currency`: USD, EUR, GBP, etc.
- `payment_gateway`: stripe, paypal, etc.
- `tax_rate`: Tax percentage (0-100)
