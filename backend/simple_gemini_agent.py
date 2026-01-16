
import logging
import os
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, google, cartesia, silero

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("free-gemini-agent")


class FreeGeminiAssistant(Agent):
    """Free Voice Assistant using Deepgram + Gemini + Cartesia"""
    
    def __init__(self) -> None:
        # Deepgram STT (Speech-to-Text)
        stt = deepgram.STT()
        
        # Gemini LLM
        llm = google.LLM(model="gemini-2.0-flash-exp")
        
        # Cartesia TTS (Text-to-Speech)
        tts = cartesia.TTS()
        
        # Silero VAD (Voice Activity Detection)
        vad = silero.VAD.load()
        
        super().__init__(
            instructions="""
                You are a helpful and friendly AI voice assistant.
            """,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad,
        )


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""
    
    logger.info(f"Agent connecting to room: {ctx.room.name}")
    
    # Connect to the room
    await ctx.connect()
    logger.info("Connected to room")
    
    # Create agent session
    session = AgentSession()
    
    # Start the session with our assistant
    await session.start(
        room=ctx.room,
        agent=FreeGeminiAssistant()
    )
    
    logger.info("Free voice assistant is ready!")


if __name__ == "__main__":
    print("=" * 60)
    print("Free Gemini Voice Agent")
    print("100% Free: Deepgram + Gemini + Cartesia")
    print("=" * 60)
    print()
    
    # Check required environment variables
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "DEEPGRAM_API_KEY",
        "GOOGLE_API_KEY",
        "CARTESIA_API_KEY"
    ]
    
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        print()
        print("Get your FREE API keys:")
        print("   1. Deepgram: https://console.deepgram.com/signup")
        print("      - 200 hours/month free")
        print()
        print("   2. Gemini: https://makersuite.google.com/app/apikey")
        print("      - Already have this")
        print()
        print("   3. Cartesia: https://play.cartesia.ai/")
        print("      - Free tier available")
        print()
        for var in required_vars:
            print(f"  {var}=your_value_here")
        exit(1)
    
    print("All API keys configured")
    print(f"LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    print()
    print("Starting free voice agent...")
    print("=" * 60)
    print()
    
    # Run the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    )