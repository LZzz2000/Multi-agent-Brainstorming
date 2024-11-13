# Multi-agent-Brainstorming

Multi-agent Brainstorming for Interpreting and Mitigating Hallucination in Multimodal-LLM



## Install

1. Clone this repository and navigate to Multi-agent-Brainstorming folder

```shell
https://github.com/LZzz2000/Multi-agent-Brainstorming.git
cd Multi-agent-Brainstorming
```

2. Install Package

```
tqdm
time
google-generativeai
Pillow
random
json
```



## Download Dataset

Please download [val2014](https://cocodataset.org/#download), [MMHal-Bench](https://huggingface.co/datasets/Shengcao1006/MMHal-Bench) and extract it to the ```data``` directory.  

The annotation files have been downloaded.

```
./Multi-agent-Brainstorming/data/val2014
./Multi-agent-Brainstorming/data/mmhal_images
./Multi-agent-Brainstorming/data/response_template.json
./Multi-agent-Brainstorming/data/coco_pope_random.json
./Multi-agent-Brainstorming/data/coco_pope_popular.json
./Multi-agent-Brainstorming/data/coco_pope_adversarial.json
```



## Get API Key

Please get ```api_key``` from [Google AI Studio](https://aistudio.google.com/).

```python
google_api_key = '' # add your api_key
```



## Run

1. Enter the ```code``` directory and fill in the ```out_file```. 

2. Set ```max_round``` and ```model_name```.

3. Run

```python
python run_gemini_pope_random_multi.py
```



## Evaluation

1. Enter the ```eval``` directory and fill in the ```ans_file```. 
2. Set the ```out```  flag to "True" if you want to output the bad case.
3. Eval

- for POPE

```python
python eval_pope.py
```

- for MMHal-Bench

```pytho
python eval_mmhal.py \
    --response output.json \
    --evaluation output_result.json\
    --api-key your-openai-apikey \
    --gpt-model gpt-4-0314
```

- for CHAIR

```python
python chair.py \
    --cap_file output.json \
    --image_id_key image_id \
    --caption_key caption \
    --cache ./chair.pkl \
    --save_path output_result.json
```



