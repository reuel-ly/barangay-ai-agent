import json
import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from ragas.run_config import RunConfig
import numpy as np

from settings import LLM_MODEL, EMBEDDING_MODEL

EVAL_FILE = "rag/eval_data.json"


def run_ragas():
    # ── Load saved results ────────────────────────────────────
    if not os.path.exists(EVAL_FILE):
        print(f"❌ No eval data found at {EVAL_FILE}")
        print("Run query_data.py first and ask some questions.")
        return

    with open(EVAL_FILE, 'r') as f:
        data = json.load(f)

    print(f"✅ Loaded {len(data)} Q&A entries from {EVAL_FILE}\n")

    # ── Build RAGAS dataset ───────────────────────────────────
    dataset = Dataset.from_dict({
        "question": [d["question"] for d in data],
        "answer":   [d["answer"]   for d in data],
        "contexts": [d["contexts"] for d in data],
    })

    # ── Wrap Ollama models for RAGAS ──────────────────────────
    ragas_llm = LangchainLLMWrapper(OllamaLLM(model=LLM_MODEL))
    ragas_embeddings = LangchainEmbeddingsWrapper(
        OllamaEmbeddings(model=EMBEDDING_MODEL)
    )

    # ── Run evaluation ────────────────────────────────────────
    print("Running RAGAS evaluation (this may take a few minutes)...\n")
    result = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,       # answer grounded in retrieved context?
            
        ],
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        run_config=RunConfig(
        max_workers=1,
        timeout=1800  # seconds
    )
    )

    # ── Print summary ─────────────────────────────────────────
    print("\n" + "=" * 50)
    print("RAGAS EVALUATION SUMMARY")
    print("=" * 50)
    faithfulness_score = result['faithfulness']
    faithfulness_mean = np.mean(faithfulness_score) if isinstance(faithfulness_score, list) else faithfulness_score
    print(f"  Faithfulness:      {faithfulness_mean:.4f}")
    
    print("=" * 50)

    # ── Per question breakdown ────────────────────────────────
    df = result.to_pandas()

    print("\n--- Per Question Breakdown ---")

    for i in range(len(df)):
        question_text = dataset[i]["question"]
        score = df.loc[i, "faithfulness"]

        score_mean = np.mean(score) if isinstance(score, list) else score

        print(f"\nQ{i+1}: {question_text[:80]}")
        print(f"  Faithfulness: {score_mean:.4f}")


    # ── Save results ──────────────────────────────────────────
    df.to_csv("ragas_results.csv", index=False)
    print("\n✅ Full results saved to ragas_results.csv")


if __name__ == "__main__":
    run_ragas()