import pandas as pd
import random

legit_jobs = [
    "Interview scheduled next week",
    "Complete coding assessment round",
    "Technical round cleared successfully",
    "Official offer letter attached",
    "Company onboarding starts Monday",
    "Recruitment process includes aptitude test",
    "Interview invitation from company HR",
    "Selection process includes multiple rounds",
    "Please complete online assessment",
    "Attend technical interview at Infosys Hyderabad",
    "Submit documents after offer letter verification",
    "Congratulations, you cleared the technical interview",
    "Campus recruitment drive announced",
    "HR discussion scheduled tomorrow",
    "Please attend virtual interview meeting"
]

scam_jobs = [
    "Pay ₹5000 registration fee and get guaranteed internship",
    "Guaranteed job after registration payment",
    "No interview required. Pay fee and join immediately",
    "Send Aadhaar card and processing fee for job confirmation",
    "WhatsApp us for instant joining",
    "Work from home and earn huge income instantly",
    "Earn ₹50000 per month without experience",
    "Pay security deposit before joining",
    "Urgent hiring. Pay verification fee now",
    "Limited seats available. Pay now",
    "Submit PAN card and training fee",
    "Direct selection. Pay onboarding charges",
    "Pay consultancy fee for interview slot",
    "Guaranteed placement after payment",
    "Send documents and joining fee immediately"
]

linkedin_scams = [
    "LinkedIn recruiter asking registration fee",
    "LinkedIn job offer without interview",
    "Fake recruiter requesting payment",
    "Premium job access after payment",
    "Recruiter asking bank details immediately"
]

telegram_scams = [
    "Telegram job group asking joining fee",
    "Telegram recruiter requests UPI payment",
    "Join Telegram premium jobs by paying fee",
    "Telegram HR asking Aadhaar and money",
    "Telegram work from home scam"
]

visa_scams = [
    "Pay visa processing fee before interview",
    "Overseas job guaranteed after payment",
    "Immediate Dubai placement after registration fee",
    "Foreign job offer requesting advance payment",
    "Work abroad package available after deposit"
]

records = []

for _ in range(2500):
    records.append([
        random.choice(legit_jobs),
        0
    ])

for _ in range(1500):
    records.append([
        random.choice(scam_jobs),
        1
    ])

for _ in range(400):
    records.append([
        random.choice(linkedin_scams),
        1
    ])

for _ in range(300):
    records.append([
        random.choice(telegram_scams),
        1
    ])

for _ in range(300):
    records.append([
        random.choice(visa_scams),
        1
    ])

random.shuffle(records)

df = pd.DataFrame(records, columns=["description", "label"])

df.to_csv("recruitment_scam_dataset.csv", index=False)

print("Dataset Created Successfully")
print("Total Records:", len(df))
print(df.head())