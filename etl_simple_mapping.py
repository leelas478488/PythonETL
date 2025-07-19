import pandas as pd

df = pd.read_csv("employees.csv")
print(df)
df.rename(columns={
    "emp_id":"Employee_id",
    "first_name":"fst_name",
    "last_name":"lst_name",
    "department":"dept",
    "salary":"pay"
}, inplace=True)

df.to_csv("target_employees.csv",index=False)
print(df)