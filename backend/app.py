from fastapi import FastAPI, Request
from pydantic import BaseModel
import json
import requests

app = FastAPI()

class GenerateRequest(BaseModel):
    model: str              # Name of the model to be used
    prompt: str             
    stream: bool = False    # Flag to enable streaming of responses

@app.post("/generate")
async def generate_full(request: GenerateRequest):
    url = "http://localhost:11434/api/generate"    
    headers = {"Content-Type": "application/json"}  
    data = {
        "model": request.model,     
        "prompt": request.prompt,   
        "stream": request.stream    
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    
    raw_response = ""
    for line in response.iter_lines():
        if line:
            raw_response += line.decode('utf-8') + "\n"     

    return raw_response

@app.post("/generate_formatted")
async def generate_formatted(request: GenerateRequest):
    url = "http://localhost:11434/api/generate"    
    headers = {"Content-Type": "application/json"}  
    data = {
        "model": request.model,     
        "prompt": request.prompt,   
        "stream": request.stream   
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    
    formatted_response = ""
    for line in response.iter_lines():
        if line:
            try:
                json_line = json.loads(line.decode('utf-8'))        
                if "response" in json_line:
                    formatted_response += json_line["response"]     
            except json.JSONDecodeError:
                continue
    
    formatted_response = formatted_response.strip() + "\n"
    
    return {"response": formatted_response}
