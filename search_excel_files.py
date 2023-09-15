import os
import pandas as pd
from zipfile import BadZipFile

def count_partial_occurrences(target_list, directory):
    count_dict = {target: 0 for target in target_list}

    for file in os.listdir(directory):
        if (file.endswith(".xlsx") or file.endswith(".xls")) and not file.startswith('.~'):
            file_path = os.path.join(directory, file)
            engine = 'openpyxl' if file.endswith('.xlsx') else 'xlrd'

            try:
                excel_data = pd.read_excel(file_path, engine=engine)
                for target in target_list:
                    count_dict[target] += excel_data.apply(lambda col: col.astype(str).str.contains(target, case=False, na=False)).sum().sum()
            except BadZipFile:
                print(f"Error: The file '{file}' is not a valid Excel file or is corrupted.")

    return count_dict

# Replace this with the list of partial names you want to search for
target_models = ['Private Car', 'TESLA', 'Model 3', 'Model Y', 'EQA', 'I4', 'I3', 'LEAF', 'Electric']

# Get the directory of the script itself
script_directory = os.path.dirname(os.path.abspath(__file__))

model_counts = count_partial_occurrences(target_models, script_directory)

for model, count in model_counts.items():
    print(f'The partial name "{model}" appears {count} times in the Excel files.')