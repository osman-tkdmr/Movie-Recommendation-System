import os
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from transformers import BertTokenizerFast, BertForSequenceClassification, DistilBertTokenizerFast, DistilBertForSequenceClassification

def visualize_model_comparison(results):
    """
    Visualize the performance comparison of different models.
    
    Args:
        results: List of dictionaries containing model results
    """
    if not results:
        print("No results to visualize.")
        return
    
    # Extract model names and metrics
    model_names = [r['model_name'] for r in results]
    accuracies = [r['eval_results']['eval_accuracy'] for r in results]
    f1_scores = [r['eval_results']['eval_f1'] for r in results]
    training_times = [r['training_time'] / 60 for r in results]  # Convert to minutes
    
    # Set up the figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot performance metrics
    x = np.arange(len(model_names))
    width = 0.35
    
    ax1.bar(x - width/2, accuracies, width, label='Accuracy')
    ax1.bar(x + width/2, f1_scores, width, label='F1 Score')
    ax1.set_ylabel('Score')
    ax1.set_title('Model Performance Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(model_names, rotation=45, ha='right')
    ax1.legend()
    ax1.set_ylim(0, 1.0)
    
    # Plot training times
    ax2.bar(x, training_times, color='orange')
    ax2.set_ylabel('Training Time (minutes)')
    ax2.set_title('Training Time Comparison')
    ax2.set_xticks(x)
    ax2.set_xticklabels(model_names, rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Create visualizations directory if it doesn't exist
    os.makedirs('./LLM/visualizations', exist_ok=True)
    plt.savefig('./LLM/visualizations/model_comparison.png')
    plt.show()
    
    # Print the best model based on accuracy
    best_idx = np.argmax(accuracies)
    print(f"Best model based on accuracy: {model_names[best_idx]} (Accuracy: {accuracies[best_idx]:.4f}, F1: {f1_scores[best_idx]:.4f})")

def plot_confusion_matrix(model, tokenizer, texts, true_labels):
    """
    Plot confusion matrix for a model on given texts and labels.
    
    Args:
        model: The trained model
        tokenizer: The tokenizer for the model
        texts: List of text samples
        true_labels: List of true labels
        
    Returns:
        predictions: Array of predicted labels
    """
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        
        # Tokenize the texts
        encodings = tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors="pt")
        
        # Move to device
        input_ids = encodings['input_ids'].to(device)
        attention_mask = encodings['attention_mask'].to(device)
        
        # Get predictions
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            predictions = outputs.logits.argmax(dim=-1).cpu().numpy()
        
        # Create confusion matrix
        cm = confusion_matrix(true_labels, predictions)
        
        # Plot
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.xlabel('Predicted Labels')
        plt.ylabel('True Labels')
        plt.title(f'Confusion Matrix - {model.config._name_or_path}')
        
        # Create visualizations directory if it doesn't exist
        os.makedirs('./LLM/visualizations', exist_ok=True)
        plt.savefig(f'./LLM/visualizations/confusion_matrix_{model.config._name_or_path.replace("/", "_")}.png')
        plt.show()
        
        return predictions
    except Exception as e:
        print(f"Error plotting confusion matrix: {e}")
        return None

def predict_sentiment(text, model_path='./LLM/best_model'):
    """
    Predict sentiment for a given text using the best trained model.
    
    Args:
        text: Text to analyze
        model_path: Path to the model directory
        
    Returns:
        Dictionary with sentiment prediction and confidence scores
    """
    # Check if model exists
    if not os.path.exists(model_path):
        return {"error": "Model not found. Please train models first."}
    
    try:
        # Load model and tokenizer using the config-based approach
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model, tokenizer = load_model_by_config(model_path)
        
        # Move model to device
        model.to(device)
        model.eval()
        
        # Tokenize input
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        input_ids = inputs["input_ids"].to(device)
        attention_mask = inputs["attention_mask"].to(device)
        
        # Get prediction
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
        
        # Convert to sentiment labels
        sentiment_labels = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
        sentiment = sentiment_labels[predicted_class]

        # Get confidence scores
        confidence_scores = {sentiment_labels[i]: float(probabilities[0][i]) for i in range(probabilities.shape[1])}
        
        return {
            "text": text,
            "sentiment": sentiment,
            "confidence": confidence_scores
        }
    except Exception as e:
        return {"error": f"Error predicting sentiment: {str(e)}"}

def batch_predict(texts, model_path='./LLM/best_model', batch_size=32):
    """
    Predict sentiment for a batch of texts using the best trained model.
    
    Args:
        texts: A list of texts to analyze.
        model_path: Path to the model directory.
        batch_size: The batch size for processing.
        
    Returns:
        A list of dictionaries, each with sentiment prediction and confidence scores.
    """
    if not isinstance(texts, list):
        # If a single string is passed, wrap it in a list
        if isinstance(texts, str):
            texts = [texts]
        else:
            # If it's another iterable (like a pandas Series), convert to list
            try:
                texts = list(texts)
            except TypeError:
                 return [{"error": "Invalid input type for texts. Expected list or string.", "text": None, "sentiment": None, "confidence": None}]

    if not texts:
        return []

    if not os.path.exists(model_path):
        return [{"error": "Model not found. Please train models first.", "text": txt, "sentiment": None, "confidence": None} for txt in texts]
    
    results = []
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Assuming load_model_by_config is defined in this file or imported
        model, tokenizer = load_model_by_config(model_path) 
        model.to(device)
        model.eval()
        
        # Ensure sentiment_labels match your model's output configuration
        sentiment_labels = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            # Filter out None or non-string items from batch_texts to prevent tokenizer errors
            valid_batch_texts = [t for t in batch_texts if isinstance(t, str)]
            if not valid_batch_texts:
                # Add error entries for invalid items if any were filtered
                for text_item in batch_texts:
                    if not isinstance(text_item, str):
                        results.append({
                            "text": text_item,
                            "error": "Invalid input text (e.g., None or non-string)",
                            "sentiment": None,
                            "confidence": None
                        })
                continue

            inputs = tokenizer(valid_batch_texts, return_tensors="pt", truncation=True, padding=True, max_length=128)
            
            input_ids = inputs["input_ids"].to(device)
            attention_mask = inputs["attention_mask"].to(device)
            
            with torch.no_grad():
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                probabilities_batch = torch.nn.functional.softmax(logits, dim=-1)
                predicted_classes_batch = torch.argmax(probabilities_batch, dim=-1)
            
            # Map results back to original batch_texts structure if some were invalid
            valid_text_idx = 0
            for text_item in batch_texts:
                if not isinstance(text_item, str):
                    # This was handled before tokenization, result already added
                    continue
                
                predicted_class = predicted_classes_batch[valid_text_idx].item()
                sentiment = sentiment_labels.get(predicted_class, "Unknown")
                
                current_probabilities = probabilities_batch[valid_text_idx]
                confidence_scores = {sentiment_labels.get(k, f"Class_{k}"): float(current_probabilities[k]) for k in range(current_probabilities.shape[0])}
                
                results.append({
                    "text": text_item,
                    "sentiment": sentiment,
                    "confidence": confidence_scores
                })
                valid_text_idx += 1
        return results
    except Exception as e:
        print(f"Error during batch prediction: {e}")
        return [{"error": f"Batch prediction failed: {e}", "text": txt, "sentiment": None, "confidence": None} for txt in texts]
        
        # Move model to device
        model.to(device)
        model.eval()
        
        # Convert to sentiment labels
        sentiment_labels = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
        
        results = []
        # Process in batches to avoid memory issues
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            
            # Ensure all texts are strings
            batch_texts = [str(text) if text is not None else "" for text in batch_texts]
            
            # Process each text individually to avoid tokenizer issues
            batch_results = []
            for text in batch_texts:
                # Tokenize input
                inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
                input_ids = inputs["input_ids"].to(device)
                attention_mask = inputs["attention_mask"].to(device)
                
                # Get predictions
                with torch.no_grad():
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                    logits = outputs.logits
                    probabilities = torch.nn.functional.softmax(logits, dim=-1)
                    predicted_class = torch.argmax(probabilities, dim=-1).item()
                
                sentiment = sentiment_labels[predicted_class]
                confidence_scores = {sentiment_labels[k]: float(probabilities[0][k]) for k in range(5)}
                
                batch_results.append({
                    "text": text,
                    "sentiment": sentiment,
                    "confidence": confidence_scores
                })
            
            results.extend(batch_results)
        
        return results
    except Exception as e:
        return [{"error": f"Error predicting sentiment: {str(e)}"}]


def load_model_by_config(model_path):
    """
    Load the appropriate model class based on the model_type in config.json
    
    Args:
        model_path: Path to the model directory
        
    Returns:
        model: The loaded model
        tokenizer: The loaded tokenizer
    """
    import json
    import os
    from transformers import AutoTokenizer
    
    # Check if model exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Please train models first.")
    
    # Read config.json to determine model type
    config_path = os.path.join(model_path, 'config.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Get model type and architecture
    model_type = config.get('model_type', '').lower()
    architectures = config.get('architectures', [])
    architecture = architectures[0] if architectures else ''
    
    # Map model types to their respective classes
    model_class_map = {
        'bert': 'BertForSequenceClassification',
        'distilbert': 'DistilBertForSequenceClassification',
        'albert': 'AlbertForSequenceClassification',
        'roberta': 'RobertaForSequenceClassification'
    }
    
    # Get the appropriate model class
    model_class_name = model_class_map.get(model_type)
    if not model_class_name:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    # Import the appropriate model class
    from transformers import (
        BertForSequenceClassification,
        DistilBertForSequenceClassification,
        AlbertForSequenceClassification,
        RobertaForSequenceClassification
    )
    
    # Map model class names to actual classes
    model_classes = {
        'BertForSequenceClassification': BertForSequenceClassification,
        'DistilBertForSequenceClassification': DistilBertForSequenceClassification,
        'AlbertForSequenceClassification': AlbertForSequenceClassification,
        'RobertaForSequenceClassification': RobertaForSequenceClassification
    }
    
    # Get the model class
    ModelClass = model_classes.get(model_class_name)
    if not ModelClass:
        raise ValueError(f"Model class not found for {model_class_name}")
    
    # Load model and tokenizer
    model = ModelClass.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    return model, tokenizer