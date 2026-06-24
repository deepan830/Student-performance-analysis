"""PROJECT 3 — EDUCATION  |  STEP 1: SQL"""
import sqlite3,pandas as pd,numpy as np
np.random.seed(7); n=1500
depts=['Computer Science','Mechanical','Civil','Electronics','Business','Arts']
edu_levels=['None','High School','Graduate','Post-Graduate']
age=np.random.randint(18,90,n).astype(float)
study_hours=np.random.randint(1,10,n); attendance=np.random.randint(40,100,n)
prev_gpa=np.round(np.random.uniform(4.0,10.0,n),2)
internet=np.random.choice([0,1],n,p=[0.25,0.75])
ptjob=np.random.choice([0,1],n,p=[0.65,0.35])
final_grade=np.clip(prev_gpa*0.4+study_hours*0.3+attendance*0.03+internet*0.5-ptjob*0.4+np.random.normal(0,0.8,n),1,10).round(2)
dropout_risk=((attendance<60)*0.4+(study_hours<3)*0.3+(final_grade<5)*0.3+np.random.rand(n)*0.2>0.45).astype(int)
df=pd.DataFrame({
    'student_id':[f'STU{str(i).zfill(4)}' for i in range(1,n+1)],
    'gender':np.random.choice(['Male','Female'],n),
    'department':np.random.choice(depts,n),
    'location':np.random.choice(['Urban','Semi-Urban','Rural'],n,p=[0.45,0.30,0.25]),
    'study_mode':np.random.choice(['Full-Time','Part-Time'],n,p=[0.80,0.20]),
    'parental_edu':np.random.choice(edu_levels,n,p=[0.10,0.30,0.40,0.20]),
    'internet_access':internet,'part_time_job':ptjob,
    'study_hours_day':study_hours,'attendance_pct':attendance.astype(float),
    'prev_gpa':prev_gpa,'final_grade':final_grade,'dropout_risk':dropout_risk
})
for c in ['attendance_pct','study_hours_day','prev_gpa']:
    df.loc[df.sample(frac=0.04).index,c]=np.nan
conn=sqlite3.connect('/home/claude/project3_education/education.db')
df.to_sql('students',conn,if_exists='replace',index=False)
queries={
    "dept_performance":"""
        SELECT department,COUNT(*) AS students,
               ROUND(AVG(final_grade),2) AS avg_grade,
               ROUND(AVG(attendance_pct),1) AS avg_attendance,
               ROUND(AVG(dropout_risk)*100,2) AS dropout_rate_pct,
               ROUND(AVG(study_hours_day),1) AS avg_study_hours
        FROM students GROUP BY department ORDER BY dropout_rate_pct DESC""",
    "location_analysis":"""
        SELECT location,COUNT(*) AS students,
               ROUND(AVG(final_grade),2) AS avg_grade,
               ROUND(AVG(dropout_risk)*100,2) AS dropout_rate_pct,
               ROUND(AVG(attendance_pct),1) AS avg_attendance
        FROM students GROUP BY location ORDER BY dropout_rate_pct DESC""",
    "parental_edu_impact":"""
        SELECT parental_edu,COUNT(*) AS students,
               ROUND(AVG(final_grade),2) AS avg_grade,
               ROUND(AVG(dropout_risk)*100,2) AS dropout_rate_pct
        FROM students GROUP BY parental_edu ORDER BY avg_grade DESC""",
    "at_risk_students":"""
        SELECT student_id,department,attendance_pct,study_hours_day,
               final_grade,prev_gpa,dropout_risk
        FROM students
        WHERE dropout_risk=1 AND attendance_pct < 60
        ORDER BY final_grade ASC LIMIT 50"""
}
for name,sql in queries.items():
    r=pd.read_sql_query(sql,conn)
    r.to_csv(f'/home/claude/project3_education/sql_{name}.csv',index=False)
    print(f"✅ SQL '{name}' → {len(r)} rows")
conn.close(); print("✅ STEP 1 COMPLETE — Education DB ready")
