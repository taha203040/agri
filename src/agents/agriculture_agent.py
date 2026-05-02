# from langchain.agents import   create_agent
# from src.retrieval.retriever import retriever_tool , diseases_tool
# from dotenv import load_dotenv
# load_dotenv()
# agent = create_agent(    
#     model='deepseek-chat',
#     tools=[retriever_tool , diseases_tool],
    
#     system_prompt='you are helpful assistant specialzed in agriculture field answer just the questions that related with soil sample using the soil_retriever tool and the diseases using disease_retriever'
# )
# # question = {'messages': [{'role': 'user', 'content': 'how soil sample help to grow planets and increase the amount of the farming ?'}]}
# question = {'messages': [{'role': 'user', 'content': 'what most diseases that tomato get it?'}]}
# answer = agent.invoke(question)
# # print('answr',answer['messages'].content)
# # print('answer',answer['messages'].content)
# ai_messages = [msg.content for msg in answer['messages'] if msg.__class__.__name__ == 'AIMessage']
# for i, msg in enumerate(ai_messages, 1):
#     print(f"AI message {i}: {msg}")
# from ultralyticsplus import YOLO, render_result

# # load model
# model = YOLO('foduucom/plant-leaf-detection-and-classification')

# # set model parameters
# model.overrides['conf'] = 0.25  # NMS confidence threshold
# model.overrides['iou'] = 0.45  # NMS IoU threshold
# model.overrides['agnostic_nms'] = False  # NMS class-agnostic
# model.overrides['max_det'] = 1000  # maximum number of detections per image


# # set image
# image = './i.png'

# # perform inference
# results = model.predict(image)

# # observe results
# print(results[0].boxes)
# render = render_result(model=model, image=image, result=results[0])
# render.show()


# src/agents/agriculture_agent.py
import torch
from PIL import Image
from torchvision import transforms
import requests
from transformers import AutoModelForImageClassification

class AgricultureAgent:
    def __init__(self):
        self.model_name = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load model
        self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Manual preprocessing (since auto processor fails)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def predict(self, image_path):
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
        
        # Get label
        predicted_class = self.model.config.id2label[predicted_idx.item()]
        confidence_score = confidence.item()
        
        return {
            "disease": predicted_class,
            "confidence": confidence_score,
            "all_predictions": [
                {
                    "label": self.model.config.id2label[i],
                    "score": probabilities[0][i].item()
                }
                for i in range(len(probabilities[0]))
            ]
        }

# Usage
if __name__ == "__main__":
    agent = AgricultureAgent()
    result = agent.predict("./image.png")
    print(f"Disease: {result['disease']}")
    print(f"Confidence: {result['confidence']:.2%}")