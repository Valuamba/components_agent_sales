class AssistantRequest {
    deal_id: number
    messaging_history: string
}

class AssistantResponse {
    tasks: [
        {
            type: "sendEmail",
            to: "customer",
            body: "We have sent message to manufacturer manager"
        },
        {
            type: "sendEmail",
            to: "manufacturer",
            body: "could you give us discount"
        }
    ]
    metadata: {
        tracing: {
            agent: "dialog-manager",
            raw_output: "...Conclusion:...."
            reasoning_steps: [
                {
                    type: "decisionPoint"
                    name: "User Request Processing"
                    observation: "This is the first message from the user."
                },
                {
                    type: "decisionPoint"
                    name: "Request Classification"
                    observation: "The user left a request indicating specific parts."
                },
                {
                    type: "action"
                    name: "Classify parts in the customer's request"
                    assignee: "sales-manager"
                    description: "Classify the specific part mentioned in the customer's request."
                    input_keys: ['message_id']
                    input: {
                        message_id: 1
                    }
                },
                {
                    type: "action"
                    name: "Send an offer to the customer"
                    task: "Send Offer to client"
                    assignee: "sales-manager"
                    description: "Send an offer to the client for the specific part they requested."
                }
            ]
        }
    }
}


class AssistantResponseV2 {
    tasks: [
        {
            type: "sendOfferToCustomer",
            parts_data: {
                parts: [
                    {
                        amount: 0,
                        brand_name: "string",
                        part_number: "string"
                    }
                ],
                client: {
                    country: "string",
                    domain: "string",
                    email: "string",
                    office_country: "string"
                },
                deal_id: 0,
                message_id: 0,
                agent_task_id: 0
            }

        }
    ]
}


