import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template
import os

app = Flask(__name__)

# Ensure the static folder exists
os.makedirs("static", exist_ok=True)

# Load and preprocess data
def load_and_preprocess_data():
    file_path = "Daily Household Transactions.csv"
    df = pd.read_csv(file_path)
    
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # Add YearMonth column
    df['YearMonth'] = df['Date'].dt.to_period('M')

    # Add Year and Month for heatmap
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    return df

# Generate visualizations
def generate_visualizations(df):
    # Monthly Spending Trends
    monthly_spending = df[df['Income/Expense'] == 'Expense'].groupby('YearMonth')['Amount'].sum()
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_spending.index.astype(str), monthly_spending.values, marker='o', linestyle='-', color='b')
    plt.title('Monthly Spending Trends', fontsize=14)
    plt.xlabel('Month', fontsize=10)
    plt.ylabel('Total Spending (INR)', fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    plt.grid(alpha=0.5)
    plt.tight_layout()
    plt.savefig('static/monthly_spending_trends.png')
    plt.close()

    # Category-Wise Breakdown
    category_spending = df[df['Income/Expense'] == 'Expense'].groupby('Category')['Amount'].sum().sort_values(ascending=False)
    plt.figure(figsize=(9, 6))
    sns.barplot(x=category_spending.values, y=category_spending.index, palette='viridis', orient='h')
    plt.title('Category-Wise Breakdown of Expenses', fontsize=14)
    plt.xlabel('Total Spending (INR)', fontsize=10)
    plt.ylabel('Category', fontsize=10)
    plt.tight_layout()
    plt.savefig('static/category_breakdown.png')
    plt.close()

    # Payment Mode Analysis
    payment_modes = df.groupby('Mode')['Amount'].sum()
    plt.figure(figsize=(9, 5))
    sns.barplot(x=payment_modes.values, y=payment_modes.index, palette='coolwarm', orient='h')
    plt.title('Payment Mode Distribution', fontsize=14)
    plt.xlabel('Total Amount (INR)', fontsize=10)
    plt.ylabel('Mode', fontsize=10)
    plt.tight_layout()
    plt.savefig('static/payment_mode_analysis.png')
    plt.close()

    # Spending Heatmap
    heatmap_data = df[df['Income/Expense'] == 'Expense'].pivot_table(
        index='Year', columns='Month', values='Amount', aggfunc='sum', fill_value=0)
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5)
    plt.title('Heatmap of Monthly Spending by Year', fontsize=14)
    plt.xlabel('Month', fontsize=10)
    plt.ylabel('Year', fontsize=10)
    plt.tight_layout()
    plt.savefig('static/spending_heatmap.png')
    plt.close()

    # Category-Wise Spending (Pie Chart)
    category_pie = df[df['Income/Expense'] == 'Expense'].groupby('Category')['Amount'].sum()
    plt.figure(figsize=(8, 8))
    colors = sns.color_palette('pastel')
    wedges, texts, autotexts = plt.pie(
        category_pie, labels=category_pie.index, autopct='%1.1f%%',
        startangle=140, colors=colors, pctdistance=0.85, wedgeprops={'edgecolor': 'black'})
    
    for text in texts:
        text.set_fontsize(9)
        text.set_fontweight('bold')
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
        autotext.set_color('black')
    
    plt.gca().add_artist(plt.Circle((0,0),0.70,fc='white'))  # Create a donut effect
    plt.title('Category-Wise Spending Distribution', fontsize=14)
    plt.tight_layout()
    plt.savefig('static/category_pie_chart.png')
    plt.close()

# Route to render the dashboard
@app.route('/')
def index():
    # Load and preprocess data
    df = load_and_preprocess_data()

    # Generate visualizations
    generate_visualizations(df)

    # Pass the paths to the visualizations
    visualizations = {
        'monthly_trends': '/static/monthly_spending_trends.png',
        'category_breakdown': '/static/category_breakdown.png',
        'payment_modes': '/static/payment_mode_analysis.png',
        'spending_heatmap': '/static/spending_heatmap.png',
        'category_pie': '/static/category_pie_chart.png'
    }

    return render_template('index.html', visualizations=visualizations)

if __name__ == '__main__':
    app.run(debug=True)
