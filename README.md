# FastAPI MVP with Together.ai

## Features
- REST API for Orders
- Upload PDFs to extract patient data (first name, last name, DOB)
- Logs user activity
- Uses Together.ai for LLM inference
- Deployable on Render.com

## Setup

1. Clone repo and install dependencies:
```
pip install -r requirements.txt
```

2. Create `.env` file with:
```
TOGETHER_API_KEY=your_api_key_here
```

3. Run app:
```
uvicorn main:app --reload
```

4. Visit `http://localhost:8000/docs`

## Deploy on Render
- Push to GitHub
- Create Web Service on Render using `render.yaml`
- Add `TOGETHER_API_KEY` as environment variable in Render dashboard
