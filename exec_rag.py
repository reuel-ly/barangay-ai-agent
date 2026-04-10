import json
import ollama
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from pathlib import Path
from datetime import datetime
import os
from langchain_ollama import OllamaLLM  # ← add this import

from google_services.google_api import create_service
from rag.get_embedding_function import get_embedding_function
from master_settings import (
    LLM_MODEL, LLM_MODEL_AGENT,
    K_similarity, PROMPT_TEXT,
    SYSTEM_PROMPT_AGENT, GOOGLE_DOCS_ID
)

CHROMA_PATH = "chroma"
CONVERSATION_FILE = "conversation_history.json"
MAX_MESSAGES = 20


# ─── Conversation Persistence ─────────────────────────────────
def load_messages(system_prompt: str) -> list:
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, 'r') as f:
            messages = json.load(f)
        print(f"[Resuming previous conversation — {len(messages)} messages]\n")
        return messages
    return [{'role': 'system', 'content': system_prompt}]


def save_messages(messages: list):
    # Convert Message objects to plain dicts before saving
    serializable = []
    for msg in messages:
        if isinstance(msg, dict):
            serializable.append(msg)
        else:
            # Convert Ollama Message object to dict
            serializable.append({
                "role": msg.role,
                "content": msg.content if msg.content else "",
            })

    with open(CONVERSATION_FILE, 'w') as f:
        json.dump(serializable, f, indent=2)


def clear_conversation(system_prompt: str) -> list:
    if os.path.exists(CONVERSATION_FILE):
        os.remove(CONVERSATION_FILE)
    print("[Conversation cleared]\n")
    return [{'role': 'system', 'content': system_prompt}]


def trim_messages(messages: list) -> list:
    system = messages[0]
    recent = messages[-MAX_MESSAGES:]
    result = [system] + recent

    # Normalize all to plain dicts
    normalized = []
    for msg in result:
        if isinstance(msg, dict):
            normalized.append(msg)
        else:
            normalized.append({
                "role": msg.role,
                "content": msg.content if msg.content else "",
            })
    return normalized


# ─── RAG ──────────────────────────────────────────────────────
def query_rag(query_text: str, conversation_history: list) -> dict:
    embedding_function = get_embedding_function()
    db = Chroma(
        persist_directory=CHROMA_PATH,   # ← no str() needed
        embedding_function=embedding_function
    )
    results = db.similarity_search_with_score(query_text, k=K_similarity)

    context_parts = []
    for doc, score in results:
        chunk_type = doc.metadata.get("type", "text").upper()
        context_parts.append(f"[{chunk_type}]\n{doc.page_content}")
    context_text = "\n\n---\n\n".join(context_parts)

    history_text = ""
    if conversation_history:
        history_lines = []
        for msg in conversation_history[-6:]:
            if msg["role"] in ["system", "tool"]:
                continue
            role = "Customer" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{role}: {msg['content']}")
        if history_lines:
            history_text = "Previous conversation:\n" + "\n".join(history_lines) + "\n\n"

    prompt_template = PromptTemplate(
        template=PROMPT_TEXT,
        input_variables=["context", "question"]
    )
    prompt = prompt_template.format(
        context=context_text,
        question=f"{history_text}Current question: {query_text}"
    )

    # ← Use OllamaLLM.invoke() instead of client.chat()
    model = OllamaLLM(model=LLM_MODEL)
    response_text = model.invoke(prompt)

    sources = [{"id": doc.metadata.get("id"), "score": score} for doc, score in results]
    return {"answer": response_text, "sources": sources}


# ─── Google Docs ──────────────────────────────────────────────
def construct_docs_service():
    SCOPES = ['https://www.googleapis.com/auth/documents']
    service = create_service(
        'google_services/credentials/credential.json',
        'docs', 'v1', SCOPES
    )
    return service


def write_grundfos_inquiry(service, document_id, company_name, company_address,
                            nature_of_business, contact_person, contact_number,
                            project_name, project_location, pump_application,
                            flow, head_tdh, voltage_requirement,
                            recommended_product=None):

    doc = service.documents().get(documentId=document_id).execute()
    end_index = doc['body']['content'][-1]['endIndex'] - 1

    recommendation_section = f"\nRecommended Product: {recommended_product}" if recommended_product else ""

    inquiry_text = f"""
GRUNDFOS PUMP INQUIRY
-------------------------------
Date: {datetime.now().strftime('%B %d, %Y')}

Company Information:
  Company Name:        {company_name}
  Company Address:     {company_address}
  Nature of Business:  {nature_of_business}
  Contact Person:      {contact_person}
  Contact Number:      {contact_number}

Project Details:
  Project Name:        {project_name}
  Project Location:    {project_location}
  Pump Application:    {pump_application}

Pump Requirements:
  Flow Rate:           {flow}
  Head / TDH:          {head_tdh}
  Voltage Requirement: {voltage_requirement}
{recommendation_section}
-------------------------------\n
"""

    requests = [{'insertText': {'location': {'index': end_index}, 'text': inquiry_text}}]
    response = service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}
    ).execute()

    print(f"  ✅ Inquiry written to Google Doc")
    return response


# ─── Tool Definitions ─────────────────────────────────────────
def get_tools():
    return [
        {
            'type': 'function',
            'function': {
                'name': 'search_documentation',
                'description': 'Search Grundfos documentation to answer technical questions about pumps.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string', 'description': 'Technical question to search for'}
                    },
                    'required': ['query']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'write_grundfos_inquiry',
                'description': 'Write a completed Grundfos pump inquiry to Google Docs. Only call when customer signals buying intent AND all fields are collected.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'company_name':        {'type': 'string'},
                        'company_address':     {'type': 'string'},
                        'nature_of_business':  {'type': 'string'},
                        'contact_person':      {'type': 'string'},
                        'contact_number':      {'type': 'string'},
                        'project_name':        {'type': 'string'},
                        'project_location':    {'type': 'string'},
                        'pump_application':    {'type': 'string'},
                        'flow':                {'type': 'string'},
                        'head_tdh':            {'type': 'string'},
                        'voltage_requirement': {'type': 'string'},
                        'recommended_product': {'type': 'string', 'description': 'Product recommended from documentation if any'}
                    },
                    'required': [
                        'company_name', 'company_address', 'nature_of_business',
                        'contact_person', 'contact_number', 'project_name',
                        'project_location', 'pump_application', 'flow',
                        'head_tdh', 'voltage_requirement'
                    ]
                }
            }
        }
    ]


# ─── Main Loop ────────────────────────────────────────────────
def run():
    client = ollama.Client()
    system = SYSTEM_PROMPT_AGENT.strip()
    messages = load_messages(system)
    service = construct_docs_service()

    expected_args = [
        'company_name', 'company_address', 'nature_of_business',
        'contact_person', 'contact_number', 'project_name',
        'project_location', 'pump_application', 'flow',
        'head_tdh', 'voltage_requirement', 'recommended_product'
    ]

    print("Grundfos Assistant")
    print("Ask me anything about Grundfos pumps.")
    print("Type 'exit' to quit, 'clear' to start a new conversation.\n")

    while True:
        prompt = input("You: ").strip()

        if prompt.lower() == 'exit':
            save_messages(messages)
            print('Goodbye!')
            break

        if prompt.lower() == 'clear':
            messages = clear_conversation(system)
            continue

        if not prompt:
            continue

        messages.append({'role': 'user', 'content': prompt})

        response = client.chat(
            model=LLM_MODEL_AGENT,
            messages=trim_messages(messages),
            tools=get_tools()
        )
        messages.append(response['message'])

        if not response['message'].get('tool_calls'):
            save_messages(messages)
            print(f"Agent: {response['message']['content']}\n")
            continue

        rag_was_called = False

        for tool in response['message']['tool_calls']:
            tool_name = tool['function']['name']
            tool_args = tool['function']['arguments']

            if tool_name == 'search_documentation':
                print(f"\n[Searching: {tool_args['query']}]\n")
                rag_result = query_rag(tool_args['query'], messages)

                print(f"Agent: {rag_result['answer']}\n")
                rag_was_called = True

                messages.append({
                    'role': 'tool',
                    'content': json.dumps({
                        "answer": rag_result["answer"],
                        "sources": [s["id"] for s in rag_result["sources"]]
                    })
                })
                messages.append({
                    'role': 'assistant',
                    'content': rag_result["answer"]
                })

            elif tool_name == 'write_grundfos_inquiry':
                print("\n[Writing inquiry to Google Docs...]\n")
                filtered_args = {k: v for k, v in tool_args.items() if k in expected_args}
                write_grundfos_inquiry(
                    **filtered_args,
                    service=service,
                    document_id=GOOGLE_DOCS_ID
                )
                messages.append({
                    'role': 'tool',
                    'content': '{"inquiry_written": true}'
                })

        if not rag_was_called:
            final_response = client.chat(
                model=LLM_MODEL_AGENT,
                messages=trim_messages(messages),
                stream=False
            )
            messages.append(final_response['message'])
            print(f"Agent: {final_response['message']['content']}\n")

        save_messages(messages)


if __name__ == "__main__":
    run()