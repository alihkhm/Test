"""
Created on Sun Dec  9 17:39:41 2018

@author: Ali
"""

import pandas as pd
import math
from datetime import datetime
from datetime import timedelta

#------------------------------------------- reading data
Employees = pd.read_csv('Data/employees.csv')
Shifts = pd.read_csv('Data/shifts.csv')

Shifts['Date']=pd.to_datetime(Shifts['Date'],format='%d/%m/%Y')

#------------------------------------------- setting up parameters
min_date = min(Shifts['Date'])
max_date = max(Shifts['Date'])
total_shifts = (max_date.day - min_date.day + 1) * 3
total_employees = len(Employees)
maxShiftsAweekPP = math.ceil((max_date.day - min_date.day + 1)*8/total_employees)
Skill_Ave = Employees["Skill Level"].mean()
Minimum_Ave_Skill = 0.8 * Skill_Ave       # minimum required average skill threshold in a shift
temp = [[-1] * 5 for i in range(total_shifts)]
schedule = pd.DataFrame(data=temp, columns=["Date","Shift","Employee1","Employee2","Employee3"])      
#schedule = pd.DataFrame(columns=list(["Date","Shift","Employees"]))
Employees["Shifts"] = 0
Employees["Shifts"] = pd.to_numeric(Employees["Shifts"])
global emp_list_day 
emp_list_day = list([])

# supervisor arrangement setup based on skill level
Supervision = 1      # 0: no supervision - random selection of employees
                     # 1: each shift will have one high skill level employee

#-------------------------------------------
def get_table(shift):
    for supervision_status in range(0,Supervision+1):
        emp = get_employees(shift, supervision_status)
        if emp == 0:
            return -1    
        for e in emp:
            Employees["Shifts"].iloc[e] = Employees["Shifts"].iloc[e] +1
    return 1

#-------------------------------------------
def get_employees(shift, supervisor):
    day_num = int((shift-1)/3) + 1 
    shift_num = shift%3
    if shift%3 == 0:
        shift_num = 3

    num_of_employees = 3
    if shift_num == 3:
        num_of_employees = 2
    if Supervision == 1 and supervisor == 0:
        num_of_employees = 1    # choosing one supervisor for each shift
    if Supervision == 1 and supervisor == 1:
        num_of_employees -= 1    # choosing the rest of the team for each shift

    emp_list_shift = list([])
    global emp_list_day
    if shift_num == 1:
        emp_list_day= list([])

    # choosing employees
    for emp in range(0,num_of_employees):
        if len(emp_list_shift) == num_of_employees: # checkpoint: list is completed
            break
        # starting with employees with the lowest number of scheduled shifts
        minDaysAweekPP = min(Employees["Shifts"])
        for availability in range(minDaysAweekPP,max_date.day - min_date.day + 1):
            if len(emp_list_shift) == num_of_employees: # checkpoint: list is completed
                break

            for emp in range(0,total_employees):
                if len(emp_list_shift) == num_of_employees: # checkpoint: list is completed
                    break
                # checking skill level for supervisors (skill level=2)
                if Supervision == 1 and supervisor == 0 and Employees["Skill Level"].iloc[emp] == 1:
                    continue
                # checking skill level for other team member(s)  (skill level=1)
                if Supervision == 1 and supervisor == 1 and Employees["Skill Level"].iloc[emp] == 2:
                    continue
                # the employee is available in day "day_num"
                if Employees.iloc[emp,2+day_num] == "No":
                    continue              
                # no same shift & no same day
                if (emp in emp_list_shift) or (emp in emp_list_day): 
                    continue
                # if the employee is among the least-scheduled-shifts employees
                if Employees.Shifts[emp] == availability:             
                    # no following shift
                    if (day_num!=1) and (shift_num == 1) and (emp in schedule.iloc[shift-1,2:5]):
                            continue
                    if (day_num==max_date.day - min_date.day + 1) and (shift_num == 3) and (emp in schedule.iloc[0,2:5]):
                            continue
                    
                    # confirm the employee
                    emp_list_shift.append(emp)
                    emp_list_day.append(emp)
                    
    if len(emp_list_shift) == num_of_employees:
        schedule["Date"].iloc[shift-1] = day_num
        schedule["Shift"].iloc[shift-1] = shift_num
        schedule.iloc[shift-1 , supervisor+2:supervisor+2+num_of_employees] = emp_list_shift[0:num_of_employees]
        return emp_list_shift
   
    return 0

#------------------------------------------- loop
shift = 1
status = 0
while True:
    shift = shift + status
    status = get_table(shift)
    if (status == 0) or (shift + status == 0) or (shift == total_shifts):
        break

# schecule based on names
for emp_row in range(0,total_shifts):
    schedule.iloc[emp_row,0] = (min_date + timedelta(days = int(schedule.iloc[emp_row,0] - 1))).strftime('%d/%m/%Y')
    for emp_column in range(2,5):
        if schedule.iloc[emp_row,emp_column] == -1:
            schedule.iloc[emp_row,emp_column] = "-"
        else:
            schedule.iloc[emp_row,emp_column] = Employees.iloc[schedule.iloc[emp_row,emp_column],0] + " " + Employees.iloc[schedule.iloc[emp_row,emp_column],1]

print(schedule)
schedule.to_csv('Data/Schedule.csv', index=False)


