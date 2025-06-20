import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
import joblib

# Load data
df = pd.read_csv("Food_Delivery_Times.csv")
df = df.dropna()

# Define features and target
X = df.drop(columns=["Order_ID", "Delivery_Time_min"])
y = df["Delivery_Time_min"]

# Categorical and numerical features
cat_features = ["Weather", "Traffic_Level", "Time_of_Day", "Vehicle_Type"]
num_features = ["Distance_km", "Preparation_Time_min", "Courier_Experience_yrs"]

# Preprocessing
cat_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

num_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="mean"))
])

preprocessor = ColumnTransformer([
    ("cat", cat_transformer, cat_features),
    ("num", num_transformer, num_features)
])

# Pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit model
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error: {mae:.2f} minutes")

# Save the model
joblib.dump(model, "delivery_time_model.pkl")

# Visualization: Feature Importance
model_rf = model.named_steps["regressor"]
encoded_features = model.named_steps["preprocessor"].transformers_[0][1].named_steps["encoder"].get_feature_names_out(cat_features)
all_features = np.concatenate([encoded_features, num_features])

importances = model_rf.feature_importances_
indices = np.argsort(importances)[-10:]

plt.figure(figsize=(10,6))
sns.barplot(x=importances[indices], y=all_features[indices])
plt.title("Top Feature Importances")
plt.tight_layout()
plt.savefig("feature_importance.png")
plt.show()

# Custom input prediction
sample_input = {
    "Distance_km": 16.42,
    "Weather": "Clear",
    "Traffic_Level": "Medium",
    "Time_of_Day": "Evening",
    "Vehicle_Type": "Bike",
    "Preparation_Time_min": 20,
    "Courier_Experience_yrs": 3
}

input_df = pd.DataFrame([sample_input])
predicted_time = model.predict(input_df)[0]
print(f"Predicted Delivery Time for custom input: {predicted_time:.2f} minutes")

# Pairplot of key numerical features
sns.pairplot(df[["Distance_km", "Preparation_Time_min", "Courier_Experience_yrs", "Delivery_Time_min"]])
plt.suptitle("Pairplot of Key Numerical Features", y=1.02)
plt.show()

# Correlation heatmap
plt.figure(figsize=(8,6))
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap")
plt.show()
