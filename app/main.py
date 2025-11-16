from app.services import ADKService
from app.agents.background_finder_agent.subagents.formatter_agent import AccountInfo
import asyncio
import dotenv
import pandas as pd
import os
from tqdm import tqdm

async def main():
    
    # Load the environment variables
    dotenv.load_dotenv()

    user_id = "Pouria"
    agent_mode = "background_finder"

    # Initialize the ADK service with user_id and agent_mode
    adk_service = ADKService(user_id=user_id, agent_mode=agent_mode)
    # Initialize session and runner
    await adk_service.initialize()

    # Get the initial data
    # Get project root (one level up from app/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(project_root, "data", "residents_base_info.csv")
    initial_data = pd.read_csv(csv_path) 

    # Truncate to the first 3 rows
    initial_data = initial_data.head(3)

    # update_dict to store the results
    update_data = []        
    for index, row in tqdm(initial_data.iterrows(), total=len(initial_data), desc="Processing alumni", leave=True):

        try:
            alumni_name = row["First Name"] + " " + row["Last Name"]
            year_of_entry = row["Entry Year"]
            query = f"alumni name: {alumni_name}, year of entry: {year_of_entry}"
            response, token_counts = await adk_service.get_agent_response(query=query)
            
            if response is None:
                raise ValueError("Agent returned None response")
            
            if token_counts is None:
                token_counts = {
                    "total_token_count": 0,
                    "prompt_token_count": 0,
                    "candidates_token_count": 0,
                    "cached_content_token_count": 0,
                    "thoughts_token_count": 0,
                }
            
            # Safely extract account URLs (ensure we have at least 5 accounts)
            accounts = response.accounts if response.accounts else []
            # Ensure we have exactly 5 accounts, padding with empty ones if needed
            while len(accounts) < 5:
                accounts.append(AccountInfo(account_type="", account_url=""))
            
            update_data.append({
                "Name": alumni_name,
                "Year of Entry to Yale": year_of_entry,
                "X Profile URL": accounts[0].account_url if len(accounts) > 0 else "",
                "LinkedIn Profile URL": accounts[1].account_url if len(accounts) > 1 else "",
                "Facebook Profile URL": accounts[2].account_url if len(accounts) > 2 else "",
                "Doximity Profile URL": accounts[3].account_url if len(accounts) > 3 else "",
                "Google Scholar Profile URL": accounts[4].account_url if len(accounts) > 4 else "",
                "Subspecialties": response.subspecialties if response.subspecialties else [],
                "Current Practice Location (Country, State, City)": response.current_practice_location or "",
                "Current Practice Name": response.current_practice_name or "",
                "Current Practice URL": response.current_practice_url or "",
                "Current Practice Email": response.current_practice_email or "",
                "In current practice since (Year)": response.in_current_practice_since or "",
                "Additional Information": response.additional_information or "",
                "Total tokens used": token_counts.get("total_token_count", 0),
                "Prompt tokens used": token_counts.get("prompt_token_count", 0),
                "Candidates tokens used": token_counts.get("candidates_token_count", 0),
                "Cached content tokens used": token_counts.get("cached_content_token_count", 0),
                "Thoughts tokens used": token_counts.get("thoughts_token_count", 0),
            })
        except Exception as e:
            print(f"Error getting agent response for {alumni_name} with year of entry {year_of_entry} (index {index}): {e}")
            update_data.append({
                "Name": alumni_name,
                "Year of Entry to Yale": year_of_entry,
                "Error": str(e),
            })
            continue

    # Save the results to a csv file
    results_df = pd.DataFrame(update_data)
    results_df.to_csv(os.path.join(project_root, "data", "alumni_results.csv"), index=False)
    print(f"Results saved to {os.path.join(project_root, 'data', 'alumni_results.csv')}")

if __name__ == "__main__":
    asyncio.run(main())