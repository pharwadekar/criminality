import os
import torch
import torch.quantization
import pandas as pd
from datasets import Dataset
import re
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, AutoModelForQuestionAnswering
from huggingface_hub import login


access_token = "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"

model_name = "huggingface-course/bert-finetuned-squad"
#huggingface-course/bert-finetuned-squad
#deepset/bert-base-uncased-squad2
#nilq/mistral-1L-tiny


# Load the tokenizer and model for Mistral

tokenizerMistral = AutoTokenizer.from_pretrained(model_name, use_auth_token=access_token)

mistral = AutoModelForQuestionAnswering.from_pretrained(model_name, use_auth_token=access_token)


# Check if the tokenizer already has a pad token; if not, add one
if tokenizerMistral.pad_token is None:
    # Add a new pad token
    tokenizerMistral.add_special_tokens({'pad_token': '[PAD]'})

# Set the padding token
tokenizerMistral.pad_token = '[PAD]'

# Tokenization function

def tokenize_function(examples):

    return tokenizerMistral(examples['Testimonial'], padding="max_length", truncation=True, max_length=600)


def trueorfalse(name, test, evidence):
    # Define a sample testimonial
    testimonial = {
        "Name": name,
        "Testimonial": test
    }

    # Store evidence text related to the case
    evidence_text = evidence

    # Combine the evidence into a single string
    #evidence_text = "\n".join(evidence["Evidence"])

    # Prepare input text for the model
    input_text = f"""Assess the testimonial below and determine if it contains any lies.

    Testimonial: {testimonial['Testimonial']}
    Evidence: {evidence_text}

    Instructions:
    - If the testimonial is truthful, respond with NO and briefly explain why.
    - If it is lying, identify specific contradictions between the testimonial and the evidence, and explain why those parts are misleading.
    - Focus on direct contradictions only, ignoring vague similarities.
    """

    # Tokenize and generate output
    inputs = tokenizerMistral(input_text, return_tensors="pt", padding=True, truncation=True)


    # Get the model's predictions
    with torch.no_grad():
        outputs = mistral(**inputs)

    # Get the start and end positions of the answer
    answer_start = torch.argmax(outputs.start_logits[:, 1:]) + 1
    answer_end = torch.argmax(outputs.end_logits[:, 1:]) + 2

    # Decode the answer from the input ids
    answer = tokenizerMistral.convert_tokens_to_string(tokenizerMistral.convert_ids_to_tokens(inputs['input_ids'][0][answer_start:answer_end]))

    answer = answer.replace("[CLS]", "").strip()


    # Determine if the testimonial is a lie
    if "NO" in answer:
        print(f"{testimonial['Name']} is not lying. The testimonial aligns with the evidence.")
    else:
        print(f"{testimonial['Name']} may be lying.")

    # Ensure to only pass necessary arguments to the generate function
    # You can use **inputs to unpack them, but ensure no extra keys are included.
    #outputs = mistral.generate(**{k: v for k, v in inputs.items() if k in mistral.config.model_type},
    #                           pad_token_id=tokenizerMistral.eos_token_id)

    # Decode the output tokens
    #generated_text = tokenizerMistral.decode(outputs[0], skip_special_tokens=True)
    # Print the results
    #if "NO" not in generated_text.strip():  # Use strip() to avoid issues with leading/trailing spaces
    #    print(f"{testimonial['Name']} has stated something close to a lie.")
    #    print(generated_text)
    #else:
    #    print(f"{testimonial['Name']} is not lying.")


evidence = """Case Title: State vs. James Morton Incident Date: July 20, 2023 Location: Luxe Jewelers, Downtown City 1. CCTV Footage - Description: CCTV footage from Luxe Jewelers captured on the night of the robbery. - Time: Footage shows the entrance at 7:55 PM. - Details: Two masked suspects entered the store. The taller suspect, approximately 6'2", wielded a crowbar, while the second suspect brandished a firearm. The footage is grainy but clearly shows the black boots with white soles worn by the taller suspect. - Source: Luxe Jewelers surveillance system. 2. Crowbar Analysis - Description: A crowbar recovered from the trunk of James Morton’s car. - Details: Fibers matching those from Morton’s vehicle were found on the crowbar. Glass shards embedded in the crowbar were consistent with glass from the broken display cases. - Date Collected: July 21, 2023. - Source: Evidence locker at the police station. """
test = """I live in the same building as James Morton. On the night of July 20, 2023, I saw him coming into the building around 8:20 PM. He looked tired and wasn’t in any kind of rush. We greeted each other like usual, and I went up to my apartment. Later, when I heard about the robbery, I was surprised to hear James’ name involved. I’m sure he was home around the time everything went down."""
trueorfalse("Pranav",test, evidence )