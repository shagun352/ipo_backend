
from schemas.pan_schema import PANResponse,IPOStatusResponse,IPOPayload
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from fastapi import FastAPI,Depends, status
from models.ipo_model import IPO
from database.connection import engine,SessionLocal
from database.base import Base
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

app = FastAPI(title="IPO")
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/add-pan/",  status_code=status.HTTP_201_CREATED)
async def add_user_pan(data : PANResponse, db: Session = Depends(get_db)):
    already_existing_pan = db.query(IPO).filter(IPO.pan_number==data.pan_number).first()
    if already_existing_pan:
        return {"detail": "PAN number already exists"}
    new_pan = IPO(pan_number=data.pan_number, username=data.username)
    db.add(new_pan)
    db.commit()
    db.refresh(new_pan)
    return {"message": "PAN added successfully!", 
        "pan_number": new_pan.pan_number, 
        "username": new_pan.username}


@app.post('/getipos/')
def fetch_ipos():
    url = "https://linkintime.co.in/Initial_Offer/IPO.aspx/GetDetails"
    payload = {}
    headers = {
        "Content-Type": "application/json", 
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            escaped_xml = response.json()["d"]
            decoded_xml = escaped_xml.replace("\\u003c", "<").replace("\\u003e", ">").replace("\\r\\n", "")
            # Parse the XML to extract IPO details
            root = ET.fromstring(decoded_xml)
            ipos = []
            for table in root.findall(".//Table"):
                company_id = table.find("company_id").text
                company_name = table.find("companyname").text
                ipos.append({"id": company_id, "name": company_name})
            return ipos
        else:
            print(f"Failed to fetch IPOs. HTTP Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


from fastapi import FastAPI, HTTPException
@app.post("/fetch-ipo-status")
def fetch_ipo_status(request: IPOPayload):
    url = "https://linkintime.co.in/Initial_Offer/IPO.aspx/SearchOnPan"

    # Payload for the request
    payload = {
        'clientid': request.client_id,
        'PAN': request.pan,
        'IFSC': '',
        'CHKVAL': '1',
        'token': ''
    }

    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()

            if "d" in result:
                xml_data = result["d"]
                print(xml_data)
                ipo_status = parse_ipo_status(xml_data)
                if ipo_status:
                    return ipo_status
                else:
                    raise HTTPException(status_code=500, detail="Error parsing IPO status.")
            else:
                raise HTTPException(status_code=404, detail="IPO status not found in the response.")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch status. Response: {response.text}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def parse_ipo_status(xml_data):
    try:
        root = ET.fromstring(xml_data)

        for table in root.findall("Table"):
            print("forrrrrrrrrrrrr")
            ipo_status = IPOStatusResponse(
                id=table.find("id").text,
                offer_price=table.find("offer_price").text,
                applicant_name=table.find("NAME1").text,
                company_name=table.find("companyname").text,
                shares_applied=table.find("SHARES").text,
                shares_allotted=table.find("ALLOT").text,
                adjusted_amount=table.find("AMTADJ").text,
                refund_amount=table.find("RFNDAMT").text,
                category=table.find("PEMNDG").text,
            )
            print(ipo_status,"statuss")
            return ipo_status
    except ET.ParseError as e:
        return None


from fastapi import HTTPException

@app.post("/update-ipo-details")

def update_ipo_details(data: IPOPayload, db: Session = Depends(get_db)):
    """
    Updates the IPO details for a specific PAN number based on API response.
    """
    url = "https://linkintime.co.in/Initial_Offer/IPO.aspx/SearchOnPan"
    payload = {
        'clientid': data.client_id,
        'PAN': data.pan,
        'IFSC': '',
        'CHKVAL': '1',
        'token': ''
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if "d" in result:
                xml_data = result["d"]
                ipo_status = parse_ipo_status(xml_data)

                if ipo_status:
                    shares_allotted = ipo_status.shares_allotted
                    print(shares_allotted)
                    pan_record = db.query(IPO).filter(IPO.pan_number == data.pan).first()

                    if pan_record:
                        pan_record.status = "Alloated"
                        pan_record.shares_allotted = ipo_status.shares_allotted
                        pan_record.applicant_name = ipo_status.applicant_name
                        pan_record.company_name = ipo_status.company_name
                        pan_record.updated_at = datetime.utcnow().isoformat()

                        db.commit()

                        return {"status": "success", "message": "Details updated successfully.", "data": ipo_status}
                    else:
                        raise HTTPException(status_code=404, detail="PAN record not found in the database.")
                else:
                    raise HTTPException(status_code=500, detail="Error parsing IPO status.")
            else:
                raise HTTPException(status_code=404, detail="IPO status not found in the response.")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch status. Response: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


   
@app.get("/get_all_pan")
def get_all_pan(db: Session = Depends(get_db)):
    '''
    get all the pan number and username from database
    '''
    pan_with_usernames = db.query(IPO.pan_number, IPO.username).all()
    result = [{"pan_number": pan, "username": username} for pan, username in pan_with_usernames]
    return {"status": "success", "data": result}
