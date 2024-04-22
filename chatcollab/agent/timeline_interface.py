import requests
from datetime import datetime
import re
from datetime import timedelta

public_key = "placeholder"
private_key = "placeholder"

def validate_datetime_string(dt_str):
    # Regular expression for matching the format 'YYYY-MM-DDTHH:MM:SS.ssssss'
    pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}'

    # Check if the string matches the pattern
    if re.match(pattern, dt_str):
        try:
            # Try parsing the datetime to ensure it's valid
            datetime.fromisoformat(dt_str)
        except ValueError:
            # If parsing fails, the format is incorrect
            print(f"The datetime string is incorrectly formatted: {dt_str}")
            raise ValueError(f"The datetime string is incorrectly formatted.")
    else:
        print(f"The datetime string does not match the required pattern: {dt_str}")
        raise ValueError(f"The datetime string does not match the required pattern.")


def get_timeline_events(n: int = None, start: str = None, end: str = None):
    """
    Get a list of events from the timeline.
    
    Args (optional):
        n: The number of events to get
        start: The start time of the events to get
        end: The end time of the events to get
    
    Returns:
        A list of events from the timeline.
    """

    if start:
        validate_datetime_string(start)
    
    if end:
        validate_datetime_string(end)

    
    url = f"http://localhost:8000/list_events/?public_key={public_key}&private_key={private_key}"

    r = requests.get(url)
    r = r.json()

    # Add print statement for debugging
    if start:
        print(f"DEBUG: start: {start}")
        # print events
        for event in r:
            print(event['created_at'])
        print("----")

    # Filter the events based on start and end times if they are provided
    if start:
        r = [event for event in r if event['created_at'] >= start]
    if end:
        r = [event for event in r if event['created_at'] <= end]
    
    # Return the last n events if n is provided
    if n:
        return r[-int(n):]
    else:
        return r


def clear_timeline():
    """
    Clear the timeline.
    """
    # Make DELETE request to /delete_events/
    url = f"http://localhost:8000/delete_events/"

    # make delete request
    r = requests.delete(url)
    
    return 


def post_timeline_event(title: str, payload: str, tags: [str], new_public_key:str = None, new_private_key:str = None):
    """
    Post a new event to the timeline.
    
    Args:
        title: The title of the event
        payload: The payload of the event
        tags: A list of tags associated with the event
    
    Returns:
        The event that was posted.
    """

    if new_public_key and new_private_key:
        url = f"http://localhost:8000/create_event/?public_key={new_public_key}&private_key={new_private_key}"
    else:
        url = f"http://localhost:8000/create_event/?public_key={public_key}&private_key={private_key}"

    # make post request
    r = requests.post(url, json={"title": title, "payload": payload, "tags": tags})
    r = r.json()

    return r


def filter_events_by_tag(tag:str, events: [dict]):
    """
    Filter events by tag.

    Args:
        tag: The tag to filter by
        events: The list of events to filter

    Returns:
        A list of events that have the specified tag
    """

    return [event for event in events if tag in event['tags']]

def update_institutional_knowledge(knowledge):
    """
    Add new institutional knowledge to the timeline.

    Args:
        knowledge: The new institutional knowledge
    
    """

    post_timeline_event(title="Institutional Knowledge", payload=knowledge, tags=["type:data"])

    return


def get_institutional_knowledge(events: [dict]):
    """
    Get the institutional knowledge from the timeline.

    Args:
        events: The list of events to search
    
    Returns:
        The institutional knowledge
    """

    knowledge = get_payload_of_most_recent_event_matching_title(title="Institutional Knowledge", events=events)
    
    print("DEBUG: knowledge: ", knowledge)

    return knowledge

def get_payload_of_most_recent_event_matching_title(title: str, events: [dict]):
    """
    Get the payload of the most recent event matching a title.

    Args:
        title: The title to match
        events: The list of events to search

    Returns:
        The payload of the most recent event matching the title
    """

    # Filter the events by title
    events = [event for event in events if event['title'] == title]

    if len(events)==0:
        print(f"No events found matching title: {title}")
        return ""

    # Return the payload of the most recent event
    return events[-1]['payload']


def get_timestamp_x_minutes_ago(minutes: int):
    """
    Get a timestamp from x minutes ago.

    Args:
        minutes: The number of minutes ago

    Returns:
        A timestamp from x minutes ago.
    """

    # Get the current time
    now = datetime.now()

    # Get the time x minutes ago
    delta = now - timedelta(minutes=minutes)

    # Return the timestamp
    return delta.isoformat()

def filter_relevant_events():
    pass