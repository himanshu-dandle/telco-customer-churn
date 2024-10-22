# Telco Customer Churn Prediction

This project aims to predict customer churn using the **Telco Customer Churn** dataset from [Kaggle](https://www.kaggle.com/blastchar/telco-customer-churn). We apply several machine learning models, including **Random Forest**, **Logistic Regression**, **Decision Trees**, and **Gradient Boosting**, to analyze customer churn and provide actionable insights.

## Project Overview:
- **Goal**: To identify customers likely to churn based on factors like monthly charges, tenure, contract type, and other demographic and service-related features.
- **Dataset**: The dataset contains customer records from a hypothetical telecom company, including demographics, account details, and usage statistics.
- **Techniques Used**:
  - **Data Preprocessing**: Handling missing values, encoding categorical variables, and scaling numerical features.
  - **Exploratory Data Analysis (EDA)**: Visualizing important relationships and patterns within the data.
  - **Modeling**: Training several machine learning models and evaluating their performance.

## Project Steps:
1. **Data Preprocessing**:
   - Handled missing values (e.g., `TotalCharges`).
   - Converted categorical features into numerical values using one-hot encoding.
   - Scaled numerical features like `MonthlyCharges`, `tenure`, and `TotalCharges` for model compatibility.
   
2. **Exploratory Data Analysis (EDA)**:
   - Analyzed key features like customer demographics, services, and account information.
   - Visualized relationships between features like **MonthlyCharges** and churn probability.
   - Created visualizations for churn patterns using histograms, correlation matrices, and bar charts.

3. **Modeling**:
   - Trained several classification models, including **Random Forest**, **Logistic Regression**, **Decision Trees**, and **Gradient Boosting**.
   - Applied **cross-validation** and tuned hyperparameters using **RandomizedSearchCV** to improve model performance.

4. **Model Evaluation**:
   - Evaluated models using metrics such as **accuracy**, **precision**, **recall**, **F1-score**, and **ROC-AUC**.
   - Compared model performance and selected the best model for churn prediction.

## Results:
- **Best Model**: The **Random Forest** classifier with the following performance:
  - **Accuracy**: 77.19%
  - **ROC-AUC Score**: 0.8481, indicating strong discriminatory power between churn and non-churn customers.
  
- **Feature Importance**:
  - The most important features for predicting churn are:
    1. **MonthlyCharges**
    2. **tenure**
    3. **Contract type**

## Improvements:
- **Class Imbalance**: Applied techniques like **class weighting** and **SMOTE** to improve recall for the churn class.
- **Threshold Tuning**: Adjusted decision threshold to improve churn customer detection.
- **Hyperparameter Tuning**: Used **RandomizedSearchCV** to fine-tune model parameters for optimal performance.

## How to Run the Project:
1. Clone the repository:
   ```bash
   git clone https://github.com/himanshu-dandle/telco-customer-churn.git
