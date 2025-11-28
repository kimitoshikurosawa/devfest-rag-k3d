try:
    import chromadb
    from .chroma_manager import ChromaManager
except ImportError:
    # Fallback to simple store if ChromaDB not available
    from .simple_store import ChromaManager
    import warnings
    warnings.warn("ChromaDB not installed, using SimpleVectorStore (keyword-based search)")

__all__ = ["ChromaManager"]
