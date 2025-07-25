# src/ai_integrations.py

import asyncio
import re

from openai import AsyncOpenAI
# FIX IS HERE: Import AsyncAnthropic for async operations
from anthropic import Anthropic, AsyncAnthropic # Keep Anthropic for potential future reference, but use AsyncAnthropic for client
import httpx
from src.config import (
    ANTHROPIC_API_KEY, CLAUDE_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL,
    NUM_VARIANTS_PER_QUERY
)
from src.utils import get_logger, safe_async_call
from src.prompt_manager import PromptManager

logger = get_logger(__name__)

class AIService:
    def __init__(self):
        # Perplexity client is removed as per last instruction.
        # FIX IS HERE: Use AsyncAnthropic for Claude client
        self.claude_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.prompt_manager = PromptManager()

    async def generate_angles(self, query_text, client_info):
        prompt = self.prompt_manager.get_angle_generation_prompt(query_text, client_info, NUM_VARIANTS_PER_QUERY)
        try:
            response = await safe_async_call(
                self.openai_client.chat.completions.create,
                model=OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            response_content = response.choices[0].message.content
            angles = [line.strip().replace('- ', '') for line in response_content.split('\n') if line.strip().startswith('- ')]
            if not angles:
                 angles = [line.strip() for line in response_content.split('\n') if line.strip()][:NUM_VARIANTS_PER_QUERY]

            logger.info(f"Generated {len(angles)} angles for query: {query_text[:50]}...")
            return angles
        except Exception as e:
            logger.error(f"Error generating angles for query '{query_text[:50]}...': {e}")
            return [f"A unique perspective {i+1}" for i in range(NUM_VARIANTS_PER_QUERY)]

    # Perplexity_research method is removed

    async def claude_drafting(self, query, client_info, general_instructions, angle, variant_num, previous_variant_max_num, dynamic_uniqueness_constraints):
        """
        Stage 1 (now): Claude AI for Drafting, directly from query and angle.
        """
        prompts = self.prompt_manager.get_claude_prompts(
            query, client_info, general_instructions, angle,
            variant_num, previous_variant_max_num, dynamic_uniqueness_constraints
        )
        try:
            # self.claude_client is now AsyncAnthropic, so its .messages.create() method is awaitable
            response = await safe_async_call(
                self.claude_client.messages.create, # This should now work correctly
                model=CLAUDE_MODEL,
                max_tokens=750,
                temperature=(0.92 if variant_num >= 4 else 0.85),
                system=prompts["system_prompt"],
                messages=prompts["user_messages"]
            )
            draft = response.content[0].text
            logger.info("Claude drafting successful.")
            return draft
        except Exception as e:
            logger.error(f"Error during Claude drafting: {e}")
            raise

    async def openai_polish(self, query, client_info, general_instructions, drafted_answer, variant_num, dynamic_uniqueness_constraints):
        prompts = self.prompt_manager.get_openai_prompts(
            query, client_info, general_instructions, drafted_answer,
            variant_num, dynamic_uniqueness_constraints
        )
        try:
            response = await safe_async_call(
                self.openai_client.chat.completions.create,
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": prompts["system_prompt"]},
                    {"role": "user", "content": prompts["user_messages"][0]["content"]}
                ],
                temperature=0.65,
                max_tokens=900
            )
            polished_answer = response.choices[0].message.content
            logger.info("OpenAI polishing successful.")
            return polished_answer
        except Exception as e:
            logger.error(f"Error during OpenAI polishing: {e}")
            raise

    async def process_single_variant(self, query_id, query_text, client_info, parameters, angle, existing_variants_for_uniqueness, variant_num, previous_variant_max_num):
        try:
            # Stage 1 (now): Claude Drafting
            draft = await self.claude_drafting(
                query_text, client_info, parameters.get("general_instructions", ""),
                angle,
                variant_num, previous_variant_max_num, existing_variants_for_uniqueness
            )

            # Stage 2 (now): OpenAI Polish
            final_answer = await self.openai_polish(
                query_text, client_info, parameters.get("general_instructions", ""),
                draft, variant_num, existing_variants_for_uniqueness
            )
            
            # Post-processing
            processed_answer = remove_variant_label_prefix(final_answer)
            processed_answer = remove_dates(processed_answer)
            processed_answer = format_two_paragraphs(processed_answer)

            return {
                "query_id": query_id,
                "angle": angle,
                "research_output": "N/A (Perplexity removed)",
                "draft": draft,
                "final_answer": processed_answer,
                "status": "Success",
                "negative_constraints_applied": existing_variants_for_uniqueness
            }
        except Exception as e:
            logger.error(f"Failed to process variant for query {query_id}, angle '{angle[:50]}...': {e}")
            return {
                "query_id": query_id,
                "angle": angle,
                "research_output": "Error",
                "draft": "Error",
                "final_answer": f"Error processing variant: {e}",
                "status": "Failed",
                "negative_constraints_applied": []
            }

    async def process_query_with_variants(self, query_id, query_text, client_info, parameters):
        all_variants_for_query = []
        generated_final_answers_text = []

        angles = await self.generate_angles(query_text, client_info)
        if len(angles) < NUM_VARIANTS_PER_QUERY:
            logger.warning(f"Only {len(angles)} angles generated for query {query_id}. Expected {NUM_VARIANTS_PER_QUERY}.")
            for i in range(NUM_VARIANTS_PER_QUERY - len(angles)):
                angles.append(f"Additional unique perspective {len(angles) + i + 1}")

        for i, angle in enumerate(angles[:NUM_VARIANTS_PER_QUERY]):
            variant_num = i + 1
            previous_variant_max_num = i

            variant_result = await self.process_single_variant(
                query_id, query_text, client_info, parameters, angle,
                generated_final_answers_text,
                variant_num, previous_variant_max_num
            )
            all_variants_for_query.append(variant_result)
            if variant_result["status"] == "Success":
                generated_final_answers_text.append(variant_result["final_answer"])
            logger.info(f"Variant {variant_num}/{NUM_VARIANTS_PER_QUERY} for query {query_id} processed.")

        return {
            "query_id": query_id,
            "query_text": query_text,
            "client_info": client_info,
            "variants": all_variants_for_query
        }

    async def close(self):
        pass # No explicit async clients to close after removing Perplexity and using AsyncAnthropic/AsyncOpenAI

# --- POST-PROCESSING FUNCTIONS (from Apps Script - unchanged) ---
def format_two_paragraphs(text):
    if not text: return ''
    cleaned_text = text.replace('\r\n', '\n').replace('\r', '\n').strip()
    paragraphs = [p.strip() for p in cleaned_text.split('\n') if p.strip()]
    if len(paragraphs) == 1:
        original_text = paragraphs[0]
        words = original_text.split(' ')
        split_point_idx = -1
        midpoint = len(words) // 2
        for i in range(max(0, midpoint - 20), min(len(words), midpoint + 20)):
            if words[i].endswith('.') or words[i].endswith('?') or words[i].endswith('!'):
                split_point_idx = i + 1
                break
        if split_point_idx == -1:
            split_point_idx = midpoint
        first_para_words = words[:split_point_idx]
        second_para_words = words[split_point_idx:]
        paragraphs = [
            ' '.join(first_para_words).strip(),
            ' '.join(second_para_words).strip()
        ]
        paragraphs = [p for p in paragraphs if p]
    if len(paragraphs) > 2:
        paragraphs = [paragraphs[0], ' '.join(paragraphs[1:])]
    elif len(paragraphs) < 2:
        if len(paragraphs) == 1 and len(paragraphs[0].split(' ')) > 80:
            words = paragraphs[0].split(' ')
            midpoint = len(words) // 2
            paragraphs = [' '.join(words[:midpoint]), ' '.join(words[midpoint:])]
        else:
            return text
    p1_words = paragraphs[0].split(' ')
    p2_words = paragraphs[1].split(' ')
    while len(p1_words) > 60 and len(p2_words) < 60 and len(p1_words) > 50:
        p2_words.insert(0, p1_words.pop())
    while len(p2_words) > 60 and len(p1_words) < 60 and len(p2_words) > 50:
        p1_words.append(p2_words.pop(0))
    p1_words = p1_words[:65]
    p2_words = p2_words[:65]
    if len(p1_words) < 30 and len(p2_words) > 70:
        words_to_move = min(30 - len(p1_words), len(p2_words) - 50)
        p1_words.extend(p2_words[:words_to_move])
        p2_words = p2_words[words_to_move:]
    if len(p2_words) < 30 and len(p1_words) > 70:
        words_to_move = min(30 - len(p2_words), len(p1_words) - 50)
        p2_words.insert(0, *p1_words[len(p1_words) - words_to_move:])
        p1_words = p1_words[:len(p1_words) - words_to_move]
    return ' '.join(p1_words) + '\n\n' + ' '.join(p2_words)


def remove_variant_label_prefix(text):
    if not text: return ''
    return re.sub(r'^\s*Variant\s*\d+:\s*', '', text, flags=re.IGNORECASE).strip()

def remove_dates(text):
    if not text: return ''
    cleaned_text = text
    cleaned_text = re.sub(r'\b(19|20)\d{2}\b', '', cleaned_text)
    cleaned_text = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*(19|20)\d{2}\b', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\b\d{1,2}\/\d{1,2}\/(19|20)\d{2}\b', '', cleaned_text)
    cleaned_text = re.sub(r'\b\d{1,2}-\d{1,2}-(19|20)\d{2}\b', '', cleaned_text)
    cleaned_text = re.sub(r'\b(Q[1-4])\s*(\d{4})\b', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\b(this|next|last|current)\s+year\b', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\b(\d{4})\s*(\d{2}:\d{2}:\d{2})\b', '', cleaned_text)
    cleaned_text = re.sub(r',\s*(19|20)\d{2}\b', '', cleaned_text)
    cleaned_text = re.sub(r'\b(today|tomorrow|yesterday)\b', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\b(recent|upcoming|past)\s+(month|year|quarter|week)s?\b', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text).strip()
    return cleaned_text