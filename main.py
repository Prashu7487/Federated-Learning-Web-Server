from fastapi import FastAPI,BackgroundTasks
from . import schema
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from .utility.Server import Server



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user = []

STREAM_DELAY = 5 # second
RETRY_TIMEOUT = 15000  # milisecond
round = 1
global_parameters = {}
max_round = 5
server = Server(global_parameters,max_round)


def event_generator():
    data = f"Ask Round {round} parameters"
    yield data

@app.get('/events')
async def sse_endpoint():
    return EventSourceResponse(event_generator())

@app.post('/sign-in')
def signIn(request: schema.User):
    user.append(request)
    print(f"{request.name} is registered")
    return {"message": "Client Registered Successfully"}

@app.get('/get-parameters')
def getParameters():
    obj = {
        "is_first":  1 if server.curr_round==1 else 0,
        "parameter": server.globals_parameters,
        "round_num": server.curr_round
    }
    return obj

@app.post('/receive-parameters')
def receiveParameters(request: schema.Parameter):
    server.client_parameters[request.client_id] = request.client_parameter
    return {'message': 'Parameters are received!'}
    

def receive_parameters_client(server):    
    event_generator()
    while(len(server.client_parameters)!=len(user)):
        pass
    

@app.get('/federated-learning')
async def federatedLearning( background_tasks: BackgroundTasks):
    background_tasks.add_task()
    return {"status": "Federated Learning started"}    
            
            
async def start_federated_learning():
    for i in range(1,server.max_round):
        print("-"*50)
        server.curr_round = i
        print(f"Round {i}")
        print("-"*50)
        receive_parameters_client(server)
        # Aggregate
        server.aggregate_weights_fedAvg_Neural()
        