# app_constants.py
import os


LAST_N_MESSAGES = 10
TIMESTAMP_FORMAT = '%b %d, %Y %H:%M:%S'

#  Scenario path
project_options = {'cert': ['Get_Feature'],
                   'development': ['Get_Feature']}


SCENARIO_PATH = os.path.join(os.getcwd(), 'docs/guide/text_feature')
SCENARIOS = [os.path.join(SCENARIO_PATH, f) for f in os.listdir(SCENARIO_PATH)
             if os.path.isfile(os.path.join(SCENARIO_PATH, f))]


# Bases on the project name, get the scenarios from the docs/guide/text_scenario folder
def get_scenario_path(scenario_name):
    # Ensure the scenario_name is in lowercase
    scenario_name = scenario_name.lower()

    # List all files in the SCENARIO_PATH
    SCENARIO_NAMES_PATH = [os.path.join(SCENARIO_PATH, f) for f in os.listdir(SCENARIO_PATH)
                           if os.path.isfile(os.path.join(SCENARIO_PATH, f))]

    # Iterate through the files and check for a match
    for file_path in SCENARIO_NAMES_PATH:
        file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0].lower()
        if scenario_name in file_name_without_extension:
            return file_path

    # If no match found, return None
    return None


# Get only the scenario file names
SCENARIO_NAMES = [f.split('/')[-1] for f in SCENARIOS]
# Get only the scenario file names without the full path
SCENARIO_NAMES_NO_PATH = [f.split('/')[-1] for f in SCENARIOS]


# Get the project type from project_options
PROJECT_TYPE_OPTIONS = list(project_options.keys())

# Get the project names from project_options
PROJECT_NAMES_OPTIONS = project_options[PROJECT_TYPE_OPTIONS[0]]
