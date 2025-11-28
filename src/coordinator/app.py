"""
DevFest RAG Assistant - Streamlit Interface
Multi-agent system for DevFest Abidjan 2025
"""
import streamlit as st
import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import DevFestAgent, KimanaAgent
from utils import OllamaClient
from vectorstore import ChromaManager
from coordinator.router import Router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="DevFest RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4285f4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5f6368;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .devfest-badge {
        background-color: #e8f0fe;
        color: #1967d2;
    }
    .kimana-badge {
        background-color: #fce8e6;
        color: #d93025;
    }
    .both-badge {
        background-color: #e6f4ea;
        color: #137333;
    }
    .source-card {
        background-color: #f8f9fa;
        border-left: 4px solid #4285f4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the multi-agent system"""
    logger.info("Initializing multi-agent system...")
    
    # Initialize Ollama client
    ollama_client = OllamaClient()
    
    # Check Ollama health
    if not ollama_client.health_check():
        st.error("⚠️ Ollama n'est pas accessible. Assurez-vous qu'Ollama est en cours d'exécution.")
        st.stop()
    
    # Initialize ChromaDB
    chroma_manager = ChromaManager()
    
    # Load data if not already loaded
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    devfest_count = chroma_manager.load_json_data(
        collection_name="devfest_docs",
        data_dir=str(data_dir / "devfest")
    )
    logger.info(f"DevFest collection: {devfest_count} documents")
    
    kimana_count = chroma_manager.load_json_data(
        collection_name="kimana_docs",
        data_dir=str(data_dir / "kimana")
    )
    logger.info(f"Kimana collection: {kimana_count} documents")
    
    # Initialize agents
    devfest_agent = DevFestAgent(ollama_client, chroma_manager)
    kimana_agent = KimanaAgent(ollama_client, chroma_manager)
    
    # Initialize router
    router = Router()
    
    logger.info("System initialized successfully!")
    
    return {
        "devfest_agent": devfest_agent,
        "kimana_agent": kimana_agent,
        "router": router,
        "chroma_manager": chroma_manager
    }


def display_agent_badge(agent_type: str):
    """Display agent badge"""
    badges = {
        "devfest": ('<span class="agent-badge devfest-badge">🎯 Agent DevFest</span>', "devfest-badge"),
        "kimana": ('<span class="agent-badge kimana-badge">👤 Agent Kimana</span>', "kimana-badge"),
        "both": ('<span class="agent-badge both-badge">🤝 Agents Combinés</span>', "both-badge")
    }
    badge_html, _ = badges.get(agent_type, badges["both"])
    st.markdown(badge_html, unsafe_allow_html=True)


def display_sources(sources):
    """Display sources in a nice format"""
    if not sources:
        return
    
    with st.expander("📚 Sources utilisées", expanded=False):
        for i, source in enumerate(sources, 1):
            relevance_pct = int(source.get('relevance', 0) * 100)
            st.markdown(f"""
            <div class="source-card">
                <strong>Source {i}</strong> ({source['source']}) - Pertinence: {relevance_pct}%<br>
                <small>{source['document'][:200]}...</small>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">🤖 DevFest RAG Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Assistant intelligent multi-agents pour DevFest Abidjan 2025</div>',
        unsafe_allow_html=True
    )
    
    # Initialize system
    try:
        system = initialize_system()
    except Exception as e:
        st.error(f"Erreur d'initialisation: {e}")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Configuration")
        
        # Agent selection mode
        agent_mode = st.radio(
            "Mode de sélection d'agent",
            ["Automatique (Routing intelligent)", "Manuel"],
            index=0
        )
        
        if agent_mode == "Manuel":
            selected_agent = st.selectbox(
                "Choisir un agent",
                ["DevFest Agent", "Kimana Agent"]
            )
        
        st.markdown("---")
        
        # System status
        st.markdown("## 📊 Statut du Système")
        
        devfest_health = system["devfest_agent"].health_check()
        kimana_health = system["kimana_agent"].health_check()
        
        col1, col2 = st.columns(2)
        with col1:
            status_icon = "✅" if devfest_health['status'] == 'healthy' else "⚠️"
            st.metric("DevFest Agent", devfest_health['status'], status_icon)
        with col2:
            status_icon = "✅" if kimana_health['status'] == 'healthy' else "⚠️"
            st.metric("Kimana Agent", kimana_health['status'], status_icon)
        
        # Collection stats
        st.markdown("### 📚 Base de Connaissances")
        devfest_stats = system["chroma_manager"].get_stats("devfest_docs")
        kimana_stats = system["chroma_manager"].get_stats("kimana_docs")
        
        st.metric("Docs DevFest", devfest_stats.get('count', 0))
        st.metric("Docs Kimana", kimana_stats.get('count', 0))
        
        st.markdown("---")
        
        # Example questions
        st.markdown("## 💡 Questions Exemples")
        
        example_questions = {
            "DevFest": [
                "À quelle heure commence le talk de Kimana ?",
                "Quels sont les sponsors de DevFest ?",
                "Où se déroule l'événement ?",
            ],
            "Kimana": [
                "Qui est Kimana Misago ?",
                "C'est quoi Ivoire.pro ?",
                "Quelle est l'expertise de Kimana ?",
            ]
        }
        
        for category, questions in example_questions.items():
            with st.expander(f"📌 {category}"):
                for q in questions:
                    if st.button(q, key=f"example_{q}"):
                        st.session_state.example_question = q
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                display_sources(message["sources"])
    
    # Handle example question
    if "example_question" in st.session_state:
        question = st.session_state.example_question
        del st.session_state.example_question
    else:
        # Chat input
        question = st.chat_input("Posez votre question...")
    
    if question:
        # Display user message
        with st.chat_message("user"):
            st.markdown(question)
        
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Process question
        with st.chat_message("assistant"):
            with st.spinner("Réflexion en cours..."):
                try:
                    # Routing
                    if agent_mode == "Automatique (Routing intelligent)":
                        route = system["router"].route(question)
                        display_agent_badge(route)
                        
                        if route == "devfest":
                            result = system["devfest_agent"].answer(question)
                        elif route == "kimana":
                            result = system["kimana_agent"].answer(question)
                        else:  # both
                            # Query both agents and combine
                            devfest_result = system["devfest_agent"].answer(question)
                            kimana_result = system["kimana_agent"].answer(question)
                            
                            # Combine answers
                            combined_answer = f"""**Agent DevFest:**
{devfest_result['answer']}

**Agent Kimana:**
{kimana_result['answer']}
"""
                            result = {
                                "agent": "Combined",
                                "answer": combined_answer,
                                "sources": devfest_result['sources'] + kimana_result['sources']
                            }
                    else:
                        # Manual mode
                        if selected_agent == "DevFest Agent":
                            display_agent_badge("devfest")
                            result = system["devfest_agent"].answer(question)
                        else:
                            display_agent_badge("kimana")
                            result = system["kimana_agent"].answer(question)
                    
                    # Display answer
                    st.markdown(result['answer'])
                    
                    # Display sources
                    if result.get('sources'):
                        display_sources(result['sources'])
                    
                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result['answer'],
                        "sources": result.get('sources', [])
                    })
                    
                except Exception as e:
                    st.error(f"Erreur: {e}")
                    logger.error(f"Error processing question: {e}", exc_info=True)


if __name__ == "__main__":
    main()
