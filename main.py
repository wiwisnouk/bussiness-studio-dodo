from fastapi import FastAPI, HTTPException, Form
from routers import HomePage

app = FastAPI()

app.include_router(HomePage.router)

#<button class="product-button" onclick="addToCart('{{ product.id }}')">
                #Выбрать
            #</button>