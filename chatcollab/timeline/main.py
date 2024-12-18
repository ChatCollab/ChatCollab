# FastAPI for Interfacing with the Central Event Timeline

#uvicorn timeline.main:app --reload

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import chatcollab.timeline.models as models
from chatcollab.timeline.schemas import *
import json
from datetime import datetime

filename_openai_log = "openai_log.json"

app = FastAPI(title="Agent and Events API", description="Manage Agents and their Events", version="1.0")

# Dependency to get the database session
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create_agent/", response_model=AgentSchema, description="Create a new Agent")
def create_agent(agent: AgentCreateSchema, db: Session = Depends(get_db)):
    agent = models.Agent(
        name = agent.name,
        isSource = agent.isSource,
        tags = agent.tags
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

@app.get("/list_agents/", description="List all Agents", response_model=List[AgentSchema])
def list_agents(db: Session = Depends(get_db)):
    return db.query(models.Agent).all()

@app.get("/list_events/", description="List all Events with Auth of specified Agent", response_model=List[EventSchema])
def list_events(public_key: str, private_key: str, db: Session = Depends(get_db)):
    # Add the following to require auth of public and private key from an agent:
    # agent = db.query(models.Agent).filter(models.Agent.public_key == public_key, models.Agent.private_key == private_key).first()
    # if not agent:
    #     raise HTTPException(status_code=404, detail="Agent not found")

    return db.query(models.Event).all()

@app.post("/create_event/", response_model=EventSchema, description="Create a new Event for a specified Agent")
def create_event(public_key: str, private_key: str, event: EventCreateSchema, db: Session = Depends(get_db)):
    
    # Add the following to require auth of public and private key from an agent:
    # agent = db.query(models.Agent).filter(models.Agent.public_key == public_key, models.Agent.private_key == private_key).first()
    # if not agent:
    #     raise HTTPException(status_code=404, detail="Agent not found")

    # Temporary while not requiring auth: (placeholder with id as 0)
    agent = models.Agent()
    agent.id = 0

    # Create the event for the agent
    db_event = models.Event(title=event.title, source_id=agent.id, tags=event.tags, payload=event.payload, created_at = datetime.now())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# Delete all events
@app.delete("/delete_events/", description="Delete all Events")
def delete_events(db: Session = Depends(get_db)):
    db.query(models.Event).delete()
    db.commit()
    return {"message": "All events deleted"}
    
@app.get("/agents", response_class=HTMLResponse)
def get_html():
    return HTMLResponse(open("./chatcollab/timeline/templates/agents.html").read())

@app.get("/timeline", response_class=HTMLResponse)
def get_html_timeline():
    return HTMLResponse(open("./chatcollab/timeline/templates/timeline.html").read())

# Read openai logs and return
@app.get("/openai_logs")
def get_openai_logs():
    try:
        # Read existing data
        with open(filename_openai_log, "r") as file:
            data = json.load(file)

            # Return new json with total number of logs, and frequency of logs for each represented hour and date
            total_logs = len(data)
            frequency = {}
            for log in data:
                date = log["timestamp"].split("T")[0]
                hour = log["timestamp"].split("T")[1].split(":")[0]
                if date not in frequency:
                    frequency[date] = {}
                if hour not in frequency[date]:
                    frequency[date][hour] = 1
                else:
                    frequency[date][hour] += 1
            data = {"total_number_of_logs":total_logs, "frequency":frequency}
    except FileNotFoundError:
        data = {"error":"No logs found"}
    
    return data