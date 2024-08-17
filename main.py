from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel

class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'

# Generating Interfaces with pydantic BaseModel
# aka Data Model of Payload
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

app = FastAPI()

"""
Path order matters
Put them in order so that there is no overlap
No redefinition, only first one gets called
"""

@app.get("/")
async def root():
    return {'message': 'Hello World'}

"""
Optional Parameter Example
Parameters will be detected by name so as long as it's matching
It can find the value

Introducing Annotated typing (provides metadata)
Fastapi uses this along with Query to provide parameter validation
"""
@app.get('/users/{user_id}/items/{item_id}') # Things that appear here are path parameters
async def read_item(
    user_id: Annotated[
        int,
        Path(
            title='The ID of the item to get'
        )
    ],
    item_id: str = ..., # Clearer way to tell users that this is required
    q: Annotated[
        str | None,
        Query(
            max_length=50,
            alias='item-query', # allows non Python-compliant variable names (this is the parameter argument placeholder)
            title='Item Query', # The title of the item to be shown on OpenAI Swagger like interface (Can only be seen in redoc)
            description='Query string for the items to search in the database that have a good match', # The description of the parameter to be shown on Open AI Swagger like interface (Shown in both redoc and doc)
            deprecated=False # Show whether endpoint has been deprecated
        )
    ] = None, # Things that appear here are query parameters, must be called in path with ?
    bananas: Annotated[list, Query()] = [], # Can be used for list of queries, represented in ?bananas=val&bananas=val2, Query does not check contents in list query
    short: bool = False
):
    item = {'item_id': item_id, 'owner_id': user_id}
    if q:
        item.update({'q': q})
    if bananas:
        item.update({
            'bananas': bananas
        })
    if not short: # Interesting property: we can use true/on/yes to represent truthiness
        item.update(
            {'description': ' This is an amazing item that has a long description'}
        )
    return item

# @app.get('/items/')
# async def read_item(skip:int = 0, limit: int = 10):
#     return fake_items_db[skip: skip + limit]

@app.get('/models/{model_name}')
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {'model_name': model_name, 'message': 'Deep Learning FTW!'}
    if model_name.value == 'lenet':
        return {'model_name': model_name, 'message': 'LeCNN all the images'}
    return {'model_name': model_name, 'message': 'Have some residuals'}

# Required query parameters
@app.get('/items/{item_id}')
async def read_user_item(item_id: str, needy: str):
    item = {'item_id': item_id, 'needy': needy}
    return item

# Post items
# Similarly to get, it will automatically find the
# placeholders and schemas to assign the values accordingly
@app.post('/items/')
async def create_item(item: Item): # Receives payload here
    return item