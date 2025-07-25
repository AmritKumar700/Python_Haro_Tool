# src/prompt_manager.py

import re
from src.config import (
    CLAUDE_PROMPT_TEMPLATE, OPENAI_PROMPT_TEMPLATE,
    ANGLE_GENERATION_PROMPT, NUM_VARIANTS_PER_QUERY
)
from src.utils import get_logger

logger = get_logger(__name__)

class PromptManager:
    def __init__(self):
        self.claude_template = CLAUDE_PROMPT_TEMPLATE
        self.openai_template = OPENAI_PROMPT_TEMPLATE
        self.angle_generation_template = ANGLE_GENERATION_PROMPT # Corrected typo ANMA_GENERATION_PROMPT to ANGLE_GENERATION_PROMPT

    # Perplexity-specific methods are removed.

    def get_claude_prompts(self, query, client_info, general_instructions, angle, variant_num, previous_variant_max_num, dynamic_uniqueness_constraints):
        """
        Generates system and user prompts for Claude AI.
        Claude now drafts directly from the query and angle.
        """
        client_name = client_info.get('name', 'N/A')
        client_guidelines = client_info.get('guidelines', 'N/A')
        
        client_context_for_prompt = f"Client Name: {client_name}\nClient Guidelines:\n{client_guidelines}"

        dynamic_constraints_str = ""
        if dynamic_uniqueness_constraints:
            dynamic_constraints_str = f"Additionally, DO NOT use phrases or ideas similar to these (from previous variants for this query): {', '.join(dynamic_uniqueness_constraints)}."
        
        formatted_template = self.claude_template.format(
            QUERY=query,
            CLIENT_INFO=client_context_for_prompt,
            GENERAL_INSTRUCTIONS=general_instructions,
            ANGLE=angle, # Pass the angle directly to Claude template
            VARIANT_NUM=variant_num,
            PREVIOUS_VARIANT_MAX_NUM=previous_variant_max_num,
            NUM_VARIANTS=NUM_VARIANTS_PER_QUERY, # Corrected typo NUM_VARIANTS_PER_QUERY
            DYNAMIC_NEGATIVE_CONSTRAINTS=dynamic_constraints_str
        )
        system_prompt = "You are an expert writer for HARO responses. Adhere strictly to all formatting, tone, and distinctness rules provided by the user and client-specific guidelines, including ALL negative constraints."
        user_prompt = formatted_template

        return {"system_prompt": system_prompt, "user_messages": [{"role": "user", "content": user_prompt}]}

    def get_openai_prompts(self, query, client_info, general_instructions, drafted_answer, variant_num, dynamic_uniqueness_constraints):
        client_name = client_info.get('name', 'N/A')
        client_guidelines = client_info.get('guidelines', 'N/A')

        client_context_for_prompt = f"Client Name: {client_name}\nClient Guidelines:\n{client_guidelines}"
        
        dynamic_constraints_str = ""
        if dynamic_uniqueness_constraints:
            dynamic_constraints_str = f"Additionally, ABSOLUTELY AVOID phrases or ideas similar to these (from other variants for this query): {', '.join(dynamic_uniqueness_constraints)}."

        formatted_template = self.openai_template.format(
            QUERY=query,
            CLIENT_INFO=client_context_for_prompt,
            GENERAL_INSTRUCTIONS=general_instructions,
            ANSWER=drafted_answer,
            DYNAMIC_NEGATIVE_CONSTRAINTS=dynamic_constraints_str
        )
        system_prompt = "You are a final editor for HARO responses. Refine the provided draft strictly adhering to all formatting, distinctness, and negative constraint rules, including ALL fixed and dynamic constraints."
        user_prompt = formatted_template

        return {"system_prompt": system_prompt, "user_messages": [{"role": "user", "content": user_prompt}]}

    def get_angle_generation_prompt(self, query, client_info, num_variants):
        client_name = client_info.get('name', 'N/A')
        client_guidelines = client_info.get('guidelines', 'N/A')
        
        return self.angle_generation_template.format(
            QUERY=query,
            CLIENT_INFO=f"Client Name: {client_name}\nClient Guidelines:\n{client_guidelines}",
            NUM_VARIANTS=num_variants
        )