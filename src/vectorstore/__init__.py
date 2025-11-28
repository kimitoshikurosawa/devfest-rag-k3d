try:
    from .chroma_manager import ChromaManager
except ImportError:
    # Fallback to simple store if ChromaDB not available
    from .simple_store import ChromaManager
    print("⚠️  Using SimpleVectorStore (ChromaDB not available)")

__all__ = ["ChromaManager"]
