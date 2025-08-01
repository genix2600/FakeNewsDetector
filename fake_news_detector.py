import joblib
import pandas as pd
import re
import string
import streamlit as st
import sys
import os

def load_model(path):
    if not os.path.exists(path):
        st.error(f"Missing file: {path}")
        st.stop()
    return joblib.load(path)

vectorizer = load_model("vectorizer.pkl")
LR = load_model("logistic_model.pkl")
DT = load_model("decision_tree_model.pkl")
GBC = load_model("gradient_boosting_model.pkl")
RF = load_model("random_forest_model.pkl")

def wordopt(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def output_label(n):
    return "Probably not fake news" if n == 1 else "Probably fake news"

def get_explanation(prediction):
    return (
        "This headline seems factual and resembles real news patterns."
        if prediction == 1 else
        "This headline shows signs commonly seen in fake news — possibly emotional or misleading phrasing."
    )

def model_details():
    st.sidebar.markdown("### Model Descriptions")
    model_choice = st.sidebar.selectbox("Choose a model to learn more:", ["All", "Logistic Regression", "Decision Tree", "Gradient Boosting", "Random Forest"])
    
    descriptions = {
        "Logistic Regression": "Simple model using word frequency patterns.",
        "Decision Tree": "Rule-based system analyzing text features.",
        "Gradient Boosting": "Builds multiple trees, learns from mistakes.",
        "Random Forest": "Collection of decision trees voting together."
    }

    if model_choice == "All":
        for name, desc in descriptions.items():
            st.sidebar.markdown(f"**{name}:** {desc}")
    else:
        st.sidebar.markdown(f"**{model_choice}:** {descriptions[model_choice]}")

def run_streamlit_app():
    st.title("📰 Fake News Headline Classifier")
    model_details()

    headline = st.text_input("Enter a news headline:")

    if headline:
        processed = wordopt(headline)
        new_xv = vectorizer.transform([processed])

        models = {
            "Logistic Regression": LR,
            "Decision Tree": DT,
            "Gradient Boosting": GBC,
            "Random Forest": RF
        }

        st.subheader("🔍 Model Predictions")
        predictions = []
        confidences = []

        for name, model in models.items():
            prediction = model.predict(new_xv)[0]
            proba = model.predict_proba(new_xv)[0]
            label = output_label(prediction)
            confidence = round(max(proba) * 100, 2)
            predictions.append(prediction)
            confidences.append((prediction, confidence))

            color = "green" if prediction == 1 else "red"
            st.markdown(f"**{name}:** :{color}[{label}]")
            st.markdown(f"Confidence: `{confidence}%`")
            st.markdown(f"Explanation: {get_explanation(prediction)}")
            st.markdown("---")

        final_vote = max(set(predictions), key=predictions.count)
        final_label = output_label(final_vote)
        real_count = predictions.count(1)
        fake_count = predictions.count(0)
        matching_conf = [conf for pred, conf in confidences if pred == final_vote]
        confidence_percent = round(sum(matching_conf) / len(matching_conf), 2)

        st.subheader("🧾 Final Verdict")
        st.success(f"Prediction: {final_label}")
        st.info(f"Models voted — Real: {real_count}, Fake: {fake_count}")
        st.info(f"Overall Confidence: {confidence_percent}%")

def manual_testing(news):
    processed = wordopt(news)
    new_xv = vectorizer.transform([processed])

    models = {
        "Logistic Regression": LR,
        "Decision Tree": DT,
        "Gradient Boosting": GBC,
        "Random Forest": RF
    }

    predictions = []
    confidences = []

    for name, model in models.items():
        prediction = model.predict(new_xv)[0]
        proba = model.predict_proba(new_xv)[0]
        label = output_label(prediction)
        confidence = round(max(proba) * 100, 2)
        explanation = get_explanation(prediction)

        predictions.append(prediction)
        confidences.append((prediction, confidence))

        print(f"\n{name}")
        print(f"Prediction:  {label}")
        print(f"Confidence:  {confidence}%")
        print(f"Explanation: {explanation}")

    final_vote = max(set(predictions), key=predictions.count)
    final_label = output_label(final_vote)
    real_count = predictions.count(1)
    fake_count = predictions.count(0)
    matching_confidences = [conf for pred, conf in confidences if pred == final_vote]
    confidence_percent = round(sum(matching_confidences) / len(matching_confidences), 2)

    print("\nFinal Verdict")
    print(f"Prediction: {final_label}")
    print(f"Based on {real_count} real and {fake_count} fake votes out of {len(predictions)} models.")
    print(f"Overall Confidence (weighted): {confidence_percent}%")

def model_info():
    print("\nAvailable Models and Their Roles:")
    print("- Logistic Regression (LR): Predicts using word frequency patterns.")
    print("- Decision Tree (DT): Rule-based breakdown of features.")
    print("- Gradient Boosting (GBC): Learns from previous mistakes across multiple trees.")
    print("- Random Forest (RF): Uses multiple trees to vote on the result.\n")
    
    model_choice = input("Type the model name (LR, DT, GBC, RF) or 'back': ").strip().upper()
    
    if model_choice == "LR":
        print("\nLogistic Regression (LR):")
        print(" - This model checks which words commonly appear in real or fake headlines.")
        print(" - It assigns weights to these words and calculates a probability score.")
        print(" - For example, clickbait words like 'shocking' or 'you won't believe' might lower the realness score.")
        print(" - Fast and works well when there's a clear difference in word usage.")
    elif model_choice == "DT":
        print("\nDecision Tree (DT):")
        print(" - Breaks headlines into conditions like 'Does this word appear?' or 'Is this phrase used?'.")
        print(" - Follows these rules step-by-step like a flowchart to make a decision.")
        print(" - Easy to understand and explain, but can sometimes overfit on small patterns.")
    elif model_choice == "GBC":
        print("\nGradient Boosting Classifier (GBC):")
        print(" - This model builds a series of decision trees.")
        print(" - Each new tree corrects the mistakes made by the previous one.")
        print(" - It's excellent at picking up complex combinations of words or patterns that single trees might miss.")
        print(" - Takes longer to train but usually gives better accuracy.")
    elif model_choice == "RF":
        print("\nRandom Forest (RF):")
        print(" - Builds many decision trees on different parts of the data.")
        print(" - Each tree votes on whether the headline is real or fake.")
        print(" - The majority vote becomes the final prediction.")
        print(" - This makes it very stable and less prone to errors from individual trees.")
    elif model_choice == "BACK":
        return
    else:
        print("Invalid input. Type one of: LR, DT, GBC, RF or 'back' to return.")

if __name__ == "__main__":
    if hasattr(st, "_is_running_with_streamlit") and st._is_running_with_streamlit:
        run_streamlit_app()
    else:
        while True:
            news = input("\nEnter headline (or type 'help' for model info, 'exit' to quit): ").strip()
            if news.lower() == "exit":
                print("Exiting.")
                break
            elif news.lower() == "help":
                model_info()
            else:
                manual_testing(news)