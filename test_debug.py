import joblib

model = joblib.load('models/ticket_classifier.pkl')
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')

text = "Question about monthly invoice charge There is an unexpected payment charge on my latest invoice statement that I need explained."
vector = vectorizer.transform([text])

print("Model Classes:", model.classes_)
print("Prediction Probabilities:", model.predict_proba(vector))