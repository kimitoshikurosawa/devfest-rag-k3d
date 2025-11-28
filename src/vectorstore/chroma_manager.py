"""
ChromaDB Manager for Vector Store operations
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ChromaManager:
    """Manage ChromaDB collections for RAG"""
    
    def __init__(
        self,
        persist_dir: str = None,
        embedding_model: str = None
    ):
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self.embedding_model_name = embedding_model or os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        logger.info(f"ChromaDB initialized at {self.persist_dir}")
    
    def create_or_get_collection(self, collection_name: str):
        """Create or get a collection"""
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Collection '{collection_name}' ready")
            return collection
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            raise
    
    def load_json_data(
        self,
        collection_name: str,
        data_dir: str,
        chunk_size: int = 500
    ) -> int:
        """
        Load JSON files from a directory into a collection
        
        Args:
            collection_name: Name of the collection
            data_dir: Directory containing JSON files
            chunk_size: Size of text chunks
            
        Returns:
            Number of documents loaded
        """
        collection = self.create_or_get_collection(collection_name)
        
        # Get existing doc count
        existing_count = collection.count()
        if existing_count > 0:
            logger.info(f"Collection '{collection_name}' already has {existing_count} documents")
            return existing_count
        
        documents = []
        metadatas = []
        ids = []
        doc_id = 0
        
        # Load all JSON files from directory
        for filename in os.listdir(data_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(data_dir, filename)
            logger.info(f"Loading {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert JSON to text chunks
            chunks = self._json_to_chunks(data, filename)
            
            for chunk in chunks:
                documents.append(chunk["text"])
                metadatas.append({
                    "source": filename,
                    "type": chunk.get("type", "general"),
                    "collection": collection_name
                })
                ids.append(f"{collection_name}_{doc_id}")
                doc_id += 1
        
        if documents:
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documents)} chunks...")
            embeddings = self.embedding_model.encode(
                documents,
                show_progress_bar=True
            ).tolist()
            
            # Add to collection
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Loaded {len(documents)} documents into '{collection_name}'")
        
        return len(documents)
    
    def _json_to_chunks(
        self,
        data: Dict[str, Any],
        source: str,
        max_length: int = 500
    ) -> List[Dict[str, Any]]:
        """Convert JSON data to text chunks"""
        chunks = []
        
        def process_value(key: str, value: Any, parent_key: str = "") -> None:
            """Recursively process JSON values"""
            full_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                for k, v in value.items():
                    process_value(k, v, full_key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        # Create a text representation of the dict
                        text = f"{full_key}: " + json.dumps(item, ensure_ascii=False)
                        if len(text) > max_length:
                            # Split large texts
                            for i in range(0, len(text), max_length):
                                chunks.append({
                                    "text": text[i:i+max_length],
                                    "type": full_key,
                                    "source": source
                                })
                        else:
                            chunks.append({
                                "text": text,
                                "type": full_key,
                                "source": source
                            })
                    else:
                        text = f"{full_key}[{i}]: {item}"
                        chunks.append({
                            "text": text,
                            "type": full_key,
                            "source": source
                        })
            else:
                text = f"{full_key}: {value}"
                chunks.append({
                    "text": text,
                    "type": full_key,
                    "source": source
                })
        
        # Process the JSON data
        for key, value in data.items():
            process_value(key, value)
        
        return chunks
    
    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search in a collection
        
        Args:
            collection_name: Name of the collection
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of results with documents and metadata
        """
        try:
            collection = self.client.get_collection(collection_name)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search error in {collection_name}: {e}")
            return []
    
    def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            return {
                "collection": collection_name,
                "count": count,
                "status": "ready" if count > 0 else "empty"
            }
        except Exception as e:
            return {
                "collection": collection_name,
                "error": str(e),
                "status": "error"
            }
