import os

from dotenv import load_dotenv


ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW_DIR = os.path.join(ANALYSIS_DIR, "data_raw")
RESULTS_DIR = os.path.join(ANALYSIS_DIR, "results")
RUNS_DIR = os.path.join(ANALYSIS_DIR, "runs")
PROMPTS_DIR = os.path.join(ANALYSIS_DIR, "prompts")
ENV_FILE = os.path.join(ANALYSIS_DIR, ".env")

load_dotenv(ENV_FILE)


def load_analysis_env(env_file: str = ENV_FILE) -> None:
    load_dotenv(env_file)


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")
