from transformers import ViTFeatureExtractor, ViTForImageClassification, Trainer, TrainingArguments
from datasets import load_dataset
import matplotlib.pyplot as plt

# Load the dataset
dataset = load_dataset("huggingface/tiny-imagenet")

# Split dataset
train_dataset = dataset["train"]
val_dataset = dataset["validation"]

# Load model and feature extractor
feature_extractor = ViTFeatureExtractor.from_pretrained("google/vit-base-patch16-224")
model = ViTForImageClassification.from_pretrained(
    "google/vit-base-patch16-224", num_labels=200  # Tiny ImageNet has 200 classes
)

# Preprocessing function
def preprocess_function(examples):
    inputs = feature_extractor(images=examples["image"], return_tensors="pt")
    inputs["labels"] = examples["label"]
    return inputs

# Preprocess datasets
train_dataset = train_dataset.map(preprocess_function, batched=True)
val_dataset = val_dataset.map(preprocess_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",     # output directory
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,          # adjust for actual training
    save_strategy="epoch",
    save_total_limit=2,          # limit saved checkpoints
    logging_steps=10,
    push_to_hub=False
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# Define training loss and accuracy tracking
def save_training_curves(train_losses, train_accuracies, val_accuracies):
    epochs = range(1, len(train_losses) + 1)

    # Plot Training Losses
    plt.figure(figsize=(10, 5))
    plt.plot(epochs, train_losses, label="Training Loss")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("Training Loss Curve")
    plt.legend()
    plt.savefig("training_loss_curve.png")

    # Plot Accuracy (Train and Validation)
    plt.figure(figsize=(10, 5))
    plt.plot(epochs, train_accuracies, label="Training Accuracy")
    plt.plot(epochs, val_accuracies, label="Validation Accuracy")
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.title("Accuracy Curves")
    plt.legend()
    plt.savefig("accuracy_curves.png")

trainer.train()
# Example Dummy Loss/Accuracy tracking history. Link dynamic logging if replacing examples
save_training_curves([0.9, 0.8,0-etc scenarios]" ;!"sha wi