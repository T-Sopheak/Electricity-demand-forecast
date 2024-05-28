import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("Welcome to Energy Demand Forecast Web Application!")
st.header("Energy Demand Forecast")
st.subheader("This application predicts the future energy demand based on historical data you provided.")
st.write('Please upload file in excel format as in example below:')

# load data from Excel file into a DataFrame
sample = pd.read_excel('energy_sample.xlsx')
styler = sample.style.hide_index()
st.write(styler.to_html(), unsafe_allow_html=True)

# Create a file uploader widget
file = st.file_uploader("Upload your file here", type=["xlsx"])

if file:
    # create target values
    data = pd.read_excel(file)
    data_array = pd.concat([data[i] for i in data.columns]).to_numpy().reshape(-1,)

    optimal_alpha = None
    optimal_gamma = None
    best_mse = None
    db = data_array.reshape(-1, 1)
    mean_results_for_all_possible_alpha_gamma_values = np.zeros((9, 9))
    for gamma in range(0, 9):
        for alpha in range(0, 9):
            pt = db[0][0]
            bt = db[1][0] - db[0][0]
            mean_for_alpha_gamma = np.zeros(len(db))
            mean_for_alpha_gamma[0] = np.power(db[0][0] - pt, 2)
            for i in range(1, len(db)):
                temp_pt = ((alpha + 1) * 0.1) * db[i][0] + (1 - ((alpha + 1) * 0.1)) * (pt + bt)
                bt = ((gamma + 1) * 0.1) * (temp_pt - pt) + (1 - ((gamma + 1) * 0.1)) * bt
                pt = temp_pt
                mean_for_alpha_gamma[i] = np.power(db[i][0] - pt, 2)
            mean_results_for_all_possible_alpha_gamma_values[gamma][alpha] = np.mean(mean_for_alpha_gamma)
    
    optimal_gamma, optimal_alpha = np.unravel_index(
        np.argmin(mean_results_for_all_possible_alpha_gamma_values),
        np.shape(mean_results_for_all_possible_alpha_gamma_values))
    optimal_alpha = (optimal_alpha + 1) * 0.1
    optimal_gamma = (optimal_gamma + 1) * 0.1
    best_mse = np.min(mean_results_for_all_possible_alpha_gamma_values)

    
    forecast = np.zeros(len(db) + 12)
    pt = db[0][0]
    bt = db[1][0] - db[0][0]
    forecast[0] = pt
    for i in range(1, len(db)):
        temp_pt = optimal_alpha * db[i][0] + (1 - optimal_alpha) * (pt + bt)
        bt = optimal_gamma * (temp_pt - pt) + (1 - optimal_gamma) * bt
        pt = temp_pt
        forecast[i] = pt
    for i in range(1,13):
        forecast[-i] = pt + ((13-i) * bt)
    
    pred_dic = {i: [forecast[i-13]] for i in range(1, 13)}
    index = ['Energy demand']
    index = pd.Index(index)
    pred_df = pd.DataFrame(pred_dic).set_index(index)
    st.write(f'The 12 month predictions are listed below:')
    st.write(pred_df.style.to_html(), unsafe_allow_html=True)
    
    # Create a line chart using Matplotlib
    fig, ax = plt.subplots()
    ax.plot(db[:, 0],label = 'real data')
    ax.plot(forecast, label = 'forecast')
    plt.legend()
    ax.set_xlabel('Month')
    ax.set_ylabel('Energer Demand')
    # Display the plot in Streamlit
    st.pyplot(fig)


    st.write(f"Best MSE = {best_mse:0.4f}")
    st.write("Optimal alpha = %s" % optimal_alpha)
    st.write("Optimal gamma = %s" % optimal_gamma)
    
    



