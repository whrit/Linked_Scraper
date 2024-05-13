import pandas as pd

# Read the JSON file
universities = pd.read_json('world_universities.json')

# Filter U.S. universities
us_universities = universities[universities['country'] == 'United States']

# Extract the names of U.S. universities
us_university_names = us_universities['name']

# Save the list of U.S. universities to an Excel file
us_university_names.to_excel('us_universities.xlsx', index=False, header=False)
