#!/bin/bash
# Script to use the force-exit endpoint to close user 1003's LENSKART position

# Get auth token
echo "Logging in as admin (9999999999)..."
TOKEN=$(curl -s -X POST https://tradingnexus.pro/api/v2/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"mobile":"9999999999","password":"123456"}' \
  2>/dev/null | jq -r '.token // empty')

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get auth token. Check credentials."
    exit 1
fi

echo "✓ Got token: ${TOKEN:0:20}..."

# First, let's try to find the position ID using the positions endpoint
echo -e "\nSearching for LENSKART positions for user 1003..."

# Call force-exit endpoint
# Need to know the position ID first, so let's try to get it from the positions endpoint
# For now, we can try common position IDs or query the API in a different way

# Let me try to get admin positions using a hypothetical endpoint
POSITIONS_RESPONSE=$(curl -s -X GET "https://tradingnexus.pro/api/v2/admin/positions/userwise" \
  -H "X-AUTH: $TOKEN" \
  2>/dev/null)

echo "Response: $POSITIONS_RESPONSE" | head -c 500

echo -e "\n\nNOTE: To close the position, you need:"
echo "1. User ID: 1003"
echo "2. Position ID: (retrieve from positions list)"
echo "3. Exit Price: (any price, e.g., 380.70)"
echo ""
echo "Then call: curl -X POST https://tradingnexus.pro/api/v2/admin/force-exit \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'X-AUTH: $TOKEN' \\"
echo "  -d '{\"user_id\":\"1003\",\"position_id\":\"<position_id>\",\"exit_price\":380.70}'"
