from fastapi import FastAPI
from . import schema
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user = []

@app.post('/sign-in')
def signIn(request: schema.User):
    user.append(request)
    print(user)
    return {"message": "Client Registered Successfully"}