from PIL import Image
import os
import whois
from datetime import datetime
from flask import Flask, request, jsonify
import joblib
import requests
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)


gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# Load trained model
model = joblib.load("recruitment_model.pkl")
vectorizer = joblib.load("recruitment_vectorizer.pkl")

# Fake company blacklist

blacklisted_companies = [

    "Fake HR",

    "Instant Jobs",

    "Quick Placement",

    "Dream Job Consultancy",

    "Job Connect Pro"

]
def check_blacklist(company_name):

    risk = 0

    reasons = []

    if not company_name:

        return risk, reasons

    for company in blacklisted_companies:

        if company_name.lower() == company.lower():

            risk += 50

            reasons.append(
                "Company found in blacklist database"
            )

    return risk, reasons
def company_email_match(company_name, email):

    risk = 0
    reasons = []

    if company_name and email:

        company = company_name.lower().replace(" ", "")

        domain = email.split("@")[-1].lower()

        if company not in domain:
            risk += 20
            reasons.append(
                "Company name does not match email domain"
            )

    return risk, reasons

def extract_text_from_image(image_path):

    try:

        image = Image.open(image_path)

        response = gemini_model.generate_content([
            "Extract all text from this image",
            image
        ])

        return response.text

    except Exception as e:

        return str(e)
def check_website_status(url):

    if not url:
        return 0, []

    risk = 0
    reasons = []

    try:
        response = requests.get(
            f"https://{url}",
            timeout=5
        )

        if response.status_code != 200:
            risk += 20
            reasons.append(
                "Website not responding properly"
            )

    except:
        risk += 30
        reasons.append(
            "Website unreachable"
        )

    return risk, reasons
def verify_email_domain(email):

    risk = 0
    reasons = []

    if not email:
        return risk, reasons

    email = email.lower()

    free_domains = [
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "hotmail.com"
    ]

    domain = email.split("@")[-1]

    if domain in free_domains:
        risk += 30
        reasons.append(
            "Recruitment email uses free email provider"
        )

    return risk, reasons
def check_domain_age(website):

    risk = 0
    reasons = []

    try:
        domain_info = whois.whois(website)

        creation_date = domain_info.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if creation_date:

            age_days = (
                datetime.now() - creation_date
            ).days

            if age_days < 180:
                risk += 40
                reasons.append(
                    "Website registered less than 6 months ago"
                )

            elif age_days < 365:
                risk += 20
                reasons.append(
                    "Website registered less than 1 year ago"
                )

    except Exception:
        risk += 10
        reasons.append(
            "Unable to verify website age"
        )

    return risk, reasons
def verify_company(company_name, website):
    risk = 0
    reasons = []

    suspicious_domains = [".xyz", ".top", ".click", ".shop"]

    if website:
        for domain in suspicious_domains:
            if website.lower().endswith(domain):
                risk += 30
                reasons.append("Suspicious website domain")

    free_domains = ["gmail.com", "yahoo.com", "outlook.com"]

    if website:
        for domain in free_domains:
            if domain in website.lower():
                risk += 20
                reasons.append("Free email domain detected")

    if company_name and len(company_name.strip()) < 3:
        risk += 10
        reasons.append("Invalid company name")

    return risk, reasons


@app.route("/")
def home():
    return {
        "message": "ScamTrace AI API Running"
    }


@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    description = data.get("description", "")
    company_name = data.get("company_name", "")
    website = data.get("website", "")
    email = data.get("email", "")

    if not description:
        return jsonify({
            "error": "Description is required"
        }), 400

    # ML Analysis
    text_vector = vectorizer.transform([description])

    prediction = model.predict(text_vector)[0]

    probability = model.predict_proba(text_vector)[0]

    scam_probability = round(probability[1] * 100, 2)

    risk_score = int(scam_probability)
    scam_keywords = [
    "registration fee",
    "processing fee",
    "guaranteed job",
    "guaranteed placement",
    "instant joining",
    "telegram",
    "whatsapp",
    "pay now"
    ]
    keyword_risk = 0
    keyword_reasons = []

    for word in scam_keywords:

        if word.lower() in description.lower():

            keyword_risk += 15

            keyword_reasons.append(
                f"Suspicious keyword detected: {word}"
        )
# Company Verification

    company_risk, reasons = verify_company(
        company_name,
        website
    )
    blacklist_risk, blacklist_reasons = check_blacklist(
        company_name
    )

    company_risk += blacklist_risk

    reasons.extend(blacklist_reasons)
    # Default values
    website_risk = 0
    website_reasons = []

    domain_risk = 0
    domain_reasons = []

    if website:
        domain_risk, domain_reasons = check_domain_age(
            website
        )

        website_risk, website_reasons = check_website_status(
            website
         )

    company_risk += website_risk
    reasons.extend(website_reasons)

    company_risk += domain_risk
    reasons.extend(domain_reasons)

    company_risk += keyword_risk
    reasons.extend(keyword_reasons)
    
    email_risk, email_reasons = verify_email_domain(
    email
)
    match_risk, match_reasons = company_email_match(
    company_name,
    email
)

    company_risk += match_risk
    reasons.extend(match_reasons)

    company_risk += email_risk
    reasons.extend(email_reasons)
    
    xai_reasons = reasons[:5]

    final_risk = min(
        100,
        risk_score + company_risk
    )
    trust_score = max(0, 100 - final_risk)


    # Final Risk Level
    if final_risk >= 80:
        risk_level = "Critical"
    elif final_risk >= 60:
        risk_level = "High"
    elif final_risk >= 40:
        risk_level = "Medium"
    elif final_risk >= 20:
        risk_level = "Low"
    else:
        risk_level = "Safe"

    recommendation = ""

    if final_risk >= 80:

        recommendation = (
            "Do not pay money. Report immediately."
        )

    elif final_risk >= 50:

        recommendation = (
            "Verify company before proceeding."
        )

    else:

        recommendation = (
            "Appears safe. Continue cautiously."
        )

    if trust_score >= 80:
        trust_status = "Trusted Company"

    elif trust_score >= 50:
        trust_status = "Needs Verification"
    else:
        trust_status = "High Risk Company"

    summary = (
        "Potential recruitment scam detected"
        if prediction == 1
        else "Job posting appears legitimate"
    )

    return jsonify({

    "prediction": int(prediction),
    "summary": summary,
    "ml_risk": risk_score,
    "company_risk": company_risk,
    "final_risk": final_risk,
    "scam_probability": scam_probability,
    "risk_level": risk_level,
    "company_name": company_name,
    "website": website,
    "xai_reasons": xai_reasons,
    "reasons": reasons,
    "recommendation": recommendation,
    "trust_score": trust_score,
    "trust_status": trust_status,

})
@app.route("/ocr-analyze", methods=["POST"])
def ocr_analyze():

    if "file" not in request.files:

        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["file"]

    company_name = request.form.get(
        "company_name",
        ""
    )

    website = request.form.get(
        "website",
        ""
    )

    email = request.form.get(
        "email",
        ""
    )

    filepath = os.path.join(
        "uploads",
        file.filename
    )

    file.save(filepath)

    extracted_text = extract_text_from_image(
        filepath
    )

    text_vector = vectorizer.transform(
        [extracted_text]
    )

    prediction = model.predict(
        text_vector
    )[0]

    probability = model.predict_proba(
        text_vector
    )[0]

    scam_probability = round(
        probability[1] * 100,
        2
    )

    risk_score = int(
        scam_probability
    )

    company_risk = 0
    reasons = []

    # Keyword Detection

    scam_keywords = [
        "registration fee",
        "processing fee",
        "guaranteed job",
        "guaranteed placement",
        "instant joining",
        "telegram",
        "whatsapp",
        "pay now"
    ]

    keyword_risk = 0
    keyword_reasons = []

    for word in scam_keywords:

        if word.lower() in extracted_text.lower():

            keyword_risk += 15

            keyword_reasons.append(
                f"Suspicious keyword detected: {word}"
            )

    company_risk += keyword_risk

    reasons.extend(
        keyword_reasons
    )

    # Company Verification

    verify_risk, verify_reasons = verify_company(
        company_name,
        website
    )

    company_risk += verify_risk

    reasons.extend(
        verify_reasons
    )

    # Blacklist Check

    blacklist_risk, blacklist_reasons = check_blacklist(
        company_name
    )

    company_risk += blacklist_risk

    reasons.extend(
        blacklist_reasons
    )

    # Website Checks

    if website:

        website_risk, website_reasons = check_website_status(
            website
        )

        domain_risk, domain_reasons = check_domain_age(
            website
        )

        company_risk += website_risk
        company_risk += domain_risk

        reasons.extend(
            website_reasons
        )

        reasons.extend(
            domain_reasons
        )

    # Email Checks

    email_risk, email_reasons = verify_email_domain(
        email
    )

    match_risk, match_reasons = company_email_match(
        company_name,
        email
    )

    company_risk += email_risk
    company_risk += match_risk

    reasons.extend(
        email_reasons
    )

    reasons.extend(
        match_reasons
    )

    # Final Risk

    final_risk = min(
        100,
        risk_score + company_risk
    )

    trust_score = max(
        0,
        100 - final_risk
    )

    xai_reasons = reasons[:5]

    # Risk Level

    if final_risk >= 80:
        risk_level = "Critical"

    elif final_risk >= 60:
        risk_level = "High"

    elif final_risk >= 40:
        risk_level = "Medium"

    elif final_risk >= 20:
        risk_level = "Low"

    else:
        risk_level = "Safe"

    # Recommendation

    if final_risk >= 80:

        recommendation = (
            "Do not pay money. Report immediately."
        )

    elif final_risk >= 50:

        recommendation = (
            "Verify company before proceeding."
        )

    else:

        recommendation = (
            "Appears safe. Continue cautiously."
        )

    # Trust Status

    if trust_score >= 80:

        trust_status = "Trusted Company"

    elif trust_score >= 50:

        trust_status = "Needs Verification"

    else:

        trust_status = "High Risk Company"

    summary = (
        "Potential recruitment scam detected"
        if prediction == 1
        else "Job posting appears legitimate"
    )

    return jsonify({

        "extracted_text": extracted_text,
        "prediction": int(prediction),
        "summary": summary,
        "ml_risk": risk_score,
        "company_risk": company_risk,
        "final_risk": final_risk,
        "scam_probability": scam_probability,
        "risk_level": risk_level,
        "website": website,
        "xai_reasons": xai_reasons,
        "reasons": reasons,
        "recommendation": recommendation,
        "trust_score": trust_score,
        "trust_status": trust_status

    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
