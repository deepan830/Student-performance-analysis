"""PROJECT 3 — EDUCATION  |  STEP 2: Python EDA"""
import sqlite3,pandas as pd,numpy as np
import matplotlib.pyplot as plt,matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import warnings; warnings.filterwarnings('ignore')

conn=sqlite3.connect('/home/claude/project3_education/education.db')
df=pd.read_sql_query("SELECT * FROM students",conn); conn.close()
df['attendance_pct']=df['attendance_pct'].fillna(df['attendance_pct'].median())
df['study_hours_day']=df['study_hours_day'].fillna(df['study_hours_day'].median())
df['prev_gpa']=df['prev_gpa'].fillna(df['prev_gpa'].median())
df=df.drop_duplicates()
df['attendance_band']=pd.cut(df['attendance_pct'],bins=[0,59,74,89,100],labels=['<60%','60-74%','75-89%','90%+'])
df['grade_letter']=pd.cut(df['final_grade'],bins=[0,4,5.5,7,8.5,10],labels=['F','D','C','B','A'])
df.to_csv('/home/claude/project3_education/cleaned_students.csv',index=False)

BG='#0A0F1E';CARD='#111827';TEXT='#F0F4FF';SUB='#8896B3'
A1='#6EE7B7';A2='#F87171';A3='#93C5FD';A4='#FCD34D'
fig=plt.figure(figsize=(20,15));fig.patch.set_facecolor(BG)
gs=gridspec.GridSpec(3,3,hspace=0.45,wspace=0.35)
def sa(ax,t):
    ax.set_facecolor(CARD);ax.tick_params(colors=SUB,labelsize=8)
    ax.set_title(t,color=TEXT,fontsize=10,fontweight='bold',pad=8)
    for sp in ax.spines.values(): sp.set_edgecolor('#1F2937')
    ax.xaxis.label.set_color(SUB);ax.yaxis.label.set_color(SUB)
fig.text(0.5,0.97,'🎓  Student Performance & Dropout Risk Dashboard',ha='center',fontsize=16,fontweight='bold',color=TEXT)
fig.text(0.5,0.945,'SQL Extracted · Python Cleaned · 1,500 Students · 6 Departments',ha='center',fontsize=9,color=SUB)
for i,(lbl,val,col) in enumerate([
    ('Total Students',f"{len(df):,}",A1),
    ('Dropout Risk Rate',f"{df['dropout_risk'].mean()*100:.1f}%",A2),
    ('Avg Final Grade',f"{df['final_grade'].mean():.2f}/10",A3),
]):
    ax=fig.add_subplot(gs[0,i]);ax.set_facecolor(CARD)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_xticks([]);ax.set_yticks([])
    ax.text(0.5,0.6,val,ha='center',va='center',fontsize=26,fontweight='bold',color=col,transform=ax.transAxes)
    ax.text(0.5,0.2,lbl,ha='center',va='center',fontsize=9,color=SUB,transform=ax.transAxes)
ax1=fig.add_subplot(gs[1,0])
gc=df['grade_letter'].value_counts().reindex(['A','B','C','D','F'])
b1=ax1.bar(gc.index,gc.values,color=[A1,A3,A4,A2,'#EF4444'],edgecolor='none',width=0.6)
for b,v in zip(b1,gc.values): ax1.text(b.get_x()+b.get_width()/2,v+5,str(v),ha='center',color=TEXT,fontsize=8,fontweight='bold')
sa(ax1,'📝 Grade Distribution');ax1.set_ylabel('Students')
ax2=fig.add_subplot(gs[1,1])
for risk,col,lbl in [(0,A1,'Low Risk'),(1,A2,'High Risk')]:
    sub=df[df['dropout_risk']==risk]
    ax2.scatter(sub['study_hours_day'],sub['final_grade'],c=col,alpha=0.4,s=20,label=lbl,edgecolors='none')
sa(ax2,'📚 Study Hours vs Final Grade');ax2.set_xlabel('Study Hours/Day');ax2.set_ylabel('Final Grade')
ax2.legend(fontsize=8,labelcolor=TEXT,facecolor=CARD,edgecolor='#1F2937')
ax3=fig.add_subplot(gs[1,2])
dd=df.groupby('department')['dropout_risk'].mean().sort_values()
ax3.barh(dd.index,dd.values*100,color=[A2 if v==dd.max() else '#1F3A5F' for v in dd.values],edgecolor='none')
for p,v in zip(ax3.patches,dd.values*100): ax3.text(v+0.3,p.get_y()+p.get_height()/2,f'{v:.1f}%',va='center',color=TEXT,fontsize=7)
sa(ax3,'⚠️ Dropout Risk by Department');ax3.set_xlabel('Dropout Risk (%)')
ax4=fig.add_subplot(gs[2,0])
h2=df.groupby(['attendance_band','grade_letter'],observed=True)['student_id'].count().unstack().fillna(0)
sns.heatmap(h2,ax=ax4,cmap='Blues',annot=True,fmt='.0f',annot_kws={'size':8,'color':TEXT},
            linewidths=0.5,linecolor=BG,cbar_kws={'shrink':0.8})
ax4.set_facecolor(CARD);ax4.set_title('📊 Attendance Band × Grade',color=TEXT,fontsize=10,fontweight='bold',pad=8)
ax4.tick_params(colors=SUB,labelsize=8);ax4.set_xlabel('Grade',color=SUB);ax4.set_ylabel('Attendance Band',color=SUB)
ax5=fig.add_subplot(gs[2,1])
eo=['None','High School','Graduate','Post-Graduate']
eg=df.groupby('parental_edu')['final_grade'].mean().reindex(eo)
b5=ax5.bar(eo,eg.values,color=[A3,A1,A4,A2],edgecolor='none',width=0.6)
for b,v in zip(b5,eg.values): ax5.text(b.get_x()+b.get_width()/2,v+0.05,f'{v:.2f}',ha='center',color=TEXT,fontsize=8,fontweight='bold')
ax5.set_xticklabels(eo,rotation=15,ha='right')
sa(ax5,'👨‍👩‍🎓 Parental Education vs Avg Grade');ax5.set_ylabel('Avg Grade')
ax6=fig.add_subplot(gs[2,2])
ld=df.groupby('location')['dropout_risk'].mean()
wedges,texts,ats=ax6.pie(ld.values,labels=ld.index,autopct='%1.1f%%',colors=[A3,A1,A2],
    startangle=90,wedgeprops={'edgecolor':BG,'linewidth':2,'width':0.65},
    textprops={'color':TEXT,'fontsize':9})
for at in ats: at.set_color(BG);at.set_fontweight('bold')
ax6.set_facecolor(CARD);ax6.set_title('🌏 Dropout Risk by Location',color=TEXT,fontsize=10,fontweight='bold',pad=8)
plt.savefig('/home/claude/project3_education/education_dashboard.png',dpi=150,bbox_inches='tight',facecolor=BG)
print("✅ Dashboard saved")

le=LabelEncoder(); dml=df.copy()
for c in ['gender','department','location','study_mode','parental_edu']:
    dml[c]=le.fit_transform(dml[c].astype(str))
feats=['gender','department','location','study_mode','parental_edu',
       'internet_access','part_time_job','study_hours_day','attendance_pct','prev_gpa']
X=dml[feats]; y=dml['dropout_risk']
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=7)
model=GradientBoostingClassifier(n_estimators=100,random_state=7)
model.fit(Xtr,ytr); ypred=model.predict(Xte)
print("\n🤖 Gradient Boosting Results:"); print(classification_report(yte,ypred))
imp=pd.Series(model.feature_importances_,index=feats).sort_values()
fig2,ax=plt.subplots(figsize=(9,6)); fig2.patch.set_facecolor(BG);ax.set_facecolor(CARD)
ax.barh(imp.index,imp.values,color=[A2 if v==imp.max() else '#1E3A5F' for v in imp.values],edgecolor='none')
for i,(idx,v) in enumerate(imp.items()): ax.text(v+0.002,i,f'{v:.3f}',va='center',color=TEXT,fontsize=8)
ax.set_title('Feature Importance — Dropout Risk Model',color=TEXT,fontsize=12,fontweight='bold',pad=10)
ax.tick_params(colors=SUB);ax.set_xlabel('Importance',color=SUB)
for sp in ax.spines.values(): sp.set_edgecolor('#1F2937')
plt.tight_layout()
plt.savefig('/home/claude/project3_education/feature_importance.png',dpi=150,bbox_inches='tight',facecolor=BG)
print("✅ Feature importance saved\n✅ STEP 2 COMPLETE")
