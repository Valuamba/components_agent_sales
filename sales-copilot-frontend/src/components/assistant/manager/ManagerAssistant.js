import AssistantContainer from "../AssistantContainer";


const ManagerAssistatant = () => {


    return <AssistantContainer name="Manager Assistant">
        <div>
            <span>
            Agent: Customer Service Representative (CSR)
            State: InitialInquiryResponse
            Task: A new customer has sent an inquiry for a Firetrol Battery Charger AS-2001. Please extract the necessary details from the email, such as the brand name, part number, and any other relevant information. Draft an initial response to acknowledge the receipt of the inquiry and inform them that we are processing their request.
            </span>
        </div>    
    </AssistantContainer>
    
}


export default ManagerAssistatant;