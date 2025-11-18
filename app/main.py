# Import config early to suppress warnings before ADK imports
from app.configs import app as app_config  # This will apply warnings filters

from app.services import ADKService
import asyncio
import dotenv
import pandas as pd
import os
from tqdm import tqdm

async def main():
    
    # Load the environment variables
    dotenv.load_dotenv()

    user_id = "Pouria"
    agent_mode = "alumni_researcher"

    # Initialize the ADK service with user_id and agent_mode
    adk_service = ADKService(user_id=user_id, agent_mode=agent_mode)
    # Initialize session and runner
    await adk_service.initialize()

    # Get the initial data
    # Get project root (one level up from app/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(project_root, "data", "residents_base_info.csv")
    initial_data = pd.read_csv(csv_path) 

    # Truncate to the first 10 rows
    initial_data = initial_data.head(10)

    # update_dict to store the results
    update_data = []        
    for index, row in tqdm(initial_data.iterrows(), total=len(initial_data), desc="Processing alumni", leave=True):

        try:
            alumni_name = row["First Name"] + " " + row["Last Name"]
            year_of_entry = row["Entry Year"]
            
            # Construct query
            query = f"alumni name: {alumni_name}, year of entry: {year_of_entry}"
            
            response, token_counts = await adk_service.get_agent_response(
                query=query,
            )
            
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
            
            # Create row data with practice information, social media links, and additional info
            # Token columns will be added at the end
            row_data = {
                "Name": alumni_name,
                "Year of Entry to Yale": year_of_entry,
                "Current Practices Names": response.current_practices_names or "",
                "Current Practices URLs": response.current_practices_urls or "",
                "Current Practice Narrative": response.current_practice_narrative or "",
                "Additional Information": response.additional_information or "",
                "X (Twitter) Link": response.x_twitter_link or "",
                "LinkedIn Link": response.linkedin_link or "",
                "Doximity Link": response.doximity_link or "",
                "Google Scholar Link": response.google_scholar_link or "",
                "Facebook Link": response.facebook_link or "",
            }
            
            # Add token counts at the end
            token_data = {
                "Total tokens used": token_counts.get("total_token_count", 0),
                "Prompt tokens used": token_counts.get("prompt_token_count", 0),
                "Candidates tokens used": token_counts.get("candidates_token_count", 0),
                "Cached content tokens used": token_counts.get("cached_content_token_count", 0),
                "Thoughts tokens used": token_counts.get("thoughts_token_count", 0),
            }
            
            # Combine row data with token data (tokens at the end)
            row_data.update(token_data)
            update_data.append(row_data)
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
    
    # Ensure token columns are at the end by reordering columns if needed
    token_columns = ["Total tokens used", "Prompt tokens used", "Candidates tokens used", 
                     "Cached content tokens used", "Thoughts tokens used"]
    other_columns = [col for col in results_df.columns if col not in token_columns]
    # Reorder: all other columns first, then token columns at the end
    column_order = other_columns + [col for col in token_columns if col in results_df.columns]
    results_df = results_df[column_order]
    
    results_df.to_csv(os.path.join(project_root, "data", "alumni_results.csv"), index=False)
    print(f"Results saved to {os.path.join(project_root, 'data', 'alumni_results.csv')}")

if __name__ == "__main__":
    asyncio.run(main())