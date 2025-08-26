# main_crew.py

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import os
# ✅ Import ALL your tools from your single, consolidated tools.py file

from Task_duplicate_finder_tool import duplicate_finder_tool
from Task_Convert_To_CSV import json_to_csv_converter_tool
from Testing_scraping import polymarket_scraper_tool, manifold_scraper_tool, predictit_scraper_tool,save_json_tool 



load_dotenv()

# Your working LLM configuration
llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# =================================================================
# DEFINE ALL AGENTS
# =================================================================

# Agent 1: Scraper
market_scraper_agent = Agent(
    role="Prediction Market Web Scraper",
    goal="Fetch the latest market data from Polymarket, Manifold Markets, and PredictIt.",
    backstory="An expert web scraper who knows the APIs of prediction markets inside and out.",
    tools=[polymarket_scraper_tool, manifold_scraper_tool, predictit_scraper_tool],
    verbose=True,
    llm=llm
)

# Agent 2: Aggregator
data_aggregator_agent = Agent(
    role="Data Aggregation Manager",
    goal="Combine data from various sources and save it into a unified JSON file.",
    backstory="A meticulous data manager who ensures all collected information is properly structured and stored.",
    tools=[save_json_tool],
    verbose=True,
    llm=llm
)

# Agent 3: Duplicate Analyzer
duplicate_analyzer_agent = Agent(
    role='Duplicate Data Analyzer',
    goal='Analyze a JSON dataset for duplicates based on a key, add a flag, and save the result.',
    backstory='You are an expert in data processing and deduplication.',
    tools=[duplicate_finder_tool],
    verbose=True,
    llm=llm
)

# Agent 4: CSV Converter
csv_converter_agent = Agent(
    role='Data Conversion Specialist',
    goal='Efficiently convert a JSON data file into a well-structured CSV format, handling any data inconsistencies.',
    backstory='An expert in data formats and file conversions, you are known for your speed and accuracy.',
    tools=[json_to_csv_converter_tool],
    verbose=True,
    llm=llm
)

# =================================================================
# DEFINE ALL TASKS IN SEQUENCE
# =================================================================

# --- Scraping Phase ---
scrape_polymarket_task = Task(description="Scrape Polymarket data.", expected_output="A list of Polymarket market data.", agent=market_scraper_agent)
scrape_manifold_task = Task(description="Scrape Manifold Markets data.", expected_output="A list of Manifold Markets market data.", agent=market_scraper_agent)
scrape_predictit_task = Task(description="Scrape PredictIt data.", expected_output="A list of PredictIt market data.", agent=market_scraper_agent)

# --- Aggregation Phase ---
aggregate_data_task = Task(
    description="Combine data from all scraping tasks and save it to the file at '{raw_json_output_file}'.",
    expected_output="Confirmation of saving the raw combined data.",
    agent=data_aggregator_agent,
    context=[scrape_polymarket_task, scrape_manifold_task, scrape_predictit_task]
)

# --- Processing Phase ---
analyze_duplicates_task = Task(
    description="Load the raw JSON file from the previous step. Find duplicates using the '{duplicate_key}' key. Save the result to '{processed_json_output_file}'.",
    expected_output="Confirmation of saving the processed data with duplicate flags.",
    agent=duplicate_analyzer_agent,
    context=[aggregate_data_task]
)

# --- Final Conversion Phase ---
convert_to_csv_task = Task(
    description="Load the processed JSON file from the previous step. Convert it to a CSV file and save it to '{final_csv_output_file}'.",
    expected_output="Confirmation of saving the final CSV file.",
    agent=csv_converter_agent,
    context=[analyze_duplicates_task]
)

# =================================================================
# ASSEMBLE THE FULL CREW
# =================================================================
full_pipeline_crew = Crew(
    agents=[market_scraper_agent, data_aggregator_agent, duplicate_analyzer_agent, csv_converter_agent],
    tasks=[
        scrape_polymarket_task, 
        scrape_manifold_task, 
        scrape_predictit_task, 
        aggregate_data_task,
        analyze_duplicates_task,
        convert_to_csv_task
    ],
    verbose=True
)

# =================================================================
# DEFINE WORKFLOW INPUTS AND RUN THE CREW
# =================================================================
inputs = {
    'raw_json_output_file': 'C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/1_combined_raw_data.json',
    'duplicate_key': 'product', # Using 'product' as the key to find duplicates
    'processed_json_output_file': 'C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/2_data_with_duplicates.json',
    'final_csv_output_file': 'C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/3_final_output.csv'
}

print("🚀 Starting the Full Data Pipeline Crew...")
result = full_pipeline_crew.kickoff(inputs=inputs)

print("\n\n########################")
print("## ✅ Full Pipeline Execution Finished!")
print(f"## Final Result from the last task: {result}")
print("########################")