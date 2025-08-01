import pandas as pd
import os

input_file = r'C:\Users\91888\PycharmProjects\PythonETL\data\input\employees.csv'
output_file='C:/Users/91888/PycharmProjects/PythonETL/data/output/employees_output.csv'

os.makedirs(os.path.dirname(output_file),exist_ok=True)

if not os.path.exists(input_file):
    raise FileNotFoundError(f"Source file not found: {input_file}")

df=pd.read_csv(input_file)
df_filtered = df[df['salary'] > 70000].copy()
df_filtered.rename(columns={
'emp_id': 'employee_id',
    'emp_name': 'employee_name',
    'department': 'dept_name',
    'salary': 'monthly_salary'
}, inplace=True)
df_filtered['processed_date'] = pd.Timestamp.now()

if os.path.exists(output_file):
    df_filtered.to_csv(output_file, mode='a', header= False, index=False)
    print(f"appended data to output file: {output_file}")
else:
    df_filtered.to_csv(output_file, index=False)
    print(f"new output file created : {output_file}")