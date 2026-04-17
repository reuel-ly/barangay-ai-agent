from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig
from langchain_groq import ChatGroq
from test.test_case import test_data
from rag.query_data import query_rag
from dotenv import load_dotenv
from rag.get_embedding_function import get_embedding_function
import json
import os
import time
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation in batches")

    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start index of test data (default: 0)"
    )

    parser.add_argument(
        "--end",
        type=int,
        default=5,
        help="End index of test data (default: 5)"
    )

    parser.add_argument(
        "--idx",
        type=int,
        default=0,
        help="Index of metrics to evaluate (default: 0)"
    )

    return parser.parse_args()

args = get_args()
start_idx = args.start
end_idx = args.end
idx = args.idx


list_metrics = [faithfulness, answer_relevancy, context_precision]
metric = list_metrics[idx]

start = time.perf_counter()

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

CACHE_FILE = "test/test_data/agent_responses.json"

# load agent responses
if not os.path.exists(CACHE_FILE):
    raise FileNotFoundError(
        f"Cache file not found: {CACHE_FILE}\n"
        "Please run 'python -m test.ragas' first to generate agent responses."
    )

print("[Loading cached agent responses...]")
with open(CACHE_FILE, "r") as f:
    cached = json.load(f)

test_data["answer"] = cached["answer"]
test_data["contexts"] = cached["contexts"]

# slicing the 5 test cases to evaluate
SLICE = slice(start_idx, end_idx) 

test_data = {k: v[SLICE] for k, v in test_data.items()}

eval_llm = LangchainLLMWrapper(ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    timeout=300,
    max_retries=3,
    n=1,
    ))
eval_embeddings = LangchainEmbeddingsWrapper(get_embedding_function())

run_config = RunConfig(
    max_workers=1,
    max_retries=5,
    max_wait=120,
    timeout=300,
)

eval_result = evaluate(
    Dataset.from_dict(test_data),
    metrics=[metric],
    llm=eval_llm,
    embeddings=eval_embeddings,
)

df = eval_result.to_pandas()

df.to_csv(f"test/test_data/eval_results_{metric.name}_{start_idx}-{end_idx}.csv", index=False)

end = time.perf_counter()

total_seconds = end - start

hours = int(total_seconds // 3600)
minutes = int((total_seconds % 3600) // 60)
seconds = total_seconds % 60

print(f"Total time: {hours}h {minutes}m {seconds:.2f}s")

