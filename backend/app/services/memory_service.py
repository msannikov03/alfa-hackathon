from typing import List, Dict, Any, Optional
import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class MemoryService:
    """Vector-based memory service for pattern recognition and context retrieval"""

    def __init__(self):
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.CHROMADB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )

            # Get or create collections
            self.conversations = self._get_or_create_collection("conversations")
            self.patterns = self._get_or_create_collection("patterns")
            self.decisions = self._get_or_create_collection("decisions")

            logger.info("Memory service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing memory service: {e}")
            self.client = None

    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.client.get_or_create_collection(
                name=name,
                metadata={"description": f"Storage for {name}"}
            )
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            return None

    async def store_conversation(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Store a conversation in vector database"""
        try:
            if not self.conversations:
                return False

            doc_id = f"conv_{user_id}_{datetime.now().timestamp()}"

            self.conversations.add(
                documents=[f"User: {user_message}\nAssistant: {ai_response}"],
                metadatas=[{
                    "user_id": str(user_id),
                    "timestamp": datetime.now().isoformat(),
                    "context": str(context or {}),
                }],
                ids=[doc_id]
            )

            return True
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            return False

    async def retrieve_relevant_context(
        self,
        user_id: int,
        query: str,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant past conversations"""
        try:
            if not self.conversations:
                return []

            results = self.conversations.query(
                query_texts=[query],
                n_results=n_results,
                where={"user_id": str(user_id)},
            )

            if not results["documents"]:
                return []

            context_items = []
            for i, doc in enumerate(results["documents"][0]):
                context_items.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "relevance": 1.0 - (results["distances"][0][i] if "distances" in results else 0.5),
                })

            return context_items
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    async def store_pattern(
        self,
        user_id: int,
        pattern_type: str,
        trigger: Dict[str, Any],
        action: str,
        success: bool = True,
    ) -> bool:
        """Store a recognized pattern"""
        try:
            if not self.patterns:
                return False

            doc_id = f"pattern_{user_id}_{pattern_type}_{datetime.now().timestamp()}"

            pattern_text = f"Pattern: {pattern_type}\nTrigger: {trigger}\nAction: {action}"

            self.patterns.add(
                documents=[pattern_text],
                metadatas=[{
                    "user_id": str(user_id),
                    "pattern_type": pattern_type,
                    "trigger": str(trigger),
                    "action": action,
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                }],
                ids=[doc_id]
            )

            return True
        except Exception as e:
            logger.error(f"Error storing pattern: {e}")
            return False

    async def find_similar_patterns(
        self,
        user_id: int,
        current_situation: str,
        n_results: int = 3,
    ) -> List[Dict[str, Any]]:
        """Find similar patterns from history"""
        try:
            if not self.patterns:
                return []

            results = self.patterns.query(
                query_texts=[current_situation],
                n_results=n_results,
                where={"user_id": str(user_id), "success": True},
            )

            if not results["documents"]:
                return []

            patterns = []
            for i, doc in enumerate(results["documents"][0]):
                patterns.append({
                    "pattern": doc,
                    "metadata": results["metadatas"][0][i],
                    "confidence": 1.0 - (results["distances"][0][i] if "distances" in results else 0.5),
                })

            return patterns
        except Exception as e:
            logger.error(f"Error finding patterns: {e}")
            return []

    async def store_decision(
        self,
        user_id: int,
        decision_type: str,
        context: Dict[str, Any],
        action_taken: str,
        outcome: str,
    ) -> bool:
        """Store a decision for learning"""
        try:
            if not self.decisions:
                return False

            doc_id = f"decision_{user_id}_{datetime.now().timestamp()}"

            decision_text = f"""Decision Type: {decision_type}
Context: {context}
Action: {action_taken}
Outcome: {outcome}"""

            self.decisions.add(
                documents=[decision_text],
                metadatas=[{
                    "user_id": str(user_id),
                    "decision_type": decision_type,
                    "context": str(context),
                    "action": action_taken,
                    "outcome": outcome,
                    "timestamp": datetime.now().isoformat(),
                }],
                ids=[doc_id]
            )

            return True
        except Exception as e:
            logger.error(f"Error storing decision: {e}")
            return False

    async def get_decision_insights(
        self,
        user_id: int,
        decision_type: str,
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """Get insights from past decisions"""
        try:
            if not self.decisions:
                return {"success_rate": 0.5, "total_decisions": 0, "recommendations": []}

            results = self.decisions.query(
                query_texts=[decision_type],
                n_results=n_results,
                where={"user_id": str(user_id), "decision_type": decision_type},
            )

            if not results["documents"]:
                return {"success_rate": 0.5, "total_decisions": 0, "recommendations": []}

            # Calculate success rate
            total = len(results["metadatas"][0])
            successful = sum(1 for meta in results["metadatas"][0] if meta.get("outcome") == "success")
            success_rate = successful / total if total > 0 else 0.5

            recommendations = []
            for meta in results["metadatas"][0][:3]:
                if meta.get("outcome") == "success":
                    recommendations.append(meta.get("action", ""))

            return {
                "success_rate": success_rate,
                "total_decisions": total,
                "recommendations": recommendations,
            }
        except Exception as e:
            logger.error(f"Error getting decision insights: {e}")
            return {"success_rate": 0.5, "total_decisions": 0, "recommendations": []}

    async def reset_memory(self, user_id: Optional[int] = None):
        """Reset memory (for testing or user request)"""
        try:
            if user_id:
                # Delete only user's data
                # ChromaDB doesn't support delete by metadata easily, so we'd need to implement this differently
                logger.warning(f"Partial reset for user {user_id} not fully implemented")
            else:
                # Reset all collections
                if self.client:
                    self.client.reset()
                    self.conversations = self._get_or_create_collection("conversations")
                    self.patterns = self._get_or_create_collection("patterns")
                    self.decisions = self._get_or_create_collection("decisions")

            return True
        except Exception as e:
            logger.error(f"Error resetting memory: {e}")
            return False


# Singleton instance
memory_service = MemoryService()
