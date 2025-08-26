from crewai import Agent,Task,Crew
from dotenv import load_dotenv
import os
load_dotenv()
from Task import duplicate_finder_tool

from langchain_google_genai import ChatGoogleGenerativeAI
llm=ChatGoogleGenerativeAI(model="google/gemini-pro",
                           verbose=True,
                           temperature=0.5,
                           google_api_key=os.getenv("GOOGLE_API_KEY")
                           )

# Define the Agent
duplicate_analyzer = Agent(
    role='Duplicate Analyzer',
    goal='Analyze JSON dataset for duplicates and update the JSON with duplicate flags',
    backstory='You are an expert in data processing and deduplication.',
    tools=[duplicate_finder_tool],
    verbose=True,
    memory=True,
    llm=llm
)

# Define the Task
analyze_duplicates_task = Task(
    description=(
        "Load the JSON file from {input_file}. "
        "Find duplicates based on the key {duplicate_key}. "
        "Mark duplicates with 'is_duplicate': True, non-duplicates with False. "
        "Save the updated JSON to {output_file}."
    ),
    expected_output='A report on the number of duplicates found and confirmation of updated JSON.',
    tools=[duplicate_finder_tool],
    agent=duplicate_analyzer
)

# Create the Crew
crew = Crew(
    agents=[duplicate_analyzer],
    tasks=[analyze_duplicates_task],
    verbose=True
)

# Run the Crew with inputs
inputs = {
    'input_file': 'C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/combined_data.json',  # Replace with your JSON file path
    'duplicate_key': 'id',  # Replace with the key to check for duplicates (e.g., 'email', 'name')
    'output_file': 'C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/updated_dataset.json'  # Output file path
}

result = crew.kickoff(inputs=inputs)
print(result)