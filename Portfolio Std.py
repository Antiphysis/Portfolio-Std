#Program to dynamically calculate projected portfolio return and 1 Standard Deviation of returns
#up and down. Accepts stock and weight inputs and retrieves data from Yahoo Finance 

import matplotlib.pyplot as plt
import tkinter as Tk
import pandas as pd
import numpy as np
import yfinance as yf
import datetime

#start and end dates for yfinance stock data pull
start = datetime.datetime(2021, 1, 1)
end = datetime.datetime(2021, 12, 31)

count = 0
ticker_list = []
mu_list = []
sig_list = []
data_list = []
weight_list = []
coef_list = []
stock_list1 = []
stock_list2 = []
price_list = []
port_mu_graph = 0
port_std_graph = 0


def stats_calc(data, weight, ticker_list):
    global count
    weight_list_prc = []
    mu_list.append(find_mu(data.iloc[:,-3]))    
    sig_list.append(find_sig(data.iloc[:,-3]))
    data_list.append(data.iloc[:,-3])
    weight_list.append(weight)
    weight_list_prc = weight_to_prc(weight_list)

#calculates correlation matrix and creates array of correlations of combinations of stock returns
    y=np.array([np.array(xi) for xi in data_list])
    corr_matrix = np.corrcoef(y)
     
    if count == 0:
        coef_list.append(corr_matrix)
        stock_list1.append(ticker_list[count])
        stock_list2.append(ticker_list[count])
    else:
        if count == 1:
            coef_list.pop()
            stock_list1.pop()
            stock_list2.pop()            
        for i in range(0, count+1):
             for j in range(0 , count+1):
                if (i < j):
                    coef_list.append(corr_matrix[i,j])
                    stock_list1.append(ticker_list[i])
                    stock_list2.append(ticker_list[j])

    count += 1    

    port_mu_graph = port_mu(mu_list, weight_list_prc)
    port_std_graph = port_std(mu_list, sig_list, weight_list_prc, coef_list, stock_list1, stock_list2, ticker_list)
    project_port_mu_std(port_mu_graph, port_std_graph, weight_list)

#converts annual stds to 5 yr basis, projects portfolio returns and high/low stdv estimates
def project_port_mu_std(port_mu_graph, port_std_graph, weight_list):
    mu_list_temp = []
    mu_list = []
    mu_list_dollars = []
    p_std_annual_to_year = []
    p_std_up = []
    p_std_down = []
    year = [1, 2, 3, 4, 5]
    dollars = 0
    
    for i in range(0, len(weight_list)):
        dollars = dollars + float(weight_list[i])

    for i in range(0, len(year)):
        curr_year = year[i]
        p_std_annual_to_year.append(port_std_graph * curr_year**.5)
                  
    for i in range(0, 5):
        if i == 0:
            mu_list_temp.append(port_mu_graph + 1) 
        else:
            mu_list_temp.append((port_mu_graph + 1) * mu_list_temp[i - 1])

    for i in range(0, len(mu_list_temp)):
        mu_list.append(mu_list_temp[i] * dollars)
    
    for i in range(0, len(mu_list)):
        p_std_down.append(mu_list[i] - mu_list[i] * p_std_annual_to_year[i])
        p_std_up.append(mu_list[i] + mu_list[i] * p_std_annual_to_year[i])
   
    plt.clf()
    plt.plot(year, mu_list, label = "Estimated Return")
    plt.plot(year, p_std_up, label = "1 Std Up", linestyle = "--")
    plt.plot(year, p_std_down, label = "1 Std Down", linestyle = "--") 
    plt.title("Projected Portfolio Return")
    plt.xlabel("Year")
    plt.ylabel("Dollars")
    plt.legend()
    plt.show()

#calculates weighted average stock return for portfolio 
def port_mu(mu_list, weight_list_prc):
    port_mu = 0    
    for i in range(0, len(mu_list)):
        port_mu = port_mu + (mu_list[i] * weight_list_prc[i])
    return port_mu

#calculates daily returns for individual stock an converts to annual return based on avg annual trading days       
def find_mu(data):
    price_list = data.values.tolist()
    temp_mu_list = []
    trading_days = 253

    for i in range(0, len(price_list) - 1):
        temp_mu_list.append((price_list[i+1] - price_list[i])/price_list[i])
        
    stock_mu_temp = sum(temp_mu_list) / len(temp_mu_list)
    stock_mu = ((stock_mu_temp+1)**trading_days - 1)

    return stock_mu

#finds standard deviation of individual stock daily returns 
def find_sig(data):
    stock_mu = find_mu(data)
    price_list = data.values.tolist()
    var_list = []
    temp_mu_list = []
    varience = 0
    stock_std = 0
 
    for i in range(0, len(price_list) - 1):
        temp_mu_list.append((price_list[i+1] - price_list[i])/price_list[i])
        
    for i in range(0, len(temp_mu_list)):
        var_list.append((temp_mu_list[i] - stock_mu)**2)
            
    varience = sum(var_list) / (len(var_list) - 1)
    stock_std = varience**.5
    return stock_std

#calculates portfolio standard deviation based on weights, returns, stock stds and correlations
def port_std(mu_list, sig_list, weight_list_prc, coef_list, stock_list1, stock_list2, ticker_list):
    weight_x_sig_list = []
    term_list = []    
    curr_stock1 = ""
    curr_stock2 = ""
    term_calc = 0
    port_sig = 0

    for i in range(0, len(weight_list)):
        weight_x_sig_list.append(float(weight_list_prc[i])*sig_list[i])        

    for i in range(0, len(ticker_list)):
        for j in range(0, len(ticker_list)):
            if i > j:
                curr_stock1 = ticker_list[i]
                curr_stock2 = ticker_list[j]
                curr_corr = corr_lkup(curr_stock1, curr_stock2, coef_list, stock_list1, stock_list2) 
                term_list.append(2*(weight_x_sig_list[i] * weight_x_sig_list[j] * curr_corr))
                  
    for i in range(0, len(weight_x_sig_list)):
        term_calc = term_calc + (weight_x_sig_list[i]**2)
      
    for i in range(0, len(term_list)):
        term_calc = term_calc + term_list[i]

    port_sig = (term_calc)**.5

    return port_sig
    
#returns correlation of stock returns between curr_stock1 and curr_stock2 lookups   
def corr_lkup(curr_stock1, curr_stock2, coef_list, stock_list1, stock_list2):
        for i in range(0, len(stock_list1)):
            if (curr_stock1 == stock_list1[i] and curr_stock2 == stock_list2[i])  or (curr_stock2 == stock_list1[i] and curr_stock1 == stock_list2[i]):    
                return coef_list[i]  

#converts dollar weights to percents for portfolfio calculation 
def weight_to_prc(weight_list):
    dollar_sum = 0
    weight_list_prc = []
    for i in range(0, len(weight_list)):
        dollar_sum = dollar_sum + float(weight_list[i])
    for i in range(0, len(weight_list)):
        weight_list_prc.append(float(weight_list[i]) / dollar_sum)
    return weight_list_prc

#collects ticker and stock weight data, passes to stats_calc function to begin calcs
def submit():   
    ticker=ticker_var.get()
    weight=weight_var.get()
    ticker_list.append(ticker)   
    ticker_var.set("")
    weight_var.set("100")
    data = yf.download(ticker_list[count], start=start, end=end)  
    stats_calc(data, weight, ticker_list)

#creates TK window to input stock tickers and weights
root = Tk.Tk()
root.title("Portfolio Standard Deviation Calculator")
root.geometry("600x100")
ticker_var=Tk.StringVar()
weight_var=Tk.StringVar()

ticker_label = Tk.Label(root, text = 'Ticker', font=('calibre', 10, 'bold'))
ticker_entry = Tk.Entry(root, textvariable = ticker_var, font=('calibre', 10, 'normal'))
weight_label = Tk.Label(root, text = 'Weight ($)', font=('calibre', 10, 'bold'))
weight_entry = Tk.Entry(root, textvariable = weight_var, font=('calibre', 10, 'normal'))

sub_btn=Tk.Button(root, text = 'Submit', command = submit)

ticker_label.grid(row=0, column=0)
ticker_entry.grid(row=0, column=1)
weight_label.grid(row=1, column=0)
weight_entry.grid(row=1, column=1)
weight_entry.insert(-1, '100')
sub_btn.grid(row=2, column=1)

root.mainloop()



