"""
Simple In-Memory Vector Store (Alternative à ChromaDB)
Pour test rapide sans dépendances lourdes
"""
import json
import logging
import numpy as np
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """Simple in-memory vector store avec recherche basique"""
    
    def __init__(self):
        self.collections = {}
        logger.info("SimpleVectorStore initialized (in-memory)")
    
    def create_or_get_collection(self, collection_name: str):
        """Create or get a collection"""
        if collection_name not in self.collections:
            self.collections[collection_name] = {
                "documents": [],
                "metadatas": [],
                "ids": []
            }
            logger.info(f"Collection '{collection_name}' created")
        return collection_name
    
    def load_json_data(
        self,
        collection_name: str,
        data_dir: str,
        chunk_size: int = 500
    ) -> int:
        """Load JSON files from a directory"""
        self.create_or_get_collection(collection_name)
        
        collection = self.collections[collection_name]
        
        # Check if already loaded
        if len(collection["documents"]) > 0:
            logger.info(f"Collection '{collection_name}' already has {len(collection['documents'])} documents")
            return len(collection["documents"])
        
        doc_id = 0
        
        # Load all JSON files
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
                collection["documents"].append(chunk["text"])
                collection["metadatas"].append({
                    "source": filename,
                    "type": chunk.get("type", "general"),
                    "collection": collection_name
                })
                collection["ids"].append(f"{collection_name}_{doc_id}")
                doc_id += 1
        
        logger.info(f"Loaded {len(collection['documents'])} documents into '{collection_name}'")
        return len(collection["documents"])
    
    def _json_to_chunks(
        self,
        data: Dict[str, Any],
        source: str,
        max_length: int = 500
    ) -> List[Dict[str, Any]]:
        """Convert JSON data to text chunks"""
        chunks = []
        
        def process_value(key: str, value: Any, parent_key: str = "") -> None:
            full_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                for k, v in value.items():
                    process_value(k, v, full_key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        text = f"{full_key}: " + json.dumps(item, ensure_ascii=False)
                        if len(text) > max_length:
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
        
        for key, value in data.items():
            process_value(key, value)
        
        return chunks
    
    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Simple keyword-based search (pas de embeddings)"""
        if collection_name not in self.collections:
            return []
        
        collection = self.collections[collection_name]
        
        # Simple keyword matching
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score each document
        scored_docs = []
        for i, doc in enumerate(collection["documents"]):
            doc_lower = doc.lower()
            doc_words = set(doc_lower.split())
            
            # Count matching words
            matches = len(query_words & doc_words)
            
            # Bonus for exact phrase match
            if query_lower in doc_lower:
                matches += 5
            
            if matches > 0:
                scored_docs.append({
                    "document": doc,
                    "metadata": collection["metadatas"][i],
                    "distance": 1.0 / (matches + 1),  # Lower is better
                    "score": matches
                })
        
        # Sort by score
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top N
        return scored_docs[:n_results]
    
    def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        if collection_name not in self.collections:
            return {
                "collection": collection_name,
                "count": 0,
                "status": "not_found"
            }
        
        collection = self.collections[collection_name]
        return {
            "collection": collection_name,
            "count": len(collection["documents"]),
            "status": "ready" if len(collection["documents"]) > 0 else "empty"
        }


# Alias pour compatibilité
ChromaManager = SimpleVectorStore
