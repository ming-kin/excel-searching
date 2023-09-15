from flask import Flask, request, render_template
import os
import pandas as pd
from zipfile import BadZipFile
import re
from datetime import datetime, timedelta

app = Flask(__name__)

def count_partial_occurrences(target_list, directory, selected_files):
    count_dict = {target: 0 for target in target_list}

    for file in selected_files:
        file_path = os.path.join(directory, file)
        engine = 'openpyxl' if file.endswith('.xlsx') else 'xlrd'

        try:
            excel_data = pd.read_excel(file_path, engine=engine)
            for target in target_list:
                count_dict[target] += excel_data.apply(lambda col: col.astype(str).str.contains(target, case=False, na=False)).sum().sum()
        except BadZipFile:
            print(f"Error: The file '{file}' is not a valid Excel file or is corrupted.")

    return count_dict

def extract_date_from_filename(filename):
    match = re.search(r'_([a-zA-Z]+)(\d+)\.xlsx', filename)
    if match:
        month, year = match.groups()
        return datetime.strptime(f'{month} {year}', '%b %Y')
    else:
        # Return a far future date if the filename does not match the pattern
        return datetime.today() + timedelta(days=100*365)

@app.route('/', methods=['GET', 'POST'])
def index():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    excel_files = [file for file in os.listdir(script_directory) if (file.endswith(".xlsx") or file.endswith(".xls")) and not file.startswith('.~')]
    
    # Sort the excel_files list based on the month and year in the file names
    excel_files.sort(key=extract_date_from_filename)

    if request.method == 'POST':
        # Collect names from input fields
        target_models = [request.form.get(f'name{i}') for i in range(1, 9) if request.form.get(f'name{i}')]

        selected_files = request.form.getlist('excel_files')
        model_counts = count_partial_occurrences(target_models, script_directory, selected_files)

        # Get the chart type from the form
        chart_type = request.form.get('chart_type')

        # Convert int64 values to int
        model_counts = {key: int(value) for key, value in model_counts.items()}

        return render_template('results.html', model_counts=model_counts, chart_type=chart_type)
    return render_template('index.html', excel_files=excel_files)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
