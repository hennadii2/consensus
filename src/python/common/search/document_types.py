from enum import Enum


class FieldOfStudyKeywordEnum(Enum):
    MEDICINE = "Medicine"
    BIOLOGY = "Biology"
    COMPUTER_SCIENCE = "Computer Science"
    CHEMISTRY = "Chemistry"
    PSYCHOLOGY = "Psychology"
    PHYSICS = "Physics"
    MATERIALS_SCIENCE = "Materials Science"
    ENGINEERING = "Engineering"
    ENVIRONMENTAL_SCIENCE = "Environmental Science"
    BUSINESS = "Business"
    ECONOMICS = "Economics"
    MATHEMATICS = "Mathematics"
    POLITICAL_SCIENCE = "Political Science"
    AGRICULTURE = "Agricultural And Food Sciences"
    EDUCATION = "Education"
    SOCIOLOGY = "Sociology"
    GEOLOGY = "Geology"
    GEOGRAPHY = "Geography"
    HISTORY = "History"
    ARTS = "Art"
    PHILOSOPHY = "Philosophy"
    LAW = "Law"
    LINGUISTICS = "Linguistics"


class StudyTypeKeywordEnum(Enum):
    """
    All possible study types strings saved to search index documents.
    """

    THRESHOLD_NOT_MET = "threshold not met"
    OTHER = "other"
    LITERATURE_REVIEW = "literature review"
    SYSTEMATIC_REVIEW = "systematic review"
    CASE_STUDY = "case report"
    META_ANALYSIS = "meta-analysis"
    RCT = "rct"
    NON_RCT_IN_VITRO = "non-rct in vitro"
    NON_RCT_EXPERIMENTAL = "non-rct experimental"
    NON_RCT_OTHER = "non-rct other"
    NON_RCT_OBSERVATIONAL_STUDY = "non-rct observational study"
    NON_RCT_NON_BIOMEDPLUS = "non-rct non-biomedplus"
    # not a real study type in the data, but need this for filtering
    _ANIMAL_STUDY = "animal"


class ControlledStudyKeywordEnum(Enum):
    CONTROLLED = "controlled"
    NOT_CONTROLLED = "not controlled"


class HumanStudyKeywordEnum(Enum):
    HUMAN = "human"
    ANIMAL = "animal"
    OTHER = "other"
