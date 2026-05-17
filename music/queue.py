# music/queue.py

from collections import defaultdict
from typing import Dict, List, Any

# Queue Storage
QUEUE: Dict[int, List[dict]] = defaultdict(list)

# Current Playing Storage
CURRENT: Dict[int, dict] = {}


def add_to_queue(chat_id: int, song_data: dict):
    """
    Add song to queue
    """
    QUEUE[chat_id].append(song_data)


def get_queue(chat_id: int):
    """
    Get full queue
    """
    return QUEUE.get(chat_id, [])


def pop_queue(chat_id: int):
    """
    Remove first song from queue
    """
    if QUEUE.get(chat_id):
        return QUEUE[chat_id].pop(0)
    return None


def clear_queue(chat_id: int):
    """
    Clear queue
    """
    QUEUE[chat_id] = []
    CURRENT.pop(chat_id, None)


def queue_length(chat_id: int):
    """
    Queue count
    """
    return len(QUEUE.get(chat_id, []))


def is_queue_empty(chat_id: int):
    """
    Check queue empty
    """
    return len(QUEUE.get(chat_id, [])) == 0


def set_current(chat_id: int, song_data: dict):
    """
    Set current playing
    """
    CURRENT[chat_id] = song_data


def get_current(chat_id: int):
    """
    Get current playing
    """
    return CURRENT.get(chat_id)


def clear_current(chat_id: int):
    """
    Clear current playing
    """
    CURRENT.pop(chat_id, None)


def has_active_player(chat_id: int):
    """
    Check if something playing
    """
    return chat_id in CURRENT


def format_queue(chat_id: int):
    """
    Beautiful queue text
    """
    queue = get_queue(chat_id)

    if not queue:
        return "📭 Queue is empty."

    text = "📜 **Music Queue:**\n\n"

    for index, song in enumerate(queue, start=1):
        title = song.get("title", "Unknown")
        requested_by = song.get("requested_by", "Unknown")

        text += (
            f"**{index}.** {title}\n"
            f"┗ 👤 Requested by: {requested_by}\n\n"
        )

    return text