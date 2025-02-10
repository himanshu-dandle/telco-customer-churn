# -*- coding: utf-8 -*-
"""customer_churn_prediction.ipynb.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16606RRK6_X1dQwLQKUr52csu3CSc5Ivw

##  Import Libraries and Load Data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import os
from scipy.stats import zscore

# Load dataset
data_path = '../data/telco_customer_churn.csv'
data = pd.read_csv(data_path)
data.head()

# Drop 'customerID' as it is non-numeric and not useful for modeling
data.drop(columns=['customerID'], errors='ignore', inplace=True)

#  Data Exploration
print("Basic Information:")
print(data.info())
print("\nSummary Statistics:")
print(data.describe())

##Check for Missing Values
missing_values = data.isnull().sum()
print("Missing Values per Column:")
print(missing_values)

# Convert 'TotalCharges' to numeric, handling missing values
data['TotalCharges'] = pd.to_numeric(data['TotalCharges'], errors='coerce')
data['TotalCharges'].fillna(data['TotalCharges'].median(), inplace=True)

"""## Exploratory Data Analysis (EDA)"""

plt.figure(figsize=(12, 6))
sns.histplot(data['tenure'], kde=True, bins=30, color='blue')
plt.title('Distribution of Tenure')
plt.show()

plt.figure(figsize=(12, 6))
sns.histplot(data['MonthlyCharges'], kde=True, bins=30, color='green')
plt.title('Distribution of Monthly Charges')
plt.show()

plt.figure(figsize=(12, 6))
sns.countplot(x='Churn', data=data, palette='pastel')
plt.title('Churn Distribution')
plt.show()

"""## Univariate Analysis"""

for col in ['tenure', 'MonthlyCharges', 'TotalCharges']:
    plt.figure(figsize=(8, 4))
    sns.boxplot(x=data[col], color='orange')
    plt.title(f'Boxplot of {col}')
    plt.show()

"""## Bivariate Analysis"""

plt.figure(figsize=(12, 6))
sns.boxplot(x='Churn', y='MonthlyCharges', data=data, palette='coolwarm')
plt.title('Monthly Charges vs Churn')
plt.show()

plt.figure(figsize=(12, 6))
sns.boxplot(x='Churn', y='tenure', data=data, palette='coolwarm')
plt.title('Tenure vs Churn')
plt.show()

"""## Handle Outliers using Z-score"""

num_features = ['tenure', 'MonthlyCharges', 'TotalCharges']
data = data[(zscore(data[num_features]) < 3).all(axis=1)]

# Encode Categorical Features using Label Encoding
categorical_cols = ['gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
                    'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                    'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract', 'PaperlessBilling',
                    'PaymentMethod']

for col in categorical_cols:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])

# One-hot encode 'Churn'
data['Churn'] = data['Churn'].map({'Yes': 1, 'No': 0})

# Split the Dataset into Features and Target Variable
X = data.drop('Churn', axis=1)
y = data['Churn']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

"""## Feature Scaling"""

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train a Random Forest Classifier
model = RandomForestClassifier(random_state=42)
model.fit(X_train_scaled, y_train)

# Predictions on test set
y_pred = model.predict(X_test_scaled)

# Performance evaluation
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# ROC-AUC score
roc_auc = roc_auc_score(y_test, model.predict_proba(X_test_scaled)[:, 1])
print(f'ROC-AUC Score: {roc_auc}')

# Save output directory
output_path = '../output'
os.makedirs(output_path, exist_ok=True)

# Plot Confusion Matrix
plt.figure(figsize=(6, 4))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.savefig(os.path.join(output_path, 'confusion_matrix.png'))
plt.show()

# Save Model Feature Importance
importances = model.feature_importances_
feature_names = X.columns
feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

# Plot Feature Importance
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_importance_df.head(10))
plt.title('Top 10 Important Features in Random Forest')
plt.savefig(os.path.join(output_path, 'feature_importance.png'))
plt.show()

print("Feature Importance:")
print(feature_importance_df.head(10))

# Check for Overfitting
train_accuracy = model.score(X_train_scaled, y_train)
test_accuracy = model.score(X_test_scaled, y_test)
print(f"Training Accuracy: {train_accuracy:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")
if train_accuracy > test_accuracy:
    print("Warning: The model might be overfitting.")

# Cross-Validation to Validate Performance
from sklearn.model_selection import cross_val_score
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
print(f"Cross-Validation Accuracy Scores: {cv_scores}")
print(f"Mean Cross-Validation Accuracy: {cv_scores.mean():.4f}")

"""## Analyis :
model shows overfitting because the training accuracy (99.84%) is significantly higher than the test accuracy (80.03%). This means your model is memorizing the training data instead of generalizing well to unseen data.
"""

## Try Random forestr tuned version

# Train a Regularized Random Forest Model
model = RandomForestClassifier(
    n_estimators=100,      # Reduce the number of trees
    max_depth=10,          # Limit depth to prevent overfitting
    min_samples_split=5,   # Require at least 5 samples to split
    min_samples_leaf=2,    # Require at least 2 samples at leaf nodes
    random_state=42
)

model.fit(X_train_scaled, y_train)

# Evaluate again
y_pred = model.predict(X_test_scaled)
roc_auc = roc_auc_score(y_test, model.predict_proba(X_test_scaled)[:, 1])

print("New Model Performance:")
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
print(f'New ROC-AUC Score: {roc_auc:.4f}')

## Gradient Boosting

# Train a Gradient Boosting Model
from sklearn.ensemble import GradientBoostingClassifier

gb_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.05,  # Reduce learning rate for better generalization
    max_depth=5,
    random_state=42
)

gb_model.fit(X_train_scaled, y_train)
y_pred_gb = gb_model.predict(X_test_scaled)
roc_auc_gb = roc_auc_score(y_test, gb_model.predict_proba(X_test_scaled)[:, 1])

print("Gradient Boosting Performance:")
print(confusion_matrix(y_test, y_pred_gb))
print(classification_report(y_test, y_pred_gb))
print(f'Gradient Boosting ROC-AUC Score: {roc_auc_gb:.4f}')

"""##  Random Forest and Gradient Boosting models are now performing better with an improved ROC-AUC score (~0.855 for RF & 0.853 for GBM).

## Fine-Tune Hyperparameters for XGBoost
"""

from xgboost import XGBClassifier

xgb_model = XGBClassifier(
    n_estimators=200,      # More trees for better learning
    learning_rate=0.03,    # Lower learning rate for better generalization
    max_depth=5,           # Limit depth
    subsample=0.8,         # Prevent overfitting by training on 80% of data
    colsample_bytree=0.8,  # Use only 80% of features per tree
    random_state=42
)

xgb_model.fit(X_train_scaled, y_train)
y_pred_xgb = xgb_model.predict(X_test_scaled)
roc_auc_xgb = roc_auc_score(y_test, xgb_model.predict_proba(X_test_scaled)[:, 1])

print("XGBoost Performance:")
print(confusion_matrix(y_test, y_pred_xgb))
print(classification_report(y_test, y_pred_xgb))
print(f'XGBoost ROC-AUC Score: {roc_auc_xgb:.4f}')

"""##  Feature Selection to Remove Noise"""

# Keep only important features
important_features = ['TotalCharges', 'MonthlyCharges', 'tenure', 'Contract', 'PaymentMethod', 'OnlineSecurity']
X_selected = X[important_features]

# Split the dataset again
X_train_sel, X_test_sel, y_train_sel, y_test_sel = train_test_split(X_selected, y, test_size=0.3, random_state=42)

# Feature Scaling
X_train_sel_scaled = scaler.fit_transform(X_train_sel)
X_test_sel_scaled = scaler.transform(X_test_sel)

# Train the XGBoost model on selected features
xgb_model.fit(X_train_sel_scaled, y_train_sel)
y_pred_xgb_sel = xgb_model.predict(X_test_sel_scaled)
roc_auc_xgb_sel = roc_auc_score(y_test_sel, xgb_model.predict_proba(X_test_sel_scaled)[:, 1])

print("XGBoost with Feature Selection Performance:")
print(confusion_matrix(y_test_sel, y_pred_xgb_sel))
print(classification_report(y_test_sel, y_pred_xgb_sel))
print(f'XGBoost ROC-AUC Score (Feature Selected): {roc_auc_xgb_sel:.4f}')

# Save Confusion Matrix Plot
plt.figure(figsize=(6, 4))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix - XGBoost')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.savefig(os.path.join(output_path, 'conf_matrix_xgboost.png'))
plt.show()

# Save Model Feature Importance
importances = model.feature_importances_
feature_names = X.columns
feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

# Plot Feature Importance
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_importance_df.head(10))
plt.title('Top 10 Features Impacting Churn - XGBoost')
plt.savefig(os.path.join(output_path, 'feature_importance_xgboost.png'))
plt.show()

print("Feature Importance:")
print(feature_importance_df.head(10))

# Get probability predictions for ROC curve
y_prob = model.predict_proba(X_test_scaled)[:, 1]

# Plot and Save ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f'XGBoost (AUC = {roc_auc:.4f})', color='blue')
plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Customer Churn Prediction')
plt.legend()
plt.savefig(os.path.join(output_path, 'roc_curve_xgboost.png'))
plt.show()

"""## Final Model Selection
Your XGBoost model performed the best with an ROC-AUC of 0.8557 and accuracy of 81%, showing slight improvement over Random Forest and Gradient Boosting.
Best Model: XGBoost (Full Features)

Accuracy: 81%
ROC-AUC Score: 0.8557
Better balance between precision and recall

## Save thje model
"""

import os

# Get the absolute path of the output directory
output_path = os.path.abspath("../output/xgboost_model_v5.json")

# Save the model using the absolute path
xgb_model.save_model(output_path)

print(f"Model saved successfully at: {output_path}")



