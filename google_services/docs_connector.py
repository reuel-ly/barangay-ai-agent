import json
import ollama

#Local Imports
from google_api import create_service
from settings import LLM_MODEL_AGENT, SYSTEM_PROMPT_AGENT, GOOGLE_DOCS_ID


# create a Google Docs service instance
def construct_docs_service():
    SCOPES = ['https://www.googleapis.com/auth/documents']
    service = create_service(
        'google_services/credentials/credential.json',
        'docs',
        'v1',
        SCOPES
    )
    return service

# function to write the inquiry details to the Google Doc
def write_grundfos_inquiry(service, document_id, company_name, company_address,
                            nature_of_business, contact_person, contact_number,
                            project_name, project_location, pump_application,
                            flow, head_tdh, voltage_requirement):

    doc = service.documents().get(documentId=document_id).execute()
    end_index = doc['body']['content'][-1]['endIndex'] - 1

    inquiry_text = f"""
                    GRUNDFOS PUMP INQUIRY RESPONSE
                    -------------------------------

                    Company Name: {company_name}
                    Company Address: {company_address}
                    Nature of Business: {nature_of_business}
                    Contact Person: {contact_person}
                    Contact Number: {contact_number}
                    Project Name / Reference: {project_name}
                    Project Location: {project_location}
                    Pump Application: {pump_application}

                    Pump Details:
                    Flow: {flow}
                    Head/TDH: {head_tdh}
                    Voltage Requirement on Site: {voltage_requirement}

                    -------------------------------\n
                    """

    requests = [
        {
            'insertText': {
                'location': {'index': end_index},
                'text': inquiry_text
            }
        }
    ]

    response = service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()

    return response

# Define the tool for the agent to call
def write_grundfos_inquiry_tool():
    return {
        'type': 'function',
        'function': {
            'name': 'write_grundfos_inquiry',
            'description': 'Write a filled-in Grundfos pump inquiry form to a Google Doc',
            'parameters': {
                'type': 'object',
                'properties': {
                    'company_name': {
                        'type': 'string',
                        'description': 'Name of the company making the inquiry'
                    },
                    'company_address': {
                        'type': 'string',
                        'description': 'Address of the company'
                    },
                    'nature_of_business': {
                        'type': 'string',
                        'description': 'Nature or industry of the business'
                    },
                    'contact_person': {
                        'type': 'string',
                        'description': 'Name of the contact person'
                    },
                    'contact_number': {
                        'type': 'string',
                        'description': 'Phone number of the contact person'
                    },
                    'project_name': {
                        'type': 'string',
                        'description': 'Project name, reference, or end user details'
                    },
                    'project_location': {
                        'type': 'string',
                        'description': 'Location of the project'
                    },
                    'pump_application': {
                        'type': 'string',
                        'description': 'Pump application type: Plumbing / Booster / Waste water / HVAC / Fire Protection'
                    },
                    'flow': {
                        'type': 'string',
                        'description': 'Required flow rate with unit (e.g. 100 gpm, 20 m3/hr)'
                    },
                    'head_tdh': {
                        'type': 'string',
                        'description': 'Required head or TDH with unit (e.g. 50 ft, 15 m)'
                    },
                    'voltage_requirement': {
                        'type': 'string',
                        'description': 'Voltage requirement on site (e.g. 230V/60Hz, 460V/3-phase)'
                    },
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

# Agent system prompt
def system_prompt():
    return SYSTEM_PROMPT_AGENT.strip()


def run():
    model = LLM_MODEL_AGENT
    client = ollama.Client()
    document_id = GOOGLE_DOCS_ID
    service = construct_docs_service()

    messages = [
        {
            'role': 'system',
            'content': system_prompt()
        }
    ]

    print("Grundfos Pump Inquiry Assistant")
    print("Provide your pump inquiry details, or type 'exit' to quit.\n")

    while True:
        prompt = input("You: ")
        if prompt.lower() == 'exit':
            print('Goodbye!')
            break

        messages.append({'role': 'user', 'content': prompt})

        response = client.chat(
            model=model,
            messages=messages,
            tools=[write_grundfos_inquiry_tool()]
        )
        messages.append(response['message'])

        if not response['message'].get('tool_calls'):
            # Try to parse the response as a manual tool call (fallback)
            try:
                content = response['message']['content']
                parsed = json.loads(content)
                if 'name' in parsed and parsed['name'] == 'write_grundfos_inquiry':
                    write_grundfos_inquiry(
                        **parsed['parameters'],
                        service=service,
                        document_id=document_id
                    )
                    messages.append({
                        'role': 'tool',
                        'content': '{"inquiry_written": true}'
                    })
                    final_response = client.chat(model=model, messages=messages, stream=False)
                    print("Agent:", final_response['message']['content'])
                    continue
            except json.JSONDecodeError:
                pass

            # Model is asking for more info or clarifying
            print("Agent:", response['message']['content'])
            continue

        # Tool was called normally
        if response['message'].get('tool_calls'):
            available_functions = {
                'write_grundfos_inquiry': write_grundfos_inquiry,
            }
            expected_args = [
                'company_name', 'company_address', 'nature_of_business',
                'contact_person', 'contact_number', 'project_name',
                'project_location', 'pump_application', 'flow',
                'head_tdh', 'voltage_requirement'
            ]
            for tool in response['message']['tool_calls']:
                function_to_call = available_functions[tool['function']['name']]
                filtered_args = {
                    k: v for k, v in tool['function']['arguments'].items()
                    if k in expected_args
                }
                function_to_call(
                    **filtered_args,
                    service=service,
                    document_id=document_id
                )
                messages.append({
                    'role': 'tool',
                    'content': '{"inquiry_written": true}'
                })

        final_response = client.chat(model=model, messages=messages, stream=False)
        messages.append(final_response['message'])
        print("Agent:", final_response['message']['content'])
        print()


if __name__ == "__main__":
    run()


"""
Example test input:
---
Our company is ABC Engineering, located at 123 Industrial St, Laguna. We are in the construction industry. Contact person is Maria Santos, 09171234567. Project is Eastwood Condo Building B, located in Quezon City. Pump application is booster. We need 80 gpm flow, 60 ft head, and 230V/60Hz single phase.
"""