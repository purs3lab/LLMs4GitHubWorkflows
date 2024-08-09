#  Experiment Setup  

## Experiment Environments
We run all experiments using one NVIDIA A100 GPU with 80G memory. 

## Fine-tune Starcoder/StarChat
Reference: https://github.com/bigcode-project/starcoder#fine-tuning

#### 1. Set up conda environment
First, create the conda environment `starcoderfinetune` and activate the conda environment.
```
conda create --name starcoderfinetune
conda activate starcoderfinetune
```

Then, install the pytorch version compatible with cuda 11.7.
```
conda install pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 pytorch-cuda=11.7 -c pytorch -c nvidia
```
Finally, install dependencies.
```
conda install -c huggingface transformers 
pip install git+https://github.com/huggingface/peft.git
conda install -c huggingface -c conda-forge datasets
conda install -c conda-forge accelerate
conda install -c conda-forge huggingface_hub
pip install bitsandbytes
pip install wandb
pip install scipy
``` 
#### 2. Set up environment variables
```
vim ~/.bash_profile
export HF_TOKEN=...
export WANDB_API_KEY=...
source ~/.bash_profile
```
#### 3. Fine-tune the model
```
python finetune/finetune.py \
  --model_path="HuggingFaceH4/starchat-beta" \
  --trainset="data/finetuning-dataset.json" \
  --testset="data/finetuning-testset.json" \
  --split="train" \
  --seq_length 2048 \
  --max_steps 3000 \
  --batch_size 1 \
  --instruction_column_name="Instruction" \
  --input_column_name="Input" \
  --output_column_name="Output" \
  --gradient_accumulation_steps 16 \
  --learning_rate 1e-4 \
  --lr_scheduler_type="cosine" \
  --num_warmup_steps 100 \
  --weight_decay 0.05 \
  --output_dir="finetuning_models/starchat" \
  --save_freq 200 \
  --run_name="starchat-finetune"
```
#### 4. Merge the adapter layers with the base model 
```
python finetune/merge_peft_adapters.py \
     --output_dir "finetuning_models/final_models/" \
     --base_model_name_or_path "HuggingFaceH4/starchat-beta" \
     --peft_model_path "finetuning_models/starchat/final_checkpoint"
```

## Fine-tune CodeLlama/Instruct-CodeLlama
Reference: https://ragntune.com/blog/guide-fine-tuning-code-llama
#### 1. Set up conda environment
First, create the conda environment `codellamafinetune` and activate the conda environment.
```
conda create --name codellamafinetune
conda activate codellamafinetune
```

Then, install dependencies.
```
pip install git+https://github.com/huggingface/transformers.git@main
pip install git+https://github.com/huggingface/peft.git
conda install -c conda-forge accelerate
conda install -c conda-forge huggingface_hub
pip install datasets
pip install bitsandbytes
pip install wandb
pip install scipy
pip install tiktoken
pip install sentencepiece
pip install protobuf
```
#### 2. Set up environment variables
```
vim ~/.bash_profile
export WANDB_API_KEY=...
source ~/.bash_profile
```
#### 3. Fine-tune the model
```
python finetune/finetune.py \
   --model_path="codellama/CodeLlama-7b-Instruct-hf" \
   --trainset="data/finetuning-dataset.json" \
   --testset="data/finetuning-testset.json" \
   --split="train" \
   --seq_length 2048 \
   --max_steps 3000 \
   --batch_size 1 \
   --instruction_column_name="Instruction" \
   --input_column_name="Input" \
   --output_column_name="Output" \
   --gradient_accumulation_steps 16 \
   --learning_rate 1e-4 \
   --lr_scheduler_type="cosine" \
   --num_warmup_steps 100 \
   --weight_decay 0.05 \
   --output_dir="finetuning_models/instruct-codellama" \
   --save_freq 200 \
   --run_name="instruct-codellama-finetune"
```
#### 4. Merge the adapter layers with the base model 
```
python finetune/merge_peft_adapters.py \
    --output_dir "finetuning_models/final_models/" \
    --base_model_name_or_path "codellama/CodeLlama-7b-Instruct-hf" \
    --peft_model_path "finetuning_models/instruct-codellama/final_checkpoint"
```
