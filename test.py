from PIL import Image
import google.generativeai as genai

genai.configure(api_key="AIzaSyCxUUSV88SsR0tMfNo9XLmuw64gDC7SAZU")

model = genai.GenerativeModel("gemini-2.5-flash")

img = Image.open("uploads/test_offer.png")

response = model.generate_content([
    "Extract all text from this image",
    img
])

print(response.text)