from fastapi import FastAPI, HTTPException
from db.handler import fetch_all

app = FastAPI(docs_url="/swagger")


@app.get("/get_naver",
         summary="get naver review data")
async def naver_review_all():
    try:
        sql = """SELECT *
                 FROM study_db.naver_spot
                 """
        result = fetch_all(sql)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error : {e}")


# debug
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8888)
