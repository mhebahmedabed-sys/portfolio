from pypdf import PdfReader
import fitz
import pytesseract
from PIL import Image , ImageEnhance,ImageFilter
from pathlib import Path
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM,AutoModelForQuestionAnswering
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
qa_tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2")
qa_model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")
#translator = pipelining ("translation", model="Helsinki-NLP/opus-mt-en-ar")
# English to Arabic Translation Model
#translator_tokenizer = AutoTokenizer.from_pretrained(
 #   "Helsinki-NLP/opus-mt-en-ar",
  #  force_download = True
#)
#translator_model = AutoModelForSeq2SeqLM.from_pretrained(
 #   "Helsinki-NLP/opus-mt-en-ar",
  #  force_download = True
#)


def translate_to_arabic(text):
    inputs = translator_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    outputs = translator_model.generate(
        **inputs,
        max_new_tokens=256
    )

    translation = translator_tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return translation
pdf_folder = Path("pdfs")
def clean_text(text):
    lines = text.splitlines()

    cleaned_lines=[]

    for line in lines:

        line = line.strip()

        if line :
            cleaned_lines.append(line)
        

    cleaned_text = "\n".join(cleaned_lines)
    return cleaned_text

    return cleaned_text
def split_text(text, chunk_size=800):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = "".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def oct_pdf():
    pdf_name = input("Enter PDF filee name:")
    file_path = pdf_folder /pdf_name
    if not file_path.exists():
        print("PDF file not found!")
        return ""

    doc = fitz.open(file_path)
    full_text = ""
    print("\n Starting OCR...")
    for page_number, page in enumerate(doc,1):
        print(f"Reading page {page_number}/ {len(doc)}...")
        pix = page.get_pixmap(matrix=fitz.Matrix(2,2))
        image = Image.frombytes("RGB",[pix.width,pix.height], pix.samples)
        image = image.convert("L")
        image = ImageEnhance.Contrast(image).enhance(2)
        image = image.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(image)
        full_text += text + "\n"
    doc.close()
    print("\nOCR completed!")
    print("\n--- OCR TEXT---")
    print(full_text[:3000])
    return full_text

def read_pdf():
    pdf_name = input("Enter PDF file name:")
    file_path= pdf_folder/ pdf_name
    if not file_path.exists():
        print("PDF file not found!")
        return 

    import PyPDF2
    full_text = ""
    with open (file_path , "rb") as file:
         reader = PyPDF2.PdfReader(file)

    
    
         #print("n PDF Content:\n")
         for page_number , page in enumerate(reader.pages ,1):
          text = page.extract_text()

          if text:
            full_text += text +"\n"
        
    print("\n PDF read successfuiiy!")
    print("\nNumber of pages:", len(reader.pages))
    print("\n---PDF TEXT---")
    print(full_text[:3000])
    return full_text
def summarize_text(text):
    chunks = split_text(text)
    summaries = []
    for i, chunk in enumerate(chunks,1):
        print(f"\nSummarizing part {i}/{len(chunks)}...")

        inputs = tokenizer(

            chunk,
            max_length =1024,
            truncation = True,
            return_tensors = "pt"

        )

        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=150,
            min_length=30,
            num_beams=4,
            early_stopping=True

        )

        summary = tokenizer.decode(
            summary_ids[0],
            skip_special_tokens = True

        )

        summaries.append(summary)
    return "\n\n".join(summaries)

def save_summary(summary):
    summaries_folder = Path("summaries")
    summaries_folder.mkdir(exist_ok = True)

    file_name = input ("Enter summary file name :")

    file_path = summaries_folder / file_name

    with open(file_path,"w",encoding = "utf-8") as file :
        file.write(summary)

    print(f"\nSummary saved successfully:{file_path}")

def view_summaries():
    summaries_folder = Path("summaries")


    if not summaries_folder.exists():
        print("No summaries found!")
        return

    files = list(summaries_folder.glob("*.txt"))

    if not files:
            print("No summaries found!")
            return

    print("\n==== SAVED SUMMARIES====")

    for i, file in enumerate(files,1):
                print(f"{i}. {file.name}")

    choice = input("\n Enter choice number: ")

    if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(files):
                with open (files[choice-1],"r", encoding="utf-8") as f:
                    summary = f.read()

                print("\n====SUMMARY====")
                print(summary)
            else:
                print("Invalid choice!")
    else:
            print("Plase enter a number!")
        
lectures = []

current_pdf_text = ""

file_path = Path(__file__).parent/"lectures.txt"

def save_lectures():
    with open(file_path,"w",encoding="utf-8") as file:
        for lecture in lectures:
            file.write(lecture + "\n")



def load_lectures():
    try:
        with open (file_path , "r", encoding="utf-8") as file:
            for line in file :
                lectures.append(line.strip())

    except FileNotFoundError:
        pass

def show_menu():

 print("\n===============")
 print("AI STUDY ASSISTNT")
 print("=================")
 print("1.Add Lecture")
 print("2.View Lecture")
 print("3.Search")
 print("4.Exit")
 print("5.Read PDF")
 print("6.Summarize PDF")
 print("7.View Saved Summaries")
 print("8.Ask Question")
 print("9.Generate Quiz")

def add_lecture():
   
    lecture = input("Enter lecture:")
    if lecture.strip()== "":
        print ("Lecture cannot be empty.")
    else:     
     lectures.append(lecture)
     save_lectures()
     print("Lecture added successfully!")
def view_lecture():
  
    if len(lectures)==0:

        print("\n No lecture found.")
    else: 
        print("\n Your Lecture:")
        for i, lecture in enumerate(lectures,1):
            print(f"{i}. {lecture}")
def search_lecture():

    if len(lectures)==0:

        print("\nNo lecture available.")

    else:

     search = input("Enter search word:")
     found= False

     for lecture in lectures:
         if search.lower() in lecture.lower():
            print("Found:", lecture)
            found = True

     if not found:
        print("No metching lecture found.")       

load_lectures()

import torch
def ask_question(text):
    question = input("Ask your question: ")

    words = question.lower().split()
    sentences = text.split(".")

    results = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        if any(word in sentence_lower for word in words):
            results.append(sentence.strip())

    if not results:
        print("No relevant information found.")
        return

    context = " ".join(results[:5])

    inputs = qa_tokenizer(
        question,
        context,
        max_length=512,
        truncation=True,
        return_tensors="pt"
    )

    outputs = qa_model(**inputs)

    start_position = outputs.start_logits.argmax()
    end_position = outputs.end_logits.argmax()

    answer_tokens = inputs["input_ids"][
        0, start_position:end_position + 1
    ]

    answer = qa_tokenizer.decode(
        answer_tokens,
        skip_special_tokens=True
    )

    print("\n===== AI ANSWER =====")
    print(answer)

def generate_quiz(text):
    import re

    sentences = re.split(r'[.!?\n]+', text)
    useful_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence.split()) >= 8:
            useful_sentences.append(sentence)

        if len(useful_sentences) == 5:
            break

    if not useful_sentences:
        print("Not enough text to generate quiz.")
        return

    print("\n===== BILINGUAL QUIZ | اختبار باللغتين =====")

    for i, sentence in enumerate(useful_sentences, 1):
        print(f"\n{i}. Lecture sentence:")
        print(sentence)

        try:
            arabic_translation = translate_to_arabic(sentence)
            print("\nArabic translation | الترجمة العربية:")
            print(arabic_translation)
        except Exception as error:
            print("Translation failed:", error)

        print("\nQuestion | السؤال:")
        print("What does this statement mean?")
        print("ماذا تعني هذه العبارة؟")

        print("\nAnswer | الإجابة:")
        print("Explain the statement using the lecture.")
        print("اشرح العبارة اعتماداً على المحاضرة.")

    print("\n===== QUIZ FINISHED | انتهى الاختبار =====")

while True:

    show_menu()
    choice = input("\nChoose an option:")

    if choice =="1":

        add_lecture()

    elif choice == "2":

        view_lecture()

    elif choice =="3":

        search_lecture()

    elif choice == "4":

        print("\n Think Yuo for using AI Study Assistant")
        print("goodbye!")

    elif choice =="5":

        read_pdf()
        print("\nPDF read successfully!")

    elif choice == "6":
        print("STEP 1")

        full_text = oct_pdf()

        current_pdf_text = full_text

        print("STEP 2")

        
        if full_text:
            cleaned_text = clean_text(full_text)

            print("\n==== CLEANED TEXT====")
            print(cleaned_text[:3000])

            summary = summarize_text(cleaned_text)

            print("\n==== PDF SUMMARY ====")
            print(summary)
            save_summary(summary)
    
        else:
           print("STEP 4 - NO text found")

    elif choice == "7":
        view_summaries()

    elif choice == "8":
      if current_pdf_text:
        print("PDF text length:", len(current_pdf_text))
        print("PDF text sample:", current_pdf_text[:500])
        ask_question(clean_text(current_pdf_text))
    elif choice == "9":
      if current_pdf_text:
        cleaned_text = clean_text(current_pdf_text)
        generate_quiz(cleaned_text)
      else:
        print("No PDF loaded. Please choose option 6 first.")