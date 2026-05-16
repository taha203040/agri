from transformers import AutoModelForImageClassification
from torchvision import transforms
from PIL import Image
import torch

def imageAnalyzer(path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = AutoModelForImageClassification.from_pretrained(
        "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
    )
    model.to(device)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    image = Image.open(path).convert('RGB')
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)

    predicted_class = model.config.id2label[predicted_idx.item()]

    return {
        "disease": predicted_class,
        "confidence": round(confidence.item(), 4),
        "all_predictions": [
            {"label": model.config.id2label[i], "score": round(probabilities[0][i].item(), 4)}
            for i in range(len(probabilities[0]))
        ]
    }

result = imageAnalyzer('../../i.jpg')
print(f"Disease  : {result['disease']}")
print(f"Confidence: {result['confidence'] * 100:.1f}%")