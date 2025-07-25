# src/config.py

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# AI API Keys
ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY_PLACEHOLDER"))
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_PLACEHOLDER"))

# AI Models
CLAUDE_MODEL = "claude-3-5-sonnet-20240620"
OPENAI_MODEL = "gpt-4o-2024-08-06"

# Other configurations
CONCURRENT_AI_CALLS = 2
NUM_VARIANTS_PER_QUERY = 5

# --- FIXED NEGATIVE EXAMPLES AND OPENING SENTENCE CONSTRAINTS ---
FIXED_NEGATIVE_EXAMPLES_PROMPT_PART = """
Specifically AVOID common phrases like "smooth shopping space," "turning casual Browse into buying," "jumped X% conversions," "without leaving their favorite apps." Also, do NOT use generic examples like "eco-friendly water bottles," "fashion lookbook", or "swimwear."
"""

OPENING_SENTENCE_CONSTRAINT_PROMPT_PART = """
The first sentence of *each variant* must be *radically different* in structure and phrasing from the others. Do NOT begin with variations of "Shoppable posts have changed/transformed/are changing/are..." as the opening. Instead, dive directly into a unique insight, a surprising fact, a specific action, or a distinct benefit relevant to *only this variant's angle*, without a broad introductory statement about shoppable posts in general. Think: a unique headline for each answer.
"""

# --- PROMPT TEMPLATES ---

# Perplexity Prompt Template (removed from active use in pipeline)
PERPLEXITY_PROMPT_TEMPLATE = """Your task is to generate exactly one distinct, expert answer. The answer must be written {RESEARCH_ANGLE}. The answer must be completely unique in viewpoint, content, and details—do not repeat insights, stories, or angles. Start the answer directly with the expert information, using clear, authoritative language. Do not include conversational filler or introductory phrases. Do not include "Variant X:", "Variant [number]:", numbered lists, or any other explicit variant labeling in your output. Only provide facts or insights without mentioning any dates, years, or timeframes. Never reference "2025" or any year in the output."""


# FIX IS HERE: Aggressive Claude prompt for humanization, storytelling, WITHOUT attribution
CLAUDE_PROMPT_TEMPLATE = f"""You are an exceptional expert writer for HARO responses. Your primary goal is to draft a uniquely compelling and deeply humanized 2-paragraph answer, drawing directly from the HARO query and the specified unique angle. Prioritize sounding genuinely human, relatable, and insightful over rigid formality.

--- STRICT RULES (Prioritize Humanization & Storytelling) ---
1. **Human Tone & Conversational Flow (CRITICAL):** The tone MUST be human, casual, and emotionally intelligent—like a seasoned expert sharing a genuine, relatable insight with a smart friend. Focus on natural conversational rhythm. Use active voice and first-person plural (we, our, us) where possible. Incorporate contractions naturally.
2. **Compelling Anecdote/Moment (First Paragraph):** Within the first paragraph, or flowing naturally into the second, include **one brief, compelling, and specific anecdote, a real client scenario, or a pivotal team moment/discovery**. This should illustrate the insight and make it tangible, avoiding abstraction. Make it a mini-story or a "turning point" (e.g., "We discovered this during our quarterly review when...", or "One client, struggling with X, found that...").
3. **Vivid & Concrete Language:** Avoid abstract or generic phrasing. Describe a **tangible change, a specific shift in approach, or a clear turning point** where possible.
4. **Content Quality:** Make the content feel original, rare, and fit for Forbes, Fast Company, or HubSpot expert panels, delivered with a genuinely human voice. The answer should address all sub-questions cohesively.
5. **Format:** Provide EXACTLY two paragraphs per answer. Ensure a clear, single blank line separates the two paragraphs. Each paragraph MUST be 50-60 words (aim for four sentences per paragraph). Each sentence MUST be 10-15 words maximum.
6. **No Fluff/Robotic Language:** Avoid fluff, clichés, robotic language, bullet points, numbered lists, and em dashes.
7. **No Labels/Intros:** NEVER include any variant labels (e.g., "Variant 1:"), numbered lists, or introductory phrases (e.g., "Here is the answer:").
8. **EXTREME DISTINCTNESS (CRITICAL):** Each of the {{NUM_VARIANTS}} answers for this query MUST be 100% distinct in content, viewpoint, and starting sentence. Ensure absolutely no overlap in core ideas or examples across answers for the same HARO query. This specific answer is for Variant {{VARIANT_NUM}}, and it MUST be unique from Variants 1-{{PREVIOUS_VARIANT_MAX_NUM}}.
9. **OPENING SENTENCE MANDATE:** {OPENING_SENTENCE_CONSTRAINT_PROMPT_PART.strip()}
10. **NEGATIVE CONSTRAINT:** {FIXED_NEGATIVE_EXAMPLES_PROMPT_PART.strip()} {{DYNAMIC_NEGATIVE_CONSTRAINTS}} Focus ONLY on the unique angle provided.
11. **No Dates/Timeframes:** Do not mention dates or timeframes.

--- CONTEXT ---
HARO Query: {{QUERY}}
Client Info: {{CLIENT_INFO}}
General Guidelines: {{GENERAL_INSTRUCTIONS}}
Unique Angle for This Variant: {{ANGLE}}
--- END ---

Your response must be EXACTLY what goes into a Google Sheet cell. No extra lines, no variant number. Just the answer, nothing else. Crucially, ensure your response consists of two distinct paragraphs, separated by a blank line, and nothing more or less.
"""

# FIX IS HERE: Greatly strengthened OpenAI prompt for humanization and jargon reduction, preserving new elements, WITHOUT attribution
OPENAI_PROMPT_TEMPLATE = f"""You are the final humanization, simplification, and authenticity expert. Your singular mission is to refine the provided draft to be **indistinguishable from genuine human writing, utterly free of jargon, highly relatable, and perfectly preserving the core anecdote**.

--- YOUR PRIMARY & MOST CRITICAL TASK (Highest Priority) ---
* **100% Humanization & Authenticity:** Ensure the text reads as if a highly knowledgeable, empathetic, and engaging human expert wrote it. It must flow naturally, conversationally, and with genuine warmth. Inject natural contractions and common, clear phrasing. Re-emphasize first-person plural (we, our, us) where appropriate to maintain a company-level voice.
* **Jargon Purge:** Systematically identify and **REMOVE ALL unnecessary jargon, technical terms, and overly complex phrasing**. Replace them with simple, everyday words that a broad, intelligent audience can easily understand without needing industry expertise.
* **Drastic Simplification:** Reduce the overall complexity of the language by **a firm 15-20%**. This means choosing simpler synonyms, breaking down long sentences, and rephrasing convoluted ideas.
* **Preserve & Enhance Anecdote/Moment:** Ensure the brief anecdote, client scenario, or pivotal team moment is crystal clear, impactful, and relatable after polishing. Do NOT abstract it or remove its vividness.
* **Relatability & Vividness:** Make the language more concrete and relatable. Avoid any remaining generic or abstract phrasing.

--- STRICT FORMATTING & CONTENT RULES (Adhere While Humanizing) ---
1.  **Format:** Output EXACTLY two paragraphs. Each paragraph MUST be 50-60 words. Ensure a clear, single blank line separates the two paragraphs.
2.  **Core Content Preservation:** Absolutely preserve the original meaning, all facts, and the overall structure. You are refining language, *not* rewriting content or removing important details.
3.  **No Labels/Intros:** NEVER include any variant labels (e.g., "Variant 1:"), numbered lists, or introductory phrases (e.g., "Here is the refined answer:"). Return ONLY the two refined paragraphs.
4.  **CRITICAL DISTINCTNESS:** This refined answer must adhere perfectly to its unique angle. ABSOLUTELY AVOID ANY REPETITION IN CORE CONCEPTS, OPENING LINES, OR KEY TAKEAWAYS that might appear in other potential variants for the same HARO query. Ensure it feels 100% distinct.
5.  **NEGATIVE EXAMPLES TO AVOID (for this *specific* query):** {FIXED_NEGATIVE_EXAMPLES_PROMPT_PART.strip()} {{DYNAMIC_NEGATIVE_CONSTRAINTS}} Your focus is on polishing the *unique content* from the draft.
6.  **No Dates/Timeframes:** Do not mention dates or timeframes.
7.  **OPENING SENTENCE CONSTRAINT:** {OPENING_SENTENCE_CONSTRAINT_PROMPT_PART.strip()} General Guidelines: {{GENERAL_INSTRUCTIONS}}

--- CONTEXT ---
HARO Query: {{QUERY}}
Client Info: {{CLIENT_INFO}}
Draft to Refine: {{ANSWER}}
--- END ---

Return the refined two paragraphs only.
"""

ANGLE_GENERATION_PROMPT = """You are a creative strategist specializing in HARO responses.
For the given journalist query, generate {NUM_VARIANTS} entirely unique and distinct angles or perspectives from which an expert could answer.
Each angle must be:
- Highly specific and niche.
- Genuinely different from the others; no overlap in core concept.
- Actionable and researchable (i.e., not just a rephrasing of the query).
- Concise (1-2 sentences max per angle).
Do NOT include common ideas, generic advice, or obvious responses. Focus on truly novel hooks.
Provide ONLY the list of angles, one per line, prefixed with a hyphen "- ".

Journalist Query:
{QUERY}

Client Info:
{CLIENT_INFO}
"""