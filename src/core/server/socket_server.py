import socketio
from src.core.logger import logger

# Create the Socket.IO server with configuration
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode="asgi",
    logger=True,
    ping_timeout=60,
    ping_interval=25,
    allow_upgrades=True,
    transports=["polling", "websocket"],
)


@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"🔌 Client connected: {sid}")

    try:
        await sio.emit(
            "connected", {"message": "Successfully connected to server"}, to=sid
        )
    except Exception as e:
        logger.error(f"Error in connect handler: {e}")


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"❌ Client disconnected: {sid}")


@sio.event
async def join_room(sid, data):
    """Handle room joining"""
    try:
        conversation_id = data.get("conversation_id")
        if conversation_id:
            await sio.enter_room(sid, conversation_id)
            logger.info(f"🏠 {sid} joined room {conversation_id}")
            await sio.emit("room_joined", {"room": conversation_id}, to=sid)
        else:
            logger.warning(f"⚠️ No conversation_id provided by {sid}")
            await sio.emit("error", {"message": "conversation_id is required"}, to=sid)
    except Exception as e:
        logger.error(f"Error in join_room: {e}")
        await sio.emit("error", {"message": "Failed to join room"}, to=sid)


@sio.event
async def send_message(sid, data):
    """Handle message sending"""
    try:
        conversation_id = data.get("conversation_id")
        message = data.get("message")

        if not conversation_id or not message:
            logger.warning(
                f"⚠️ Missing data from {sid}: conversation_id={conversation_id}, message={message}"
            )
            await sio.emit(
                "error", {"message": "conversation_id and message are required"}, to=sid
            )
            return

        logger.info(f"💬 {sid} -> {conversation_id}: {message}")

        # Echo the user's message to everyone in the room
        await sio.emit(
            "new_message",
            {"author": "user", "message": message, "timestamp": str(sid)},
            room=conversation_id,
        )

        # Process AI response (dummy example)
        ai_response = f"Echo: {message}"
        await sio.emit(
            "new_message",
            {"author": "ai", "message": ai_response, "timestamp": str(sid)},
            room=conversation_id,
        )

    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        await sio.emit("error", {"message": "Failed to send message"}, to=sid)


@sio.event
async def ping(sid, data):
    """Handle ping events"""
    await sio.emit("pong", data, to=sid)


# Create the Socket.IO ASGI app - DO NOT specify socketio_path here if mounting at root
socket_app = socketio.ASGIApp(sio)

logger.info("✅ Socket.IO server initialized successfully")
