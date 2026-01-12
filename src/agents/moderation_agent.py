"""
Moderation Agent using Azure AI Content Safety and Microsoft Agent Framework.

This agent analyzes text content for policy violations including:
- Hate speech and discrimination
- Profanity
- Violence and threats
- Self-harm content
- Sexual content
- PII leaks
"""

import os
from typing import Any

from openai import AsyncAzureOpenAI
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class ModerationAgent:
    """
    Content moderation agent that uses Azure AI Content Safety service
    and an AI agent to analyze content for policy violations.
    """

    def __init__(
        self,
        foundry_endpoint: str,
        model_deployment: str,
        content_safety_endpoint: str,
        content_safety_key: str | None = None,
        policies: dict[str, Any] | None = None,
    ):
        """
        Initialize the moderation agent.

        Args:
            foundry_endpoint: Microsoft Foundry project endpoint
            model_deployment: Model deployment name
            content_safety_endpoint: Azure Content Safety endpoint
            content_safety_key: Content Safety API key (or use Managed Identity)
            policies: Moderation policies configuration
        """
        self.policies = policies or {}

        # Initialize Azure AI Content Safety client
        if content_safety_key:
            credential = AzureKeyCredential(content_safety_key)
        else:
            credential = DefaultAzureCredential()

        self.content_safety_client = ContentSafetyClient(
            endpoint=content_safety_endpoint, credential=credential
        )

        # Initialize Azure OpenAI client for contextual analysis
        # Use DefaultAzureCredential which works with managed identity automatically
        azure_credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(azure_credential, "https://cognitiveservices.azure.com/.default")
        
        # Use the foundry endpoint directly as the Azure OpenAI endpoint
        self.openai_client = AsyncAzureOpenAI(
            azure_ad_token_provider=token_provider,
            api_version="2024-10-21",
            azure_endpoint=foundry_endpoint
        )
        
        self.model_deployment = model_deployment
        self.system_instructions = self._build_instructions()

    def refresh_policies(self, policies: dict[str, Any]) -> None:
        """
        Refresh moderation policies without recreating the agent.
        
        Args:
            policies: Updated moderation policies configuration
        """
        self.policies = policies
        # Rebuild instructions with new policies
        new_instructions = self._build_instructions()
        # Update the chat agent's instructions
        self.chat_agent.instructions = new_instructions
        print(f"✅ Moderation policies refreshed")

    def _build_instructions(self) -> str:
        """Build agent instructions based on configured policies."""
        return """You are a content moderation expert working for Russell Cellular's HR team.

Your role is to analyze Microsoft Teams messages for policy violations including:
1. Hate speech, discrimination, or harassment based on race, gender, religion, etc.
2. Profane or offensive language
3. Violent or threatening content
4. Self-harm related content
5. Sexually explicit content
6. Leakage of personally identifiable information (PII)

For each message you analyze:
- Assess the severity (low, medium, high)
- Identify which specific policies are violated
- Provide a brief justification
- Consider context (workplace appropriateness, professional standards)
- Be sensitive to false positives (technical jargon, legitimate business discussions)

Respond in JSON format:
{
    "is_violation": true/false,
    "violations": ["policy1", "policy2"],
    "severity": "low|medium|high",
    "confidence": 0.0-1.0,
    "justification": "Brief explanation",
    "recommended_action": "delete|flag|archive|allow"
}

Be thorough but fair. The goal is to maintain a respectful workplace environment
while minimizing false positives that could frustrate legitimate communication.
"""

    async def analyze_text(self, text: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Analyze text content for policy violations.

        Args:
            text: The text content to analyze
            context: Optional context (author, channel, etc.)

        Returns:
            Dictionary containing analysis results
        """
        # Step 1: Use Azure Content Safety for baseline detection
        content_safety_result = await self._analyze_with_content_safety(text)

        # Step 2: Use AI agent for contextual analysis
        agent_result = await self._analyze_with_agent(text, context, content_safety_result)

        # Step 3: Combine results and apply policies
        final_result = self._apply_policies(content_safety_result, agent_result)

        return final_result

    async def _analyze_with_content_safety(self, text: str) -> dict[str, Any]:
        """
        Use Azure Content Safety service for baseline text analysis.

        Returns:
            Dictionary with category scores and detected issues
        """
        try:
            print(f"🔍 Analyzing content with Content Safety: '{text[:100]}{'...' if len(text) > 100 else ''}'")
            request = AnalyzeTextOptions(text=text)
            response = self.content_safety_client.analyze_text(request)

            # Extract category severities
            results = {
                "hate": response.categories_analysis[0].severity if response.categories_analysis else 0,
                "self_harm": response.categories_analysis[1].severity if len(response.categories_analysis) > 1 else 0,
                "sexual": response.categories_analysis[2].severity if len(response.categories_analysis) > 2 else 0,
                "violence": response.categories_analysis[3].severity if len(response.categories_analysis) > 3 else 0,
            }

            # More sensitive detection thresholds (severity 1+ for hate, 2+ for others)
            hate_flagged = results["hate"] >= 1  # Lower threshold for harassment/bullying
            other_flagged = any(results[cat] >= 2 for cat in ["self_harm", "sexual", "violence"])
            flagged = hate_flagged or other_flagged

            print(f"📊 Content Safety results: {results}, flagged: {flagged}")

            return {
                "service": "azure_content_safety",
                "categories": results,
                "flagged": flagged,
                "details": {
                    "hate_flagged": hate_flagged,
                    "other_flagged": other_flagged
                }
            }
        except Exception as e:
            print(f"❌ Content Safety error: {e}")
            return {
                "service": "azure_content_safety",
                "error": str(e),
                "flagged": False,
            }

    async def _analyze_with_agent(
        self, text: str, context: dict[str, Any] | None, content_safety_result: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Use AI agent for contextual analysis with workplace awareness.

        Args:
            text: Text to analyze
            context: Contextual information
            content_safety_result: Results from Content Safety service

        Returns:
            Dictionary with agent's analysis
        """
        try:
            # Build context-aware prompt
            context_info = ""
            if context:
                author = context.get("author", "Unknown")
                channel = context.get("channel", "Unknown")
                context_info = f"\nContext: Posted by {author} in #{channel} channel."

            safety_info = f"\nContent Safety baseline: {content_safety_result.get('categories', {})}"

            user_message = f"""Analyze this Teams message for policy violations:

Message: "{text}"
{context_info}
{safety_info}

Provide your analysis in JSON format."""

            # Use OpenAI Chat Completions API
            response = await self.openai_client.chat.completions.create(
                model=self.model_deployment,
                messages=[
                    {"role": "system", "content": self.system_instructions},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            # Parse agent response (assuming JSON format)
            import json

            agent_text = response.choices[0].message.content
            # Extract JSON from response (may be wrapped in markdown)
            if "```json" in agent_text:
                agent_text = agent_text.split("```json")[1].split("```")[0]
            elif "```" in agent_text:
                agent_text = agent_text.split("```")[1].split("```")[0]

            return json.loads(agent_text.strip())

        except Exception as e:
            # Fallback if agent fails
            return {
                "service": "agent_analysis",
                "error": str(e),
                "is_violation": False,
                "confidence": 0.0,
            }

    def _apply_policies(self, content_safety_result: dict[str, Any], agent_result: dict[str, Any]) -> dict[str, Any]:
        """
        Apply configured policies to determine final action.

        Args:
            content_safety_result: Results from Content Safety service
            agent_result: Results from AI agent

        Returns:
            Final moderation decision
        """
        text_policies = self.policies.get("text_policies", {})

        # Determine if this is a violation
        is_violation = agent_result.get("is_violation", False) or content_safety_result.get("flagged", False)

        # Get severity and confidence
        severity = agent_result.get("severity", "low")
        confidence = agent_result.get("confidence", 0.5)

        # Determine action based on policies and severity
        action = "allow"
        notify = False
        violated_policies = agent_result.get("violations", [])
        
        # Also check Content Safety categories directly if flagged
        if content_safety_result.get("flagged", False):
            categories = content_safety_result.get("categories", {})
            print(f"🚨 Content Safety flagged! Categories: {categories}")
            for category, score in categories.items():
                if score >= 2:  # Low severity or higher
                    print(f"   ➕ Adding category '{category}' (score: {score}) to violated policies")
                    # Add category to violated policies if not already there
                    if category not in violated_policies:
                        violated_policies.append(category)

        print(f"🔍 Violated policies: {violated_policies}")
        print(f"📋 Available policies: {list(text_policies.keys())}")
        
        if is_violation:
            # Check each violated policy
            for policy_name in violated_policies:
                # Normalize policy name (replace spaces with underscores for lookup)
                policy_key = policy_name.lower().replace(" ", "_")
                policy = text_policies.get(policy_key, {})
                
                print(f"🔎 Checking '{policy_name}' -> '{policy_key}' -> Found: {policy_key in text_policies}")
                if policy_key in text_policies:
                    print(f"   ✓ Policy config: enabled={policy.get('enabled')}, notify={policy.get('notify')}, action={policy.get('action')}")
                
                if policy.get("enabled", False):
                    policy_action = policy.get("action", "flag")
                    policy_notify = policy.get("notify", False)

                    # Use most severe action
                    if policy_action == "delete":
                        action = "delete"
                    elif policy_action == "flag" and action != "delete":
                        action = "flag"

                    notify = notify or policy_notify
                    print(f"   → notify={notify}, action={action}")

        return {
            "is_violation": is_violation,
            "violations": violated_policies,
            "severity": severity,
            "confidence": confidence,
            "action": action,
            "notify": notify,
            "justification": agent_result.get("justification", ""),
            "content_safety_scores": content_safety_result.get("categories", {}),
            "agent_recommendation": agent_result.get("recommended_action", action),
        }

    async def close(self):
        """Clean up resources."""
        if hasattr(self.chat_agent, "close"):
            await self.chat_agent.close()
