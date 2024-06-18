import pandas as pd
import numpy as np
import streamlit as st
import pickle
import sklearn
import streamlit.components.v1 as components
from sklearn.preprocessing import QuantileTransformer
import mysql.connector
global conn

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password="Iri@Sql2024#",
    database="heart_disease_predict"
)


#model=pickle.load(open('model.sav','rb'))

st.title("Heart Disease Detection")

model=pickle.load(open('model.sav','rb'))
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)


# scaler = QuantileTransformer(output_distribution='normal')

menu=["Prediction","Contribute to the Data"]
choice=st.sidebar.radio("Menu",menu)

def user_data():
    age=st.number_input(min_value=18,max_value=100,value=None,step=1,placeholder="Enter your age",label='Enter Valid Age : ')
    sex=st.selectbox(options=[' ','Male','Female'],label="Select Gender",placeholder='Chiose Gender')
    cp=st.selectbox(options=[' ','Typical angina', 'Atypical angina', 'Non-anginal', 'Asymptomatic'],label="Choose type of Chest Pain : ")
    trestbps=st.number_input(min_value=70,max_value=200,value=None,placeholder="Enter your resting blood pressure",label="Enter resting blood pressure (in mm Hg on admission to the hospital)")
    chol=st.number_input(min_value=120,max_value=600,value=None,placeholder='Enter your Serum cholesterol',label='Serum cholesterol in mg/dl')
    fbs=st.radio('Is fasting blood sugar > 120 mg/dl',['Yes','No'])
    restecg=st.selectbox(options=[' ','Normal', 'STT abnormality', 'LV hypertrophy'],label='Resting electrocardiographic results')
    thalach=st.number_input(min_value=60,max_value=200,value=None,step=1,placeholder='Enter maximum heart rate achived (bpm) ',label="Maximum heart rate achieved")
    exang=st.radio("Exercise-induced angina",["True","False"])
    oldpeak=st.number_input(min_value=0.0,max_value=7.0,value=None,placeholder="Enter Correct ST Depression",label='ST depression induced by exercise relative to rest')
    slope=st.selectbox(options=[' ','Upsloping','Flat (horizontal)' ,'Downsloping'],label='Slope of the peak exercise ST segment')
    ca=st.select_slider(options=[0,1,2,3],label='Number of major vessels (0-3) colored by fluoroscopy')
    thal=st.selectbox(options=[" ","No Thalasemia",'Normal','Fixed defect','Reversible defect'],label='Condition of Blood disorder - Thalassemia ')
    

    feat_li=[sex,cp,restecg,slope,thal]
    for i in feat_li:
        if i==' ':
            st.toast("Select and Fill All The Input Correctly!")
        break
    if  age!=None and trestbps!=None and chol!=None and thalach!=None and  exang!=None and oldpeak!=None  and sex!= ' ' and cp != ' ' and restecg != ' ' and slope!=" " and thal !=' ' :
        param={'Male':1,'Female':0,'Typical angina':0,'Atypical angina':1,'Non-anginal':2,'Asymptomatic':3,'Normal':0,'STT abnormality':1,
                'LV hypertrophy':2,'Upsloping':0,'Flat (horizontal)':1 ,'Downsloping':2,"No Thalasemia":0,'Normal':1,
                'Fixed defect':2,'Reversible defect':3,"True":0,"False":1,'Yes':0,'No':1}
        sex_dt=param[sex]
        cp_dt=param[cp]
        restecg_dt=param[restecg]
        slope_dt=param[slope]
        thal_dt=param[thal]
        exang_dt=param[exang]
        fbs_dt=param[fbs]   

        user_data_fed={
                'age':age,
                'sex':sex_dt,
                'cp':cp_dt,
                'trestbps':trestbps,
                'chol':chol, 
                'fbs':fbs_dt, 
                'restecg':restecg_dt, 
                'thalach':thalach,
                'exang':exang_dt, 
                'oldpeak':oldpeak, 
                'slope':slope_dt, 
                'ca':ca, 
                'thal':thal_dt
            }
        report=pd.DataFrame(user_data_fed,index=[0])
        return report
    else:
        st.toast("Select All The Input Correctly!")
        return "Error"
def get_val(report_scaled):
    scaling_need=['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
    report_scaled[scaling_need]=scaler.transform(report_scaled[scaling_need])
    #st.write(report_scaled.head())
    val=model.predict(report_scaled)
    return val

if choice=='Prediction':
    st.subheader("Please give proper details to predict prone to Heart Disease")
    scaling_need=['age', 'trestbps', 'chol', 'thalach', 'oldpeak']

    report_scaled=user_data()
    if type(report_scaled)==str:
        st.warning(report_scaled)
    else:
        # report_scaled[scaling_need]=scaler.transform(report_scaled[scaling_need])
        # st.write(report_scaled.head())
        # ans=model.predict(report_scaled)
        ans=get_val(report_scaled)
        if ans==0:
            st.write("No possible Heart Disease")
        else:
            st.warning("Prone to Heart Disease")
if choice=='Contribute to the Data':
    user_input=user_data()
    submit=st.button("Add Your data to Dataset")
    #st.write(user_input)
    if submit:
        cur = conn.cursor()
        sql = "INSERT INTO original_data(`age`,`sex`,`cp`,`trestbps`,`chol`,`fbs`,`restecg`,`thalach`,`exang`,`oldpeak`,`slope`,`ca`,`thal`,`target`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ;"
        # tuple_arr = tuple(tuple(row) for row in user_input.values)
        
        # new_val=tuple_arr+(pred_val)
        # st.write(new_val) 
        l=[row for row in user_input.values[0]]
        #l[9]=round(float(l[9]),2)
        for i in range(0,len(l)):
            if i==9:
                l[i]=float(l[i])
            else:
                l[i]=int(l[i])
        pred_val=get_val(user_input)
        l.append(int(pred_val[0]))
        # val=[]
        # st.write(l)
        # for i in l:
        #     st.write(i)
        #     val.append(i)
        # st.write(val)
        data_tuple=tuple(l)
        st.write(f"We are adding following data into our dataset : {data_tuple}")     
        cur.execute(sql, data_tuple)  
        conn.commit()
        cur.close()
        conn.close()
        st.write("Data Added Successfully!")

            
            
            

            
            
        
            
           
   

        

      
    #data_fed=user_data()
    
        
        
        