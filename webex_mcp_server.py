#!/usr/bin/env python3
"""
Webex Teams MCP Server
Enables Claude Desktop to interact with Cisco Webex Teams via MCP protocol
"""

import asyncio
import json
import os
import logging
from typing import Any, Optional
from datetime import datetime

from mcp.server import Server
from mcp.types import Tool, TextContent
from webexteamssdk import WebexTeamsAPI
from webexteamssdk.exceptions import ApiError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webex-mcp-server")

# Initialize MCP server
app = Server("webex-mcp-server")

# Global Webex API client
webex_api: Optional[WebexTeamsAPI] = None


def initialize_webex_client() -> WebexTeamsAPI:
    """Initialize Webex Teams API client from environment variable."""
    access_token = os.getenv("WEBEX_ACCESS_TOKEN")
    
    if not access_token:
        raise ValueError(
            "WEBEX_ACCESS_TOKEN environment variable is required. "
            "Get your token from: https://developer.webex.com/docs/getting-started"
        )
    
    return WebexTeamsAPI(access_token=access_token)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Webex Teams tools."""
    return [
        Tool(
            name="send_message",
            description="Send a message to a Webex Teams space/room. Can send text and optionally mention people.",
            inputSchema={
                "type": "object",
                "properties": {
                    "room_id": {
                        "type": "string",
                        "description": "The ID of the room/space to send the message to"
                    },
                    "text": {
                        "type": "string",
                        "description": "The message text to send (supports Markdown)"
                    },
                    "markdown": {
                        "type": "string",
                        "description": "Optional: Markdown-formatted message (overrides text if provided)"
                    },
                    "person_email": {
                        "type": "string",
                        "description": "Optional: Email of person to mention in the message"
                    }
                },
                "required": ["room_id", "text"]
            }
        ),
        Tool(
            name="list_spaces",
            description="List all Webex Teams spaces/rooms the bot has access to. Returns space IDs, names, and types.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of spaces to return (default: 50)",
                        "default": 50
                    },
                    "type": {
                        "type": "string",
                        "description": "Filter by space type: 'direct' or 'group'",
                        "enum": ["direct", "group"]
                    }
                }
            }
        ),
        Tool(
            name="get_space_details",
            description="Get detailed information about a specific Webex Teams space including title, type, and creation date.",
            inputSchema={
                "type": "object",
                "properties": {
                    "room_id": {
                        "type": "string",
                        "description": "The ID of the room/space"
                    }
                },
                "required": ["room_id"]
            }
        ),
        Tool(
            name="get_messages",
            description="Retrieve recent messages from a Webex Teams space. Returns message content, sender, and timestamps.",
            inputSchema={
                "type": "object",
                "properties": {
                    "room_id": {
                        "type": "string",
                        "description": "The ID of the room/space"
                    },
                    "max_messages": {
                        "type": "integer",
                        "description": "Maximum number of messages to retrieve (default: 20)",
                        "default": 20
                    }
                },
                "required": ["room_id"]
            }
        ),
        Tool(
            name="create_space",
            description="Create a new Webex Teams space/room with specified members.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title/name of the new space"
                    },
                    "team_id": {
                        "type": "string",
                        "description": "Optional: Team ID if creating space within a team"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="add_person_to_space",
            description="Add a person to a Webex Teams space by their email address.",
            inputSchema={
                "type": "object",
                "properties": {
                    "room_id": {
                        "type": "string",
                        "description": "The ID of the room/space"
                    },
                    "person_email": {
                        "type": "string",
                        "description": "Email address of the person to add"
                    },
                    "is_moderator": {
                        "type": "boolean",
                        "description": "Whether to make the person a moderator (default: false)",
                        "default": False
                    }
                },
                "required": ["room_id", "person_email"]
            }
        ),
        Tool(
            name="list_space_members",
            description="List all members in a Webex Teams space including their names, emails, and roles.",
            inputSchema={
                "type": "object",
                "properties": {
                    "room_id": {
                        "type": "string",
                        "description": "The ID of the room/space"
                    }
                },
                "required": ["room_id"]
            }
        ),
        Tool(
            name="get_person_details",
            description="Get detailed information about a person by email or person ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Email address of the person (use email OR person_id)"
                    },
                    "person_id": {
                        "type": "string",
                        "description": "Person ID (use email OR person_id)"
                    }
                }
            }
        ),
        Tool(
            name="delete_message",
            description="Delete a message from a Webex Teams space (requires appropriate permissions).",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The ID of the message to delete"
                    }
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="search_spaces",
            description="Search for Webex Teams spaces by name/title.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Text to search for in space names"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "default": 20
                    }
                },
                "required": ["search_term"]
            }
        ),
        Tool(
            name="get_my_details",
            description="Get information about the authenticated bot/user including name, email, and organization.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from Claude."""
    global webex_api
    
    if webex_api is None:
        webex_api = initialize_webex_client()
    
    try:
        if name == "send_message":
            return await handle_send_message(arguments)
        elif name == "list_spaces":
            return await handle_list_spaces(arguments)
        elif name == "get_space_details":
            return await handle_get_space_details(arguments)
        elif name == "get_messages":
            return await handle_get_messages(arguments)
        elif name == "create_space":
            return await handle_create_space(arguments)
        elif name == "add_person_to_space":
            return await handle_add_person_to_space(arguments)
        elif name == "list_space_members":
            return await handle_list_space_members(arguments)
        elif name == "get_person_details":
            return await handle_get_person_details(arguments)
        elif name == "delete_message":
            return await handle_delete_message(arguments)
        elif name == "search_spaces":
            return await handle_search_spaces(arguments)
        elif name == "get_my_details":
            return await handle_get_my_details(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except ApiError as e:
        error_msg = f"Webex API Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_send_message(args: dict) -> list[TextContent]:
    """Send a message to a Webex space."""
    room_id = args["room_id"]
    text = args["text"]
    markdown = args.get("markdown")
    person_email = args.get("person_email")
    
    message_params = {
        "roomId": room_id,
        "text": text
    }
    
    if markdown:
        message_params["markdown"] = markdown
    
    if person_email:
        person = webex_api.people.list(email=person_email).__next__()
        message_params["toPersonId"] = person.id
    
    message = webex_api.messages.create(**message_params)
    
    result = {
        "message_id": message.id,
        "room_id": message.roomId,
        "text": message.text,
        "created": str(message.created)
    }
    
    return [TextContent(
        type="text",
        text=f"Message sent successfully!\n\n{json.dumps(result, indent=2)}"
    )]


async def handle_list_spaces(args: dict) -> list[TextContent]:
    """List Webex spaces."""
    max_results = args.get("max_results", 50)
    space_type = args.get("type")
    
    params = {"max": max_results}
    if space_type:
        params["type"] = space_type
    
    rooms = list(webex_api.rooms.list(**params))
    
    spaces_info = []
    for room in rooms:
        spaces_info.append({
            "id": room.id,
            "title": room.title,
            "type": room.type,
            "created": str(room.created),
            "lastActivity": str(room.lastActivity) if hasattr(room, 'lastActivity') else None
        })
    
    result = {
        "total_spaces": len(spaces_info),
        "spaces": spaces_info
    }
    
    return [TextContent(
        type="text",
        text=f"Found {len(spaces_info)} spaces:\n\n{json.dumps(result, indent=2)}"
    )]


async def handle_get_space_details(args: dict) -> list[TextContent]:
    """Get details about a specific space."""
    room_id = args["room_id"]
    room = webex_api.rooms.get(room_id)
    
    details = {
        "id": room.id,
        "title": room.title,
        "type": room.type,
        "created": str(room.created),
        "lastActivity": str(room.lastActivity) if hasattr(room, 'lastActivity') else None,
        "creatorId": room.creatorId if hasattr(room, 'creatorId') else None
    }
    
    return [TextContent(
        type="text",
        text=f"Space details:\n\n{json.dumps(details, indent=2)}"
    )]


async def handle_get_messages(args: dict) -> list[TextContent]:
    """Get messages from a space."""
    room_id = args["room_id"]
    max_messages = args.get("max_messages", 20)
    
    messages = list(webex_api.messages.list(roomId=room_id, max=max_messages))
    
    messages_info = []
    for msg in messages:
        messages_info.append({
            "id": msg.id,
            "personEmail": msg.personEmail,
            "text": msg.text,
            "created": str(msg.created)
        })
    
    result = {
        "room_id": room_id,
        "message_count": len(messages_info),
        "messages": messages_info
    }
    
    return [TextContent(
        type="text",
        text=f"Retrieved {len(messages_info)} messages:\n\n{json.dumps(result, indent=2)}"
    )]


async def handle_create_space(args: dict) -> list[TextContent]:
    """Create a new Webex space."""
    title = args["title"]
    team_id = args.get("team_id")
    
    params = {"title": title}
    if team_id:
        params["teamId"] = team_id
    
    room = webex_api.rooms.create(**params)
    
    result = {
        "id": room.id,
        "title": room.title,
        "type": room.type,
        "created": str(room.created)
    }
    
    return [TextContent(
        type="text",
        text=f"Space created successfully!\n\n{json.dumps(result, indent=2)}"
    )]


async def handle_add_person_to_space(args: dict) -> list[TextContent]:
    """Add a person to a space."""
    room_id = args["room_id"]
    person_email = args["person_email"]
    is_moderator = args.get("is_moderator", False)
    
    membership = webex_api.memberships.create(
        roomId=room_id,
        personEmail=person_email,
        isModerator=is_moderator
    )
    
    result = {
        "membership_id": membership.id,
        "room_id": membership.roomId,
        "person_email": membership.personEmail,
        "is_moderator": membership.isModerator
    }
    
    return [TextContent(
        type="text",
        text=f"Person added successfully!\n\n{json.dumps(result, indent=2)}"
    )]


async def handle_list_space_members(args: dict) -> list[TextContent]:
    """List members of a space."""
    room_id = args["room_id"]
    
    memberships = list(webex_api.memberships.list(roomId=room_id))
    
    members_info = []
    for membership in memberships:
        members_info.append({
            "person_email": membership.personEmail,
            "person_display_name": membership.personDisplayName,
            "is_moderator": membership.isModerator,
            "created": str(membership.created)
        })
    
    result = {
        "room_id": room_id,
        "member_count": len(members_info),
        "members": members_info
    }
    
    return [TextContent(
        type="text",
        text=f"Found {len(members_info)} members:\n\n{json.dumps(result, indent=2)}"
    )]


async def handle_get_person_details(args: dict) -> list[TextContent]:
    """Get details about a person."""
    email = args.get("email")
    person_id = args.get("person_id")
    
    if email:
        person = list(webex_api.people.list(email=email))[0]
    elif person_id:
        person = webex_api.people.get(person_id)
    else:
        raise ValueError("Either email or person_id must be provided")
    
    details = {
        "id": person.id,
        "emails": person.emails,
        "displayName": person.displayName,
        "firstName": person.firstName if hasattr(person, 'firstName') else None,
        "lastName": person.lastName if hasattr(person, 'lastName') else None,
        "created": str(person.created)
    }
    
    return [TextContent(
        type="text",
        text=f"Person details:\n\n{json.dumps(details, indent=2)}"
    )]


async def handle_delete_message(args: dict) -> list[TextContent]:
    """Delete a message."""
    message_id = args["message_id"]
    
    webex_api.messages.delete(message_id)
    
    result = {
        "status": "success",
        "message_id": message_id,
        "action": "deleted"
    }
    
    return [TextContent(
        type="text",
        text=f"Message deleted successfully!\n\n{json.dumps(result, indent=2)}"
    )]


async def handle_search_spaces(args: dict) -> list[TextContent]:
    """Search for spaces by name."""
    search_term = args["search_term"].lower()
    max_results = args.get("max_results", 20)
    
    all_rooms = list(webex_api.rooms.list(max=100))
    matching_rooms = [
        room for room in all_rooms 
        if search_term in room.title.lower()
    ][:max_results]
    
    spaces_info = []
    for room in matching_rooms:
        spaces_info.append({
            "id": room.id,
            "title": room.title,
            "type": room.type,
            "created": str(room.created)
        })
    
    result = {
        "search_term": search_term,
        "matches_found": len(spaces_info),
        "spaces": spaces_info
    }
    
    return [TextContent(
        type="text",
        text=f"Found {len(spaces_info)} matching spaces:\n\n{json.dumps(result, indent=2)}"
    )]


async def handle_get_my_details(args: dict) -> list[TextContent]:
    """Get authenticated user/bot details."""
    me = webex_api.people.me()
    
    details = {
        "id": me.id,
        "emails": me.emails,
        "displayName": me.displayName,
        "firstName": me.firstName if hasattr(me, 'firstName') else None,
        "lastName": me.lastName if hasattr(me, 'lastName') else None,
        "orgId": me.orgId,
        "created": str(me.created),
        "type": me.type
    }
    
    return [TextContent(
        type="text",
        text=f"Bot/User details:\n\n{json.dumps(details, indent=2)}"
    )]


async def main():
    """Main entry point for the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Webex MCP Server starting...")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
