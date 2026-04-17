from ragas import evaluate
from ragas.metrics.collections import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
from ragas.llms import LangchainLLMWrapper
from langchain_groq import ChatGroq
from test.test_case import test_data
from rag.query_data import query_rag
import os
import json
import time

start = time.perf_counter()

CACHE_FILE = "test/test_data/agent_responses.json"


if os.path.exists(CACHE_FILE):
    print("[Loading cached agent responses...]")
    with open(CACHE_FILE, "r") as f:
        cached = json.load(f)
    test_data["answer"] = cached["answer"]
    test_data["contexts"] = cached["contexts"]
else:
    
    for q in test_data["question"]:
        print(f"[Running agent on test question: {q}]")
        result = query_rag(q, history=[])
        test_data["answer"].append(result["answer"])
        test_data["contexts"].append(result["retrieved_texts"])

   
    with open(CACHE_FILE, "w") as f:
        json.dump({
            "answer": test_data["answer"],
            "contexts": test_data["contexts"]
        }, f, indent=2)
    print(f"[Saved agent responses to {CACHE_FILE}]")

end = time.perf_counter()

total_seconds = end - start

hours = int(total_seconds // 3600)
minutes = int((total_seconds % 3600) // 60)
seconds = total_seconds % 60

print(f"Total time: {hours}h {minutes}m {seconds:.2f}s")