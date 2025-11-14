from typing import Optional, Dict, Any
import logging
from openai import AsyncOpenAI
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Enhanced LLM Service with business context and decision-making"""

    def __init__(self):
        # Initialize DeepSeek client
        if settings.DEEPSEEK_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
            )
        else:
            logger.warning("DEEPSEEK_API_KEY not set - LLM features will not work")
            self.client = None

    async def process_with_context(
        self,
        message: str,
        business_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Process a message with full business context

        Args:
            message: User's input message
            business_context: Business information and settings
            conversation_history: Previous messages in conversation

        Returns:
            Dict with response and metadata
        """
        try:
            # Build system prompt with business context
            system_prompt = self._build_system_prompt(business_context)

            # Build messages array
            messages = [{"role": "system", "content": system_prompt}]

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": message})

            # Get response from LLM
            response = await self._call_llm(messages)

            # Determine if action requires approval
            requires_approval = self._check_approval_needed(response, business_context)

            return {
                "response": response,
                "requires_approval": requires_approval,
                "confidence": 0.85,  # Could be enhanced with actual confidence scoring
                "action_type": self._detect_action_type(response),
            }
        except Exception as e:
            logger.error(f"Error processing message with context: {e}")
            return {
                "response": "I encountered an error processing your request. Please try again.",
                "requires_approval": True,
                "confidence": 0.0,
                "action_type": "error",
            }

    def _build_system_prompt(self, business_context: Optional[Dict[str, Any]] = None) -> str:
        """Build system prompt with business context"""
        base_prompt = """You are an autonomous AI business assistant for Russian SMB owners.
Your role is to proactively manage business tasks, make decisions within thresholds, and only escalate critical matters.

Key principles:
- Act autonomously within approved thresholds
- Be proactive, not reactive
- Focus on saving time and preventing problems
- Provide clear, actionable insights in Russian language
- Always consider business context when making decisions
"""

        if business_context:
            context_str = f"""
Current Business Context:
- Business Name: {business_context.get('business_name', 'Not set')}
- Type: {business_context.get('business_type', 'Not set')}
- Location: {business_context.get('location', 'Not set')}
- Operating Hours: {business_context.get('operating_hours', 'Not set')}
- Average Daily Revenue: ₽{business_context.get('average_daily_revenue', 0):,}
- Typical Customers/Day: {business_context.get('typical_customer_count', 0)}
- Employees: {business_context.get('employee_count', 0)}

Decision Thresholds:
{self._format_thresholds(business_context.get('decision_thresholds', {}))}
"""
            return base_prompt + context_str

        return base_prompt

    def _format_thresholds(self, thresholds: Dict[str, Any]) -> str:
        """Format decision thresholds for prompt"""
        if not thresholds:
            return "- Auto-approve: Actions under ₽10,000\n- Require approval: ₽10,000 - ₽50,000\n- Always escalate: Over ₽50,000"

        auto = thresholds.get('auto_approve', {})
        require = thresholds.get('require_approval', {})
        escalate = thresholds.get('always_escalate', {})

        return f"""- Auto-approve: Up to ₽{auto.get('max_amount', 10000):,}
- Require approval: ₽{require.get('amount_range', [10000, 50000])[0]:,} - ₽{require.get('amount_range', [10000, 50000])[1]:,}
- Always escalate: Over ₽{escalate.get('min_amount', 50000):,}"""

    async def _call_llm(self, messages: list) -> str:
        """Call DeepSeek API"""
        try:
            if not self.client:
                return "LLM service is not configured. Please set DEEPSEEK_API_KEY in your .env file."

            response = await self.client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {e}")
            return f"Error calling LLM: {str(e)}. Please check your DEEPSEEK_API_KEY."

    def _check_approval_needed(self, response: str, business_context: Optional[Dict[str, Any]] = None) -> bool:
        """Determine if the action requires user approval"""
        # Check for keywords that indicate high-impact actions
        high_impact_keywords = [
            "payment", "pay", "transfer", "invoice", "contract",
            "legal", "complaint", "refund", "discount", "price change"
        ]

        response_lower = response.lower()
        for keyword in high_impact_keywords:
            if keyword in response_lower:
                return True

        return False

    def _detect_action_type(self, response: str) -> str:
        """Detect the type of action from the response"""
        response_lower = response.lower()

        if any(word in response_lower for word in ["payment", "pay", "invoice"]):
            return "financial"
        elif any(word in response_lower for word in ["customer", "client", "respond"]):
            return "customer_service"
        elif any(word in response_lower for word in ["report", "analytics", "metrics"]):
            return "reporting"
        elif any(word in response_lower for word in ["schedule", "post", "social"]):
            return "marketing"
        elif any(word in response_lower for word in ["supplier", "order", "inventory"]):
            return "operations"
        else:
            return "general"

    async def generate_briefing(
        self,
        business_context: Dict[str, Any],
        recent_actions: list,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate morning briefing content"""
        try:
            prompt = f"""Generate a concise morning briefing for {business_context.get('business_name')} in Russian.

Recent Actions (last 24 hours):
{self._format_actions(recent_actions)}

Current Metrics:
- Revenue: ₽{metrics.get('revenue', 0):,} ({metrics.get('revenue_change', '0%')})
- Customers: {metrics.get('customers', 0)} ({metrics.get('customer_change', '0%')})

Provide:
1. Summary of completed actions
2. Urgent items for today
3. Key recommendations

Keep it brief and actionable."""

            messages = [
                {"role": "system", "content": "You are a business assistant generating morning briefings in Russian."},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_llm(messages)

            return {
                "summary": response,
                "completed_actions": recent_actions,
                "metrics": metrics,
            }
        except Exception as e:
            logger.error(f"Error generating briefing: {e}")
            return {
                "summary": "Не удалось сгенерировать брифинг.",
                "completed_actions": [],
                "metrics": {},
            }

    def _format_actions(self, actions: list) -> str:
        """Format actions for prompt"""
        if not actions:
            return "No recent actions"

        formatted = []
        for action in actions[:10]:  # Limit to 10 most recent
            formatted.append(f"- {action.get('description', 'Unknown action')} at {action.get('time', 'unknown time')}")

        return "\n".join(formatted)


# Singleton instance
llm_service = LLMService()
