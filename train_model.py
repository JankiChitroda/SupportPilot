import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

# 1. Load your cleaned dataset
df = pd.read_csv('cleaned_customer_support_tickets_500.csv', encoding='latin-1')

# 2. Assign clean categories based on keywords matching your project slides (Network, VPN, Password, Software, Hardware)
def assign_category(text):
    text = str(text).lower()
    if 'vpn' in text:
        return 'VPN'
    elif 'password' in text or 'login' in text or 'reset' in text:
        return 'Password'
    elif 'wifi' in text or 'network' in text or 'internet' in text or 'slow' in text:
        return 'Network'
    elif 'install' in text or 'software' in text or 'app' in text:
        return 'Software'
    else:
        return 'Hardware'

df['Clean_Category'] = df['Ticket Description'].apply(assign_category)

X = df['Ticket Description']
y = df['Clean_Category']

# 3. Split data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Vectorize text using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vector = vectorizer.fit_transform(X_train)
X_test_vector = vectorizer.transform(X_test)

# 5. Train the Logistic Regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vector, y_train)

# 6. Evaluate accuracy
accuracy = model.score(X_test_vector, y_test)
print(f"Classification Accuracy: {accuracy * 100:.2f}%")

# 7. Save the model and vectorizer
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/ticket_classifier.pkl')
joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')

print("Model trained and saved successfully in models/ folder!")