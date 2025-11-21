from fastapi import FastAPI, HTTPException
import uvicorn
import time


app = FastAPI()

i = 0
@app.post("/real_time")
async def store_data(data: dict):
     global i
     instruction={"acceleration":"","steering":""}
     try:
         for item in data:
            #front distance processing
            if item == "front_distance":
               value = int(data[item])
               if value < 20:
                  instruction["acceleration"]="brake"
               elif value > 40:
                  instruction["acceleration"]="slow down"
               else:
                  instruction["acceleration"]="keep going"

            #lateral distance processing
            elif item == "rear_distance":
                  value = int(data[item])
                  if value < 15:
                     instruction["steering"]="dont steer"
                  elif value >= 15 and value < 50 :
                     instruction["steering"]="be careful while steering"
                  else:
                     instruction["steering"]="steer free"
         print(f"Sendind instructions: {instruction}")
         i+=1


         #Add delay
         if i%10==0 and i!=0:
             time.sleep(5)
         return instruction
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
