"""
Complete Gemini Live Agent with RAG using Function Calling
Combines: Gemini Live API + LlamaIndex RAG + LiveKit
"""

import logging
import os
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import google
from rag_llamaindex import query_docs, build_index

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini-rag-agent")


# Define the RAG tool for Gemini
def create_rag_tool():
    """Create the query_docs tool definition for Gemini"""
    from google.genai import types
    
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="query_docs",
                description="Search and retrieve information from uploaded documents. Use this tool when the user asks questions about their documents.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "query": types.Schema(
                            type=types.Type.STRING,
                            description="The search query or question to look up in the uploaded documents"
                        )
                    },
                    required=["query"]
                )
            )
        ]
    )


class GeminiRAGAssistant(Agent):
    """Voice Assistant with RAG using Gemini Live API"""
    
    def __init__(self) -> None:
        instructions = """
You are a helpful and friendly AI voice assistant for TechVision company.

IMPORTANT INSTRUCTIONS:
- When the user asks about products, pricing, support, or company information, you MUST use the query_docs tool to get accurate information.
- Always base your answers on the information from query_docs when available.
- Keep your responses brief, natural, and conversational.
- Do not mention that you're using a tool or searching - just provide the answer naturally.
- If query_docs doesn't return relevant info, you can use your general knowledge but mention this is not from official documents.

You help customers with questions about:
- Products (CloudSync Pro, DataGuard, TeamConnect)
- Pricing and plans
- Support and contact information
- Company information
"""
        
        # Use Gemini Live API RealtimeModel (بدون tools)
        realtime_model = google.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-12-2025",
            voice="Puck",
            temperature=0.8,
        )
        
        super().__init__(
            instructions=instructions,
            llm=realtime_model,
        )
    
    async def on_function_call(self, function_name: str, arguments: dict) -> str:
        """Handle function calls from Gemini"""
        logger.info(f" Function called: {function_name}")
        logger.info(f"Arguments: {arguments}")
        
        if function_name == "query_docs":
            query = arguments.get("query", "")
            result = query_docs(query)
            logger.info(f"RAG returned result: {result[:100]}...")
            return result
        
        return "Function not found"


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""
    
    logger.info(f"Connecting to room: {ctx.room.name}")
    
    # Connect to the room FIRST
    await ctx.connect()
    logger.info("Connected to room")
    
    # Build RAG index (non-blocking)
    logger.info("Checking RAG index...")
    try:
        index = build_index()
        if index:
            logger.info("RAG system ready with documents")
        else:
            logger.info("No documents uploaded - waiting for uploads")
    except Exception as e:
        logger.warning(f"RAG index check: {e}")
    
    # Create agent session
    session = AgentSession()
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=GeminiRAGAssistant()
    )
    
    logger.info("Gemini RAG voice assistant ready!")
    logger.info("Users can upload documents and ask questions")


if __name__ == "__main__":
    print("=" * 60)
    print("Gemini Live Agent with RAG")
    print("Native Audio + Function Calling + LlamaIndex")
    print("=" * 60)
    print()
    
    # Check required environment variables
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "GOOGLE_API_KEY"
    ]
    
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        print()
        print("Required in .env file:")
        for var in required_vars:
            print(f"  {var}=your_value_here")
        exit(1)
    
    print("Environment configured")
    print(f"LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    print()
    print("Initializing RAG system...")
    print("   - Gemini embeddings (API-based, lightweight)")
    print("   - LlamaIndex vector store")
    print("   - Function calling integration")
    print()
    print("=" * 60)
    print()
    
    # Run the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    )