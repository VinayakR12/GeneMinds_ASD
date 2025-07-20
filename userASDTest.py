import pandas as pd
from flask import request, jsonify
import numpy as np
import joblib


def load_models():
    try:
        mlp = joblib.load('models/mlp.joblib')
        random_forest = joblib.load('models/random_forest.joblib')
        mlp_scaler = joblib.load('models/scaler (1).pkl')

        if hasattr(mlp_scaler, 'feature_names_in_'):
            mlp_feature_names = mlp_scaler.feature_names_in_.tolist()
        else:
            raise ValueError("Scaler doesn't have feature names.")

        return mlp, random_forest, mlp_scaler, mlp_feature_names

    except Exception as e:
        print(f"Error loading models: {str(e)}")
        raise



mlp, random_forest, mlp_scaler, mlp_feature_names = load_models()

import lime
import lime.lime_tabular


def generate_lime_explanation(input_df):
    try:
        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=np.zeros((100, len(input_df.columns))),
            feature_names=input_df.columns,
            class_names=['No Autism', 'Autism'],
            mode='classification',
            verbose=False,
            random_state=42
        )

        exp = lime_explainer.explain_instance(
            input_df.values[0],
            random_forest.predict_proba,
            num_features=15
        )
        return [{'feature': f[0], 'weight': float(f[1])} for f in exp.as_list()]

    except Exception as e:
        print(f"LIME explanation failed: {str(e)}")
        return []


import cohere
import config

co = config.ASDCOAPI

def build_prompt(data):
    score = sum([int(data.get(f'A{i}_Score', 0)) for i in range(1, 11)])
    risk_text = "High Risk" if int(data["prediction"]) == 1 else "Low Risk"

    prompt = f"""
Autism Screening Report

Basic Information:
- Name: {data['name']}
- Age: {data['age']}
- Gender: {data['gender']}
- Ethnicity: {data['ethnicity']}
- Country of Residence: {data['country_of_res']}
- Test Completed By: {data['relation']}

Medical History:
- Born with Jaundice: {'Yes' if int(data['jaundice']) else 'No'}
- Family Member with PDD: {'Yes' if int(data['family_pdd']) else 'No'}

Autism Screening Scores:
"""
    for i in range(1, 11):
        prompt += f"\n- A{i}_Score: {data.get(f'A{i}_Score')}"

    prompt += f"\n\nTotal Score: {score}/10"
    prompt += f"\nPrediction: {risk_text} (Class = {data['prediction']})"

    prompt += """
\n\n📝 Please write a professional but compassionate medical summary on Autism Spectrum Disorder including:
- user name
- Describe their health and reasons behind the prediction
- A thorough and empathetic explanation of the results
- A simple explanation for parents, avoiding technical jargon
- Suggestions for next steps, focusing on early intervention
- Emotional support, acknowledging the emotional impact for parents
    """

    return prompt


def get_medical_summary(cohere_prompt):
    response = co.generate(
        model="command-light",
        prompt=cohere_prompt,
        max_tokens=900,
        temperature=0.7
    )
    return response.generations[0].text.strip()


def prepare_features(form_data):
    features = {feature: 0 for feature in mlp_feature_names}

    # Extract features from the form data
    for i in range(1, 11):
        features[f'A{i}_Score'] = int(form_data.get(f'A{i}_Score', 0))

    features['name'] = str(form_data.get('name', ''))
    features['age'] = float(form_data.get('age', 0))
    features['gender'] = 1 if form_data.get('gender', 'f') == 'm' else 0
    features['jaundice'] = int(form_data.get('jaundice', 0))
    features['family_pdd'] = int(form_data.get('family_pdd', 0))
    features['used_app_before'] = int(form_data.get('used_app_before', 0))

    # Process categorical fields (ethnicity, country_of_res, relation)
    for field in ['ethnicity', 'country_of_res', 'relation']:
        value = form_data.get(field, '')
        feature_name = f"{field}_{value.replace(' ', '_')}"
        if feature_name in features:
            features[feature_name] = 1

    return pd.DataFrame([features], columns=mlp_feature_names)


def handle_prediction():
    try:
        # Extract form data
        data = request.form.to_dict()
        features_df = prepare_features(data)

        # Predict using MLP and Random Forest models
        mlp_scaled = mlp_scaler.transform(features_df)
        mlp_pred = mlp.predict(mlp_scaled)[0]
        rf_pred = random_forest.predict(features_df)[0]

        # Probability scores for both models
        mlp_proba = mlp.predict_proba(mlp_scaled)[0]
        rf_proba = random_forest.predict_proba(features_df)[0]

        # Combine predictions using weighted average
        final_pred = int(np.round((mlp_pred * 0.6 + rf_pred * 0.4)))
        final_proba = (mlp_proba[1] * 0.6 + rf_proba[1] * 0.4)

        # Generate LIME explanation
        lime_explanation = generate_lime_explanation(features_df)

        # Create prompt for Cohere model
        data['prediction'] = str(final_pred)
        cohere_prompt = build_prompt(data)

        # Generate medical summary using Cohere API
        medical_summary = get_medical_summary(cohere_prompt)

        return jsonify({
            'success': True,
            'final_pred': final_pred,
            'final_proba': float(final_proba),
            'mlp_pred': int(mlp_pred),
            'mlp_proba': [float(p) for p in mlp_proba],
            'rf_pred': int(rf_pred),
            'rf_proba': [float(p) for p in rf_proba],
            'lime': lime_explanation,
            'summary': medical_summary
        })

    except Exception as e:
        # return jsonify({'success': False, 'error': str(e)}), 400
        print(f"Error occurred: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400
