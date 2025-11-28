"""
Intelligent Router for multi-agent system
"""
import logging
from typing import Literal

logger = logging.getLogger(__name__)


AgentType = Literal["devfest", "kimana", "both"]


class Router:
    """Route questions to the appropriate agent"""
    
    # Keywords for routing
    DEVFEST_KEYWORDS = [
        'devfest', 'event', 'événement', 'agenda', 'programme', 'schedule',
        'heure', 'quand', 'when', 'time', 'horaire',
        'talk', 'présentation', 'speaker', 'intervenant',
        'palm club', 'lieu', 'place', 'où', 'where',
        'sponsor', 'partenaire',
        'hackathon', 'quiz', 'activité', 'pause',
        'gdg', 'google', 'cloud abidjan'
    ]
    
    KIMANA_KEYWORDS = [
        'kimana', 'misago',
        'ivoire.pro', 'ivoire pro', 'ivoirepro',
        'marabu', 'cabinet marabu',
        'ivoryguards', 'ivory guards',
        'cto', 'devops', 'kubernetes',
        'qui est', 'who is', 'profil', 'profile',
        'co-founder', 'fondateur',
        'guce', 'eranove',
        'certification', 'kcna', 'google cloud certified'
    ]
    
    def __init__(self):
        logger.info("Router initialized")
    
    def route(self, question: str) -> AgentType:
        """
        Route a question to the appropriate agent
        
        Args:
            question: User question
            
        Returns:
            Agent type: 'devfest', 'kimana', or 'both'
        """
        q_lower = question.lower()
        
        # Count keyword matches
        devfest_score = sum(1 for kw in self.DEVFEST_KEYWORDS if kw in q_lower)
        kimana_score = sum(1 for kw in self.KIMANA_KEYWORDS if kw in q_lower)
        
        logger.info(f"Routing scores - DevFest: {devfest_score}, Kimana: {kimana_score}")
        
        # Decision logic
        if devfest_score > kimana_score:
            logger.info("Routed to: DevFest Agent")
            return "devfest"
        elif kimana_score > devfest_score:
            logger.info("Routed to: Kimana Agent")
            return "kimana"
        else:
            # Ambiguous or general question - try both
            logger.info("Routed to: Both Agents")
            return "both"
    
    def get_routing_explanation(self, question: str, route: AgentType) -> str:
        """Get human-readable explanation of routing decision"""
        explanations = {
            "devfest": "Question dirigée vers l'agent DevFest (informations sur l'événement)",
            "kimana": "Question dirigée vers l'agent Kimana (profil professionnel)",
            "both": "Question ambiguë - consultation des deux agents"
        }
        return explanations.get(route, "Routing inconnu")
