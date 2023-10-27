import hashlib
from dataclasses import dataclass
from typing import Optional

import backoff
import openai
from openai.error import RateLimitError

_OPENAI_GPT_4_MODEL = "gpt-4-0314"
_OPENAI_GPT_4_INSTRUCTIONS = """Generate a brief answer for the following question that summarizes all of the relevant claims provided without any outside knowledge or opinions.
If there is no answer based on the claims, write "N/A".
Your response has to be limited to one sentence, and sound scientific.
It must be simple enough to be understood by a non-scientific person reading the claims.
Try to generalize across similar concepts in order to shorten the response, while maintaining accuracy.  If the question can be answered shorter, answer shorter.
If you need to list things, categorize them into at most 3 buckets of related concepts.
Start your response with "These studies suggest".
If claims that suggest different answers to the question (or show both positive/negative effects), include both answers, and start your response with "some studies suggest" or "most studies suggest" and then add "while other studies" before writing the other side.
If all claims agree, start your response with "these studies suggest" and write even simpler."""  # noqa: E501
_OPENAI_GPT_4_TEMPERATURE = 0
MODEL_VERSION_QUESTION_SUMMARIZER = f"{_OPENAI_GPT_4_MODEL}:{hashlib.sha256(_OPENAI_GPT_4_INSTRUCTIONS.encode()).hexdigest()[:8]}"  # noqa: E501

_OPENAI_DAVINCI_MODEL = (
    "davinci:ft-consensus:finetune-davinci-summarization-v05-2023-03-22-09-33-30"  # noqa: E501
)
_OPENAI_DAVINCI_BASE_PROMPT = "Based on the context, give a concise, scientific answer to the question. Always include all relevant points of view. If there are no relevant answers, do not answer the question."  # noqa: E501
_OPENAI_DAVINCI_TEMPERATURE = 0
_OPENAI_DAVINCI_MAX_TOKENS = 128
FALLBACK_MODEL_VERSION_QUESTION_SUMMARIZER = f"{_OPENAI_DAVINCI_MODEL}:{hashlib.sha256(_OPENAI_DAVINCI_BASE_PROMPT.encode()).hexdigest()[:8]}"  # noqa: E501


@dataclass(frozen=True)
class QuestionSummarizerPrediction:
    summary: Optional[str]


def _cleanup_summary(summary: Optional[str]) -> Optional[str]:
    if summary:
        # Remove default prefix
        summary = summary.strip().removeprefix("Summary: ")
        # Convert to None if N/A string
        summary = None if summary.strip() == "N/A" else summary
    return summary


@dataclass(frozen=True)
class SummarizerInput:
    messages: list[dict]


def create_summarize_question_gpt4_input(
    question: str,
    answers: list[str],
) -> SummarizerInput:
    if len(answers) == 0:
        return SummarizerInput(messages=[])
    claims = "\n\n".join([f"Claim: {x}" for x in answers])
    prompt = f"Question: {question}\n\n{claims}"
    messages = [
        {"role": "system", "content": _OPENAI_GPT_4_INSTRUCTIONS},
        {"role": "user", "content": prompt},
    ]
    return SummarizerInput(messages=messages)


async def summarize_question_gpt4(
    input: SummarizerInput,
) -> QuestionSummarizerPrediction:
    """
    Returns a GPT-4 summary of the answer to the question given the answers.
    """
    if len(input.messages) == 0:
        return QuestionSummarizerPrediction(summary=None)

    result = await openai.ChatCompletion.acreate(
        model=_OPENAI_GPT_4_MODEL,
        temperature=_OPENAI_GPT_4_TEMPERATURE,
        messages=input.messages,
    )
    summary = result["choices"][0]["message"]["content"]
    summary = _cleanup_summary(summary)
    return QuestionSummarizerPrediction(summary=summary)


@backoff.on_exception(backoff.expo, RateLimitError, max_time=10)
async def summarize_question_gpt4_with_backoff(
    input: SummarizerInput,
) -> QuestionSummarizerPrediction:
    """Same as above, but recalls openai with exponential backoff on failures."""
    return await summarize_question_gpt4(input=input)


async def summarize_question_davinci(
    question: str,
    answers: list[str],
) -> QuestionSummarizerPrediction:
    """
    Returns a davinci summary of the answer to the question given the answers.
    """
    if len(answers) == 0:
        return QuestionSummarizerPrediction(summary=None)

    joined_answers = "\n".join(answers)
    prompt = f"{_OPENAI_DAVINCI_BASE_PROMPT}\n{joined_answers}\n{question}\n\n###\n\n"
    result = await openai.Completion.acreate(
        model=_OPENAI_DAVINCI_MODEL,
        prompt=prompt,
        temperature=_OPENAI_DAVINCI_TEMPERATURE,
        max_tokens=_OPENAI_DAVINCI_MAX_TOKENS,
        stop="END",
    )
    summary = result["choices"][0]["text"]
    summary = _cleanup_summary(summary)
    return QuestionSummarizerPrediction(summary=summary)
