import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# 1) Load the merged file
PATH = r'C:\Users\LENOVO\Downloads\MachineLearningCSV\CIC_IDS_2017_Merged.csv'
print(" Loading dataset...")
df = pd.read_csv(PATH)
df.columns = df.columns.str.strip()

# 2) Critical Cleaning
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

# 3) Select Target Attacks
# Grouping DoS Hulk, DoS GoldenEye, and DoS Slowloris into one category
dos_types = ["DoS Hulk", "DoS GoldenEye", "DoS slowloris", "DoS Slowhttptest"]
target_attacks = ["BENIGN", "PortScan", "SSH-Patator"] + dos_types

df = df[df["Label"].isin(target_attacks)].copy()

# 4) Precise Mapping
# Class 0: Benign, 1: PortScan, 2: DoS, 3: SSH-Patator
def map_label(l):
    if l == "BENIGN": return 0
    if l == "PortScan": return 1
    if l in dos_types: return 2
    if l == "SSH-Patator": return 3
    return 0

df["Attack"] = df["Label"].apply(map_label)

# 5) Feature Selection
# IMPORTANT: These must be calculated EXACTLY the same way in your sniffer
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

# 6) Split and Scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 7) Train
# Increased n_estimators and added max_features for better generalization
print(" Training Random Forest Model...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=25,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1 # Uses all CPU cores
)
model.fit(X_train_scaled, y_train)

# 8) Save results
joblib.dump(model, "../Models/multiclass_ids_model.pkl")
joblib.dump(scaler, "../Models/multiclass_ids_scaler.pkl")
print(" Training Complete. Model and Scaler saved.")

# 9) Evaluation
y_pred = model.predict(X_test_scaled)
print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred, target_names=["BENIGN", "PortScan", "DoS", "SSH-Patator"]))