
import logging
import os
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession, 
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import google

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini-live-agent")


class GeminiLiveAssistant(Agent):
    """Voice Assistant using Gemini Live API (native audio)"""
    
    def __init__(self) -> None:
        # Define instructions
        instructions = """
            You are a helpful and friendly AI voice assistant.
            Keep your responses brief, natural, and conversational.
        """
        
        # Use Gemini Live API RealtimeModel
        # This handles STT + LLM + TTS all in one!
        realtime_model = google.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-12-2025",
            voice="Puck",  # Options: Puck, Charon, Kore, Fenrir, Aoede
            temperature=0.8,
        )
        
        super().__init__(
            instructions=instructions,
            llm=realtime_model,
        )


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""
    
    logger.info(f"Connecting to room: {ctx.room.name}")
    
    # Connect to the room
    await ctx.connect()
    logger.info("Connected to room")
    
    # Create agent session with Gemini Live
    session = AgentSession()
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=GeminiLiveAssistant()
    )
    
    logger.info("Gemini Live voice assistant ready!")


if __name__ == "__main__":
    print("=" * 60)
    print("Gemini Live API Agent (Official)")
    print("Native Audio: STT + LLM + TTS built-in")
    print("=" * 60)
    print()
    
    # Check required environment variables
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "GOOGLE_API_KEY"  # For Gemini API
    ]
    
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        print()
        print("Required in .env file:")
        for var in required_vars:
            print(f"  {var}=your_value_here")
        print()
        print("Note: GOOGLE_API_KEY is your Gemini API key")
        print("Get it from: https://makersuite.google.com/app/apikey")
        exit(1)
    
    print("Environment configured")
    print(f"LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    print()
    print("Starting Gemini Live API agent...")
    print("   Using: gemini-2.5-flash-native-audio")
    print("   Voice: Puck")
    print("=" * 60)
    print()
    
    # Run the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    )