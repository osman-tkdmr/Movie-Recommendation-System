# predict_sentiment.py
import torch
from transformers import BertTokenizerFast, BertForSequenceClassification

# 1) Model ve tokenizer'ı yükle
model_path = 'LLM/sentiment_model'  # Eğitimde kaydettiğin klasör
tokenizer = BertTokenizerFast.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)

# GPU kullanımı varsa model'i CUDA'ya al
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model.to(device)
model.eval()

# 2) Predict fonksiyonu
def predict_texts(texts):
    encodings = tokenizer(
        texts,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    )
    input_ids = encodings['input_ids'].to(device)
    attention_mask = encodings['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        preds = logits.argmax(-1)
    return preds.cpu().numpy()

# 3) Test
if __name__ == "__main__":
    sample_texts = [
        "This movie soo bad, I hate it.",
        "I love this movie!",
        "The acting is great, but the story is boring.",
        "The cinematography is amazing.",
        "The plot is linear and predictable.",
        "I would watch it again, but it's not my favorite genre.",
        "The acting is fantastic, but the music is just too loud.",
        "The cinematography is stunning, but the story is confusing.",
        "The plot is engaging and well-developed.",
        "I would not recommend this movie to anyone.",
        "The acting is terrible, but the music is just right.",
        "The cinematography is terrible, but the story is just right.",
        "The plot is linear and predictable.",
        "I would watch it again, but it's not my favorite genre.",
        "The acting is fantastic, but the music is just too loud.",
        "The cinematography is stunning, but the story is confusing.",
        "The plot is engaging and well-developed.",
        "I would not recommend this movie to anyone.",
        "The acting is terrible, but the music is just right.",
        "The cinematography is terrible, but the story is just right.",
        "The plot is linear and predictable.",
        "I would watch it again, but it's not my favorite genre.",
        "The acting is fantastic, but the music is just too loud.",
        "The cinematography is stunning, but the story is confusing.",
        "The plot is engaging and well-developed.",
        "I would not recommend this movie to anyone.",
        "The acting is terrible, but the music is just right.",
        "The cinematography is terrible, but the story is just right."
    ]
    predictions = predict_texts(sample_texts)
    print(predictions)