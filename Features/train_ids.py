import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

PATH = r'C:\Users\LENOVO\Downloads\MachineLearningCSV\CIC_IDS_2017_Merged.csv'

print("Loading dataset...")
df = pd.read_csv(PATH)
df.columns = df.columns.str.strip()

# Cleaning
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

# Target selection
dos_types = ["DoS Hulk", "DoS GoldenEye", "DoS slowloris", "DoS Slowhttptest"]
target_attacks = ["BENIGN", "PortScan", "SSH-Patator"] + dos_types

df = df[df["Label"].isin(target_attacks)].copy()

# Label mapping
def map_label(l):
    if l == "BENIGN": return 0
    if l == "PortScan": return 1
    if l in dos_types: return 2
    if l == "SSH-Patator": return 3
    return 0

df["Attack"] = df["Label"].apply(map_label)

# Features
feature_cols = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Average Packet Size",
    "SYN Flag Count",
    "ACK Flag Count",
    "RST Flag Count",
    "Flow Bytes/s",
    "Flow Packets/s"
]

X = df[feature_cols]
y = df["Attack"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model
print("Training model...")
model = RandomForestClassifier(
    n_estimators=120,
    max_depth=25,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_scaled, y_train)

# Save
joblib.dump(model, "multiclass_ids_model.pkl")
joblib.dump(scaler, "multiclass_ids_scaler.pkl")

print("Training complete.")

# Evaluation
y_pred = model.predict(X_test_scaled)
print(classification_report(y_test, y_pred, target_names=["BENIGN", "PortScan", "DoS", "SSH"]))