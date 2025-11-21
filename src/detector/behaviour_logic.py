# src/detectors/behaviour_logic.py
from datetime import datetime
import math

def is_night(hour, cfg):
    ns = cfg.get("cameras", {}).get("night_start", 20)
    ne = cfg.get("cameras", {}).get("night_end", 6)
    if ns > ne:
        return (hour >= ns) or (hour < ne)
    else:
        return (hour >= ns) and (hour < ne)

def group_alert_needed(num_people, stationary_count, cfg, now_hour):
    at_night = is_night(now_hour, cfg)
    group_threshold = cfg.get("people", {}).get("group_threshold", 5)
    return at_night and (num_people >= group_threshold) and (stationary_count > 0)
