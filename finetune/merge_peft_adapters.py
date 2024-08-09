from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

import os
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, default="./finetuning_models/final_models/")
    parser.add_argument("--base_model_name_or_path", type=str, default="codellama/CodeLlama-7b-Instruct-hf")
    parser.add_argument("--peft_model_path", type=str, default="/")

    return parser.parse_args()

def main():
    args = get_args()

    base_model = AutoModelForCausalLM.from_pretrained(
        args.base_model_name_or_path,
        return_dict=True,
        torch_dtype=torch.float16 
    )

    model = PeftModel.from_pretrained(base_model, args.peft_model_path)
    model = model.merge_and_unload()
    
    if args.base_model_name_or_path.startswith("codellama"):
        from transformers import CodeLlamaTokenizer
        tokenizer = CodeLlamaTokenizer.from_pretrained(args.base_model_name_or_path, use_auth_token=True)
    else:
        tokenizer = AutoTokenizer.from_pretrained(args.base_model_name_or_path)

    
    model.save_pretrained(args.output_dir + f"{args.base_model_name_or_path}-merged")
    tokenizer.save_pretrained(args.output_dir + f"{args.base_model_name_or_path}-merged")
    print(f"Model saved to {args.base_model_name_or_path}-merged")

if __name__ == "__main__" :
    main()