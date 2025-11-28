"""
Base Agent class for RAG agents
"""
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from ..utils.ollama_client import OllamaClient
from ..vectorstore.chroma_manager import ChromaManager

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for RAG agents"""
    
    def __init__(
        self,
        name: str,
        collection_name: str,
        ollama_client: OllamaClient,
        chroma_manager: ChromaManager,
        system_prompt: str = None
    ):
        self.name = name
        self.collection_name = collection_name
        self.ollama_client = ollama_client
        self.chroma_manager = chroma_manager
        self.system_prompt = system_prompt or self._default_system_prompt()
        
        logger.info(f"Agent '{self.name}' initialized with collection '{self.collection_name}'")
    
    @abstractmethod
    def _default_system_prompt(self) -> str:
        """Return default system prompt for this agent"""
        pass
    
    def search_knowledge(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search in the agent's knowledge base"""
        return self.chroma_manager.search(
            collection_name=self.collection_name,
            query=query,
            n_results=n_results
        )
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context from search results"""
        if not search_results:
            return "Aucun document pertinent trouvé dans la base de connaissances."
        
        context_parts = ["Documents pertinents:\n"]
        for i, result in enumerate(search_results, 1):
            doc = result['document']
            source = result['metadata'].get('source', 'unknown')
            context_parts.append(f"\n[Document {i}] (Source: {source})\n{doc}\n")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build the final prompt for the LLM"""
        prompt = f"""Contexte:
{context}

Question: {question}

Instructions:
- Réponds de manière claire et précise
- Base ta réponse sur le contexte fourni
- Si l'information n'est pas dans le contexte, dis-le clairement
- Cite les sources quand c'est pertinent
- Réponds en français

Réponse:"""
        return prompt
    
    def answer(
        self,
        question: str,
        n_results: int = 3,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG
        
        Args:
            question: User question
            n_results: Number of documents to retrieve
            temperature: LLM temperature
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            logger.info(f"[{self.name}] Processing question: {question}")
            
            # 1. Search knowledge base
            search_results = self.search_knowledge(question, n_results)
            
            # 2. Build context
            context = self._build_context(search_results)
            
            # 3. Build prompt
            prompt = self._build_prompt(question, context)
            
            # 4. Generate answer
            response = self.ollama_client.generate(
                prompt=prompt,
                system=self.system_prompt,
                temperature=temperature
            )
            
            # 5. Format response
            return {
                "agent": self.name,
                "question": question,
                "answer": response.get("text", ""),
                "sources": [
                    {
                        "document": r['document'],
                        "source": r['metadata'].get('source', 'unknown'),
                        "relevance": 1 - r.get('distance', 1)
                    }
                    for r in search_results
                ],
                "metadata": {
                    "model": response.get("model", "unknown"),
                    "tokens": response.get("tokens", 0),
                    "num_sources": len(search_results)
                }
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Error answering question: {e}")
            return {
                "agent": self.name,
                "question": question,
                "answer": f"Désolé, une erreur s'est produite: {str(e)}",
                "sources": [],
                "metadata": {"error": str(e)}
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check agent health"""
        try:
            # Check collection
            stats = self.chroma_manager.get_stats(self.collection_name)
            
            # Check Ollama
            ollama_ok = self.ollama_client.health_check()
            
            return {
                "agent": self.name,
                "status": "healthy" if ollama_ok and stats['status'] == 'ready' else "degraded",
                "collection": stats,
                "ollama": "connected" if ollama_ok else "disconnected"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "status": "error",
                "error": str(e)
            }
