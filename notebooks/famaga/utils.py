import csv
import re
import json


def generate_csv():
    # File path to save the CSV file
    file_path = 'scenarios.csv'
    
    # Open a file to write
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Scenario id', 'Motivation', 'Details'])
        
        # Write the data
        for item in json_output:
            details = "\n".join(item['scenarios'])  # Combine scenarios into a single string
            writer.writerow([item['id'], item['motivation'], details])


def get_scenarios(scenario):
    scenarios = re.split(r"Scenario \d+: ", scenario)[1:]
    
    # Define a list to hold all scenarios as dictionaries
    scenarios_json = []
    
    # Parse each scenario
    for idx, scenario in enumerate(scenarios, start=1):
        lines = scenario.strip().split("\n")
        title = lines[0].strip('"')
        motivation = lines[1].split("Motivation: ", 1)[1]
        
        # Extract scenario details into a list, skipping the title and motivation which are already extracted
        # details = lines[2:]
        details = [s.strip('- ').strip() for s in lines[2:]]
        
        # Construct the dictionary for the current scenario
        scenario_dict = {
            "id": idx,
            "title": title,
            "motivation": motivation,
            "scenarios": details
        }
        scenarios_json.append(scenario_dict)

    return scenarios_json