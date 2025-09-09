import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
import joblib

# Generate synthetic data
np.random.seed(42)
n_samples = 1000

# Features
temperature = np.random.uniform(0, 40, n_samples)
humidity = np.random.uniform(0, 100, n_samples)
transportation_time = np.random.uniform(1, 24, n_samples)
month = np.random.randint(1, 13, n_samples)
dayofweek = np.random.randint(0, 7, n_samples)
dayofyear = np.random.randint(1, 366, n_samples)
is_month_start = np.random.randint(0, 2, n_samples)
is_month_end = np.random.randint(0, 2, n_samples)

# Target: packaging type
packaging_types = ['Plastic', 'Biodegradable', 'Paper', 'Metal']
target = np.random.choice(packaging_types, n_samples)

# Create DataFrame
data = pd.DataFrame({
    'temperature': temperature,
    'humidity': humidity,
    'transportation_time': transportation_time,
    'month': month,
    'dayofweek': dayofweek,
    'dayofyear': dayofyear,
    'is_month_start': is_month_start,
    'is_month_end': is_month_end,
    'packaging_type': target
})

# Split features and target
X = data.drop('packaging_type', axis=1)
y = data['packaging_type']

# Define numerical and categorical features
numerical_features = ['temperature', 'humidity', 'transportation_time', 'dayofyear']
categorical_features = ['month', 'dayofweek', 'is_month_start', 'is_month_end']

# Create preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])

# Create pipeline
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('clf', DecisionTreeClassifier(random_state=42))
])

# Train the model
pipeline.fit(X, y)

# Save the model
joblib.dump(pipeline, 'supply_packaging_model.pkl')

print("Model retrained and saved as supply_packaging_model.pkl")
