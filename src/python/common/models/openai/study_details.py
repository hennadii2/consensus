import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import backoff
import openai
from openai.error import RateLimitError

_OPENAI_GPT_4_MODEL = "gpt-4-0613"
_OPENAI_GPT_4_TEMPERATURE = 0

_POPULATION_INSTRUCTIONS = """
You will be provided with the abstract of a research paper. Your task is to describe the population(s) that participated in the experiment or was analyzed by authors in one very short sentence under 75 characters. Your answer should look something like this: "Older adults (50-71 years)" or "Male Rats" or "women with breast cancer and controls" or "patients aged 15-55 years old, both male and female", or "Patients with Dementia"",  "Broiler Chickens", "Healthy adults", "College athletes".

If the abstract says something like: "We examined brains from people with  PDD (N = 29), DLB (N = 27), and AD (N = 15) and comparison subjects without depression or dementia (N = 24)" your response should be: "People with PDD, DLB and AD and healthy controls"

If the abstract says something like: "Results: 54 T2DM patients (53.7% women, mean age 53.5+/-21yr)" your response should be: "Women T2DM patients"

You should not list anything about the sample size of the experiment. Your response must not be more than one very short sentence and you are allowed to generalize and summarize in the interest of being short.

If the research paper is not an actual experiment (e.g., an analysis of econometric data, an opinion piece, a book review, a background literature review, a theoretical paper), please write back: "n/a". If the paper does not clearly list any attributes of the population that they studied, please write back: "n/a". Your answer should only contain information about the experiment participants and nothing more. Your response must be less than 75 characters.
"""  # noqa: E501

_METHOD_INSTRUCTIONS = """
You will be provided with the abstract of a research paper. Your task is to give a very short, less-than-one sentence description of the type of study that was conducted.

Your answer should look something like this: "Randomized Controlled Trial", "Meta analysis", "Retrospective review", "Survey and data analysis", "pilot phase II, open label, nonrandomized trial", Model development and comparison", "Controlled experimental study", "Hospital-based case-control study", "In vitro experiment", "Epidemiological analysis", "In vivo experiment with microinjections", "Controlled pharmacological intervention study", "Case report", "Case Series", "Systematic Review", "Comprehensive Review".

You are allowed to generalize and summarize and your response should be able to understood by a non-expert. You should not list anything about the sample size of the experiment. Your response must not be more than one short sentence and not more than 75 characters. If the paper does not clearly list the type of study they conducted, write back "n/a".
"""  # noqa: E501

_OUTCOME_INSTRUCTIONS = """
You will be provided with the abstract of a research paper. Your task is to give a very short, less-than-one sentence description of the main outcome that was measured in the study. Your response should look something like: "Short Term Memory", "Self-assessed stress levels", "Quality of sleep index", "The burden on welfare programs",  "Standardized Test Scores" "VO2 Max Levels", "Flu-like symptoms", "The benefits of mindfulness", "Adverse effects of Zinc", "Anti-depressive properties of fish oil". Simplify your response as much as possible, for instance instead saying "Accuracy of EMIBA assay in confirming Lyme disease in cancer patients", just say "Accuracy of EMIBA assay".

If there are multiple outcomes measure, you must list each outcome as comma-separated list like: "Backward Number Recall, Spatial Recall, Long Term Memory" or "Restless leg symptoms, quality of sleep, side effects of Benzodiazepines". This list should look something like: "Changes in body weight, lean mass and muscle mass" or "Cortisol levels, serum zinc levels and depression severity scores". Do everything you can to shorten this list. If you can group together similar outcomes into one concept,  do it. If the outcomes are not a central part of the experiment, do not bother listing them. For example, if a paper says something like: "Overall one-year survival was 50% for all status 1 recipients. The primary-acute subgroup (n = 63) experienced a 57% one-year survival compared with 50% for the primary-chronic (n = 51) subgroup (P = 0.07). Of the reTx-acute recipients (n = 43), 44% were alive at one year in comparison with 20% for the reTx-chronic (n = 11) group (P = 0.18). There was no significant difference in survival for the following: transplant center, blood group compatibility with donors, age, preservation solution, or graft size. For patients retranslated for acute reasons (primary graft nonfunction (PGNF) or hepatic artery thrombosis [HAT]), survival was significantly better if a second donor was found within 3 days of relisting (52% vs. 20%; P = 0.012)" your response should just be "one-year survival rates".

You are allowed to generalize and summarize and your response should be very short and able to understood by a non-expert. Do no provide any details that are not about the outcomes measured and make your response as short as possible. Do not provide any details about the population of the study, the sample size, or the intervention used. If the paper does not clearly list the outcomes they were measuring, write back "n/a".
"""  # noqa: E501

_POPULATION_HASH = hashlib.sha256(_POPULATION_INSTRUCTIONS.encode()).hexdigest()[:8]
_METHOD_HASH = hashlib.sha256(_METHOD_INSTRUCTIONS.encode()).hexdigest()[:8]
_OUTCOME_HASH = hashlib.sha256(_OUTCOME_INSTRUCTIONS.encode()).hexdigest()[:8]

MODEL_VERSION_STUDY_DETAILS = (
    f"{_OPENAI_GPT_4_MODEL}:{_POPULATION_HASH}:{_METHOD_HASH}:{_OUTCOME_HASH}"  # noqa: E501
)

NA_RESPONSE_LOWERCASE = "n/a"


class StudyDetailsType(Enum):
    POPULATION = "population"
    METHOD = "method"
    OUTCOME = "outcome"


@dataclass(frozen=True)
class StudyDetailsPrediction:
    details: Optional[str]


@dataclass(frozen=True)
class StudyDetailsInput:
    messages: list[dict]


def _get_instructions(study_details_type: StudyDetailsType) -> str:
    if study_details_type == StudyDetailsType.POPULATION:
        return _POPULATION_INSTRUCTIONS
    elif study_details_type == StudyDetailsType.METHOD:
        return _METHOD_INSTRUCTIONS
    elif study_details_type == StudyDetailsType.OUTCOME:
        return _OUTCOME_INSTRUCTIONS
    raise NotImplementedError(
        "Failed to get study details instructions: unknown type: {study_details_type}"
    )


def create_study_details_gpt4_input(
    study_details_type: StudyDetailsType,
    abstract: str,
) -> StudyDetailsInput:
    if len(abstract) == 0:
        return StudyDetailsInput(messages=[])

    instructions = _get_instructions(study_details_type)
    prompt = f"Abstract: {abstract}"
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": prompt},
    ]
    return StudyDetailsInput(messages=messages)


async def generate_study_details_gpt4(
    input: StudyDetailsInput,
) -> StudyDetailsPrediction:
    """
    Returns a GPT-4 output of a study details prompt.
    """
    if len(input.messages) == 0:
        return StudyDetailsPrediction(details=None)

    result = await openai.ChatCompletion.acreate(
        model=_OPENAI_GPT_4_MODEL,
        temperature=_OPENAI_GPT_4_TEMPERATURE,
        messages=input.messages,
    )
    details = result["choices"][0]["message"]["content"]

    # The model can return N/A, we let it through and standardize by lowercaseing
    if details.lower() == NA_RESPONSE_LOWERCASE:
        details = NA_RESPONSE_LOWERCASE

    return StudyDetailsPrediction(details=details)


@backoff.on_exception(backoff.expo, RateLimitError, max_time=10)
async def generate_study_details_gpt4_with_backoff(
    input: StudyDetailsInput,
) -> StudyDetailsPrediction:
    """Same as above, but recalls openai with exponential backoff on failures."""
    return await generate_study_details_gpt4(input=input)
