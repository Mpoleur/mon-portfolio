import streamlit as st
import random

#############################
#   Functions
#############################

def roll(num_roll,selected_dice):
    for i in range(num_roll):
        random_int = random.randint(1, selected_dice)
        roll_result=[selected_dice,random_int]
        roll_results.append(roll_result)
    return roll_results

def rolls(request):
    for i in range(len(request)):
        for q in range(request[i][0]):
            random_int = random.randint(1,request[i][1])
            roll_result=[request[i][1],random_int]
            roll_results.append(roll_result)
    return roll_results

#############################
#   Page set up
#############################

st.set_page_config(
    page_title="Roll dés dices",
    page_icon="🎲",
)

#############################
#   Body
#############################

st.title("🎲 Fais tourner les dés")

st.header("Sélection des dés")

#############################
#   Logs
#############################

#############################
#   Quick roll
#############################
roll_results=[]
with st.expander(label="Quick roll",expanded=True):
    with st.container(horizontal=True):
        col1,col2 = st.columns(2)
        with col1:
            with st.container():
                st.button("D100", key="solo_d100",on_click=rolls, args=([[1,100],]))
                st.button("D20", key="solo_d20",on_click=roll, args=(3,20))
                st.button("D12", key="solo_d12",on_click=roll, args=(1,12))
        with col2:
            with st.container():
                st.subheader("Log results")    
                st.markdown(roll_results)



#############################
#   Dice selection form
#############################

with st.form(key="dice_Selection",
        clear_on_submit=False,
        enter_to_submit=False,
        ):
    D100 = [st.number_input(label="D100", min_value=0,step=1),100]
    D20 = [st.number_input(label="D20", min_value=0,step=1),20]
    D12 = [st.number_input(label="D12", min_value=0,step=1),12]
    D8 = [st.number_input(label="D8", min_value=0,step=1),8]
    D6 = [st.number_input(label="D6", min_value=0,step=1),6]
    D4 = [st.number_input(label="D4", min_value=0,step=1),4]
    request = [D100,D20,D12,D8,D6,D4]

    submit=st.form_submit_button(label="Roll", key="roll_button")

    if submit:
        st.write(rolls(request))

            