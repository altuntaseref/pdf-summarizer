import os
import pdfplumber
import openai
import ssl
from concurrent.futures import ThreadPoolExecutor

ssl._create_default_https_context = ssl._create_unverified_context

openai.api_key = "***********************"

# Get the PDF file path from the user
pdf_file_path = input("Enter the PDF file path: ")

# Read the PDF file using pdfplumber
pdf_text = ""
with pdfplumber.open(pdf_file_path) as pdf:
    for page in pdf.pages:
        pdf_text += page.extract_text().lower()

# Split the text into smaller chunks
chunk_size = 1500  # You can experiment with this value based on your content size
chunks = [pdf_text[i:i+chunk_size] for i in range(0, len(pdf_text), chunk_size)]

# Initialize the summary text
pdf_summary_text = ""

# Define a function to process a chunk using OpenAI API
def process_chunk(chunk):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful research assistant."},
            {"role": "user", "content": f"Summarize this: {chunk}"},
        ],
    )
    summary = response["choices"][0]["message"]["content"]
    # Remove the first part identifier if it exists
    if summary.startswith("Summary (Part"):
        summary = "\n".join(summary.split("\n")[1:])
    return summary

# Use ThreadPoolExecutor for parallel processing
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
    for i, future in enumerate(futures):
        chunk_summary = future.result()
        pdf_summary_text += chunk_summary + " "  # Add space between chunks

# Write the summary to a file with UTF-8 encoding
pdf_summary_file = os.path.join(
    os.path.dirname(pdf_file_path),
    os.path.splitext(os.path.basename(pdf_file_path))[0] + "_summary.txt"
)
with open(pdf_summary_file, "w+", encoding="utf-8") as file:
    file.write(pdf_summary_text)

# Print the summary
print(pdf_summary_text)

print("Summary saved to:", pdf_summary_file)
