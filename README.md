# Webex Teams MCP Server

A Model Context Protocol (MCP) server that enables Claude Desktop to interact with Cisco Webex Teams. Send messages, manage spaces, and automate team collaboration directly from Claude.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

## ✨ Features

- 🚀 **11 Powerful Tools** for complete Webex Teams integration
- 💬 **Messaging**: Send, retrieve, and delete messages with Markdown support
- 👥 **Space Management**: Create, search, and manage team spaces
- 🤝 **People Management**: Add members, list participants, and get user details
- 🔒 **Secure**: Uses official Webex Teams API with bot tokens
- ⚡ **Async**: Built with async/await for optimal performance

## 📋 Prerequisites

- **Python 3.10+** installed
- **Webex Teams Account** (free at https://www.webex.com/)
- **Webex Bot Token** or Personal Access Token
- **Claude Desktop** installed

## 🚀 Quick Start

### 1. Get a Webex Bot Token

**Option A: Create a Bot (Recommended for production)**
1. Go to https://developer.webex.com/my-apps/new/bot
2. Fill in bot details and create the bot
3. **Copy the Bot Access Token** immediately (you won't see it again!)
4. Add the bot to your Webex spaces

**Option B: Personal Access Token (For testing only)**
1. Go to https://developer.webex.com/docs/getting-started
2. Your token is displayed after logging in
3. ⚠️ **Warning**: Personal tokens expire after 12 hours

### 2. Install

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/webex-mcp-server.git
cd webex-mcp-server

# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Claude Desktop

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "webex": {
      "command": "/FULL/PATH/TO/venv/bin/python",
      "args": [
        "/FULL/PATH/TO/webex-mcp-server/src/webex_mcp_server.py"
      ],
      "env": {
        "WEBEX_ACCESS_TOKEN": "YOUR_WEBEX_BOT_TOKEN_HERE"
      }
    }
  }
}
```

**Important Notes:**
- Replace `/FULL/PATH/TO/` with your actual absolute path
- Replace `YOUR_WEBEX_BOT_TOKEN_HERE` with your actual token
- On macOS, use `/venv/bin/python`
- On Windows, use `\venv\Scripts\python.exe`

### 4. Restart Claude Desktop

Completely quit and restart Claude Desktop to load the MCP server.

### 5. Test It!

In Claude Desktop, try:
```
Can you list my Webex spaces?
```

You should see your Webex spaces listed! 🎉

## 🛠️ Available Tools

### Messaging
- **send_message** - Send text or Markdown messages to spaces
- **get_messages** - Retrieve conversation history
- **delete_message** - Remove messages (with permissions)

### Space Management
- **list_spaces** - List all accessible spaces
- **get_space_details** - Get detailed space information
- **create_space** - Create new team spaces
- **search_spaces** - Find spaces by name

### People Management
- **add_person_to_space** - Add members to spaces
- **list_space_members** - List all space participants
- **get_person_details** - Get user information
- **get_my_details** - Get bot/user account info

## 💡 Usage Examples

### Send a Message
```
Send a message to my "Project Alpha" space saying "Meeting starts in 5 minutes!"
```

### Create a Space
```
Create a new Webex space called "Q1 Planning" and add john@company.com as a member.
```

### Get Space Messages
```
Show me the last 10 messages from my "Engineering Team" space.
```

### Search for Spaces
```
Find all my Webex spaces that contain "customer" in the name.
```

## 🔧 Advanced Configuration

### Multiple MCP Servers

If you have other MCP servers (like Splunk), combine them:

```json
{
  "mcpServers": {
    "webex": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/webex_mcp_server.py"],
      "env": {
        "WEBEX_ACCESS_TOKEN": "YOUR_TOKEN"
      }
    },
    "splunk": {
      "command": "node",
      "args": ["splunk-server.js"]
    }
  }
}
```

### Environment Variables

Instead of putting the token in the config, use environment variables:

```json
{
  "mcpServers": {
    "webex": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/webex_mcp_server.py"],
      "env": {
        "WEBEX_ACCESS_TOKEN": "${WEBEX_TOKEN}"
      }
    }
  }
}
```

Then set `WEBEX_TOKEN` in your system environment.

## 🐛 Troubleshooting

### "Server not found" in Claude Desktop

1. Check that paths in `claude_desktop_config.json` are absolute (not relative)
2. Verify the Python virtual environment path is correct
3. Restart Claude Desktop completely (quit, don't just close window)

### "Authentication failed" errors

1. Verify your `WEBEX_ACCESS_TOKEN` is correct
2. Check that the token hasn't expired (personal tokens expire in 12 hours)
3. Ensure the bot has been added to spaces you're trying to access

### "Permission denied" errors

1. Bot tokens need to be added to spaces before they can interact
2. Some operations require moderator permissions
3. Check bot has necessary scopes in the Webex Developer portal

### Connection test

Create a test script:

```python
import os
from webexteamssdk import WebexTeamsAPI

token = os.getenv("WEBEX_ACCESS_TOKEN")
api = WebexTeamsAPI(access_token=token)

# Test connection
me = api.people.me()
print(f"✅ Connected as: {me.displayName}")

# List spaces
rooms = list(api.rooms.list(max=5))
print(f"✅ Found {len(rooms)} spaces")
```

## 🏗️ Development

### Project Structure

```
webex-mcp-server/
|── webex_mcp_server.py         # Main MCP server
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # MIT License
```

### Running in Development

```bash
# Activate virtual environment
source venv/bin/activate

# Set token
export WEBEX_ACCESS_TOKEN="your_token_here"

# Run server directly
python src/webex_mcp_server.py
```

### Adding New Tools

1. Define the tool in `list_tools()`
2. Create a handler function `handle_your_tool(args)`
3. Add the handler to `call_tool()`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [Webex Developer Portal](https://developer.webex.com/)
- [Create Webex Bot](https://developer.webex.com/my-apps/new/bot)
- [Webex API Documentation](https://developer.webex.com/docs/api/getting-started)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/download)

## 🙏 Acknowledgments

- Built for integration with [Claude Desktop](https://claude.ai/download)
- Uses the official [Webex Teams SDK](https://github.com/CiscoDevNet/webexteamssdk)
- Implements the [Model Context Protocol](https://modelcontextprotocol.io/)

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/webex-mcp-server/issues)
- **Webex Support**: [Webex Developer Support](https://developer.webex.com/support)
- **MCP Protocol**: [MCP Documentation](https://modelcontextprotocol.io/)

---

**Made with ❤️ for the Cisco community**
