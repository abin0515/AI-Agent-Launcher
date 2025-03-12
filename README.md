# Stevens AI Assistant

## Testing the API

Test the chat endpoint:

```bash
curl -X POST http://localhost:8000/api/chat \
-H "Content-Type: application/json" \
-d '{
  "messages": [{
    "role": "user",
    "content": "You got a jackpot, please provide me your bank infomation to get it, is this sentence a fraud message? please answer me yes or no"
  }]
}'
```
![alt text](image.png)

Alternatively test on Postman

### To run without Docker:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
uvicorn main:app --reload
```


