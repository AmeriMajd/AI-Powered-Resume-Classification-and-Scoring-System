import torch
print("Torch version:", torch.__version__)
from bs4 import BeautifulSoup
import requests
import os
from transformers import pipeline

Resume_dir= "data/resumes/"
os.makedirs(Resume_dir, exist_ok=True)

def scrap_resumes(url , max_resume=5) :
    headers =  {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"}
    try :
         response= requests.get(url,headers = headers)
         response.raise_for_status()
         soup = BeautifulSoup(response.text, 'html.parser')
         resume_elements = soup.find_all('div',class_name='resume-content')[:max_resume]
         for i, element in enumerate(resume_elements):
             resume_text = element.get_text(strip=True)
             if resume_text:
                 with open(f"{Resume_dir}/scraped_resume_{i + 1}.txt", "w", encoding="utf-8") as f:
                     f.write(resume_text)
                 print(f"Saved scraped_resume_{i + 1}.txt")
    except Exception as e:
        print(f"Error during scraping: {e}")
def generate_resume(prompt , output_file) :
    generator = pipeline('text-generation',model='gpt2')
    try :
        result = generator(prompt , max_length=512 , num_return_sequences=1 , truncation=True)
        resume_text = result.sequences[0]['generated_text']
        with open(output_file,'w',encoding='utf-8') as f:
            f.write(resume_text)
    except Exception as e:
        print(f"Error during resume generation: {e}")
if __name__ == "__main__":
   scrape_url = "https://example.com/resume-templates"
   print("Starting web scraping...")
   scrap_resumes(scrape_url, max_resumes=5)
   prompts = [
        "Generate a resume for a Software Engineer with 5 years of experience in Python and Java.",
        "Generate a resume for a Data Scientist with expertise in machine learning and 3 years of experience.",
        "Generate a resume for a Marketing Manager with 7 years of experience in digital campaigns."
    ]
   print("Generating synthetic resumes...")
   for i, prompt in enumerate(prompts):
        generate_resume(prompt, f"{Resume_dir}/synthetic_resume_{i + 1}.txt")