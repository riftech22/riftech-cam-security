#!/bin/bash

###############################################################################
# Simple Telegram Bot Test Script
###############################################################################

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "          🤖 TELEGRAM BOT TEST - SIMPLE VERSION"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check config
if [ ! -f "config.py" ]; then
    echo "❌ Error: config.py not found!"
    exit 1
fi

# Extract credentials
BOT_TOKEN=$(grep "TELEGRAM_BOT_TOKEN" config.py | cut -d'"' -f2)
CHAT_ID=$(grep "TELEGRAM_CHAT_ID" config.py | cut -d'"' -f2 | tr -d '"')

if [ -z "$BOT_TOKEN" ] || [ -z "$CHAT_ID" ]; then
    echo "❌ Error: Telegram credentials not found!"
    exit 1
fi

echo "✓ Bot Token: ${BOT_TOKEN:0:20}...${BOT_TOKEN: -5}"
echo "✓ Chat ID: $CHAT_ID"
echo ""

# Test 1: Get Bot Info
echo "📡 Test 1: Get Bot Info..."
echo "----------------------------------------"
RESPONSE=$(timeout 10 curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe")

if [ $? -eq 0 ] && echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ SUCCESS: Bot connected!"
    echo "   Bot Name: $(echo "$RESPONSE" | grep -o '"first_name":"[^"]*' | cut -d'"' -f4)"
    echo "   Bot Username: @$(echo "$RESPONSE" | grep -o '"username":"[^"]*' | cut -d'"' -f4)"
else
    echo "❌ FAILED: Cannot connect to bot"
    echo "   Response: $RESPONSE"
    exit 1
fi
echo ""

# Test 2: Send Message
echo "📨 Test 2: Send Test Message..."
echo "----------------------------------------"
MESSAGE="🔧 *Telegram Bot Test*

✅ Connection successful!
✅ Bot is working!

Test completed successfully."

RESPONSE=$(timeout 15 curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\": \"$CHAT_ID\", \"text\": \"$MESSAGE\", \"parse_mode\": \"Markdown\"}")

if [ $? -eq 0 ] && echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ SUCCESS: Message sent!"
    echo "   Message ID: $(echo "$RESPONSE" | grep -o '"message_id":[0-9]*' | cut -d':' -f2)"
else
    echo "❌ FAILED: Cannot send message"
    echo "   Response: $RESPONSE"
    echo ""
    echo "Possible reasons:"
    echo "  - User has not started the bot (send /start in Telegram)"
    echo "  - Wrong Chat ID"
    echo "  - Network connection issue"
    echo ""
    echo "To fix:"
    echo "  1. Open Telegram"
    echo "  2. Search for your bot: @$(echo "$RESPONSE" | grep -o '"username":"[^"]*' | cut -d'"' -f4)"
    echo "  3. Send /start"
    echo "  4. Run this script again"
    exit 1
fi
echo ""

# Test 3: Check for Updates
echo "📥 Test 3: Check for New Messages..."
echo "----------------------------------------"
RESPONSE=$(timeout 10 curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates")

if [ $? -eq 0 ]; then
    if echo "$RESPONSE" | grep -q '"ok":true'; then
        RESULT_COUNT=$(echo "$RESPONSE" | grep -o '"result":\[' | wc -l)
        echo "✅ SUCCESS: Can receive messages!"
        echo "   Pending updates: $RESULT_COUNT"
    else
        echo "⚠️  WARNING: Cannot check updates"
        echo "   Response: $RESPONSE"
    fi
else
    echo "⚠️  WARNING: Timeout checking updates"
fi
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════"
echo "               ✅ TESTS COMPLETED!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🎉 Telegram Bot is working!"
echo ""
echo "📋 Next Steps:"
echo "1. Start the security system:"
echo "   ./start_both_servers.sh"
echo ""
echo "2. Send commands in Telegram:"
echo "   /start   - Show welcome message"
echo "   /arm     - ARM the system"
echo "   /status  - Check system status"
echo ""
echo "3. When ARMED, you will receive alerts with photos!"
echo ""
