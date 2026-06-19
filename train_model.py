import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

print("Loading Dataset...")

df = pd.read_csv("data/fake_job_postings.csv")

# Null values remove
df["title"] = df["title"].fillna("")
df["company_profile"] = df["company_profile"].fillna("")
df["description"] = df["description"].fillna("")
df["requirements"] = df["requirements"].fillna("")

# Combine important columns
df["combined_text"] = (
    df["title"] + " " +
    df["company_profile"] + " " +
    df["description"] + " " +
    df["requirements"]
)

X = df["combined_text"]
y = df["fraudulent"]

print("Vectorizing Text...")

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000
)

X_vectorized = vectorizer.fit_transform(X)

print("Splitting Dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training Random Forest Model...")

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Evaluating Model...")

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nAccuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, predictions))

print("\nSaving Model...")

joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("Model Saved Successfully!")