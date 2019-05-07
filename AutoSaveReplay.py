#!/usr/bin/env python
# title             : AutoSaveReplay.py
# description       : Saves continously Replays
# author            : Bootscreen
# date              : 2019 05 07
# version           : 0.1
# dependencies      : - Python 3.6 (https://www.python.org/)
# notes             : Follow this step for this script to work:
#                   : Python:
#                   :   1. Install python (v3.6 and 64 bits, this is important)
#                   : OBS:
#                   :   1. Go to Tools › Scripts
#                   :   2. Click the "Python Settings" tab
#                   :   3. Select your python install path
#                   :   4. Click the "Scripts" tab
#                   :   5. Click the "+" button and add this script
#                   :   6. Set the Timespan between Replays
#                   :   7. (optional: set Scenes on which no Replays should be saved)
#                   :   8. Check "Enable"
#                   :
# python_version    : 3.6+
# ==============================================================================

import obspython as obs
import os, time, datetime, codecs, win32gui, win32process, win32api, win32con

enabled = True
debug_mode = False
timer_minutes = 10
timer_minutes_to_millisec = 60000
scenes = ''



def script_defaults(settings):
    global debug_mode
    if debug_mode: print("Calling defaults")
    
    global enabled
    global timer_minutes
    global scenes

    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_int(settings, "timer", timer_minutes)
    obs.obs_data_set_default_string(settings, "scenes", scenes)

def script_description():
    return "<b>Starts a continous timer after which a replay is saved<br/></b>" + \
        "<hr>"
    
def script_properties():
    global debug_mode
    if debug_mode: print("[ASR] Loaded properties.")
    
    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    obs.obs_properties_add_bool(props, "debug_mode", "Debug Mode")
    obs.obs_properties_add_int(props, "timer", "Timer (Minutes)", 1, 120, 1 )
    obs.obs_properties_add_text(props, "scenes", "Scenes on which no replay is saved", obs.OBS_TEXT_MULTILINE )
    return props

def script_save(settings):
    global debug_mode
    if debug_mode: print("[ASR] Saved properties.")
    
    script_update(settings)

def script_load(settings):
    global debug_mode
    if debug_mode: print("[ASR] Loaded script.")
    
    global timer_minutes
    timer_minutes = obs.obs_data_get_int(settings, "timer")
    obs.timer_remove(save_replay)
    obs.timer_add(save_replay, timer_minutes * timer_minutes_to_millisec)
    
def script_unload():
    global debug_mode
    if debug_mode: print("[ASR] Unloaded script.")
    
    obs.timer_remove(save_replay)

def script_update(settings):
    global debug_mode
    if debug_mode: print("[ASR] Updated properties.")
    
    global enabled
    global scenes
    global timer_minutes
            
            
    debug_mode = obs.obs_data_get_bool(settings, "debug_mode")
    scenes = obs.obs_data_get_string(settings, "scenes")
    timer_minutes = obs.obs_data_get_int(settings, "timer")
    
    currentScene = obs.obs_frontend_get_current_scene()
    sceneName = obs.obs_source_get_name(currentScene)
    
    if obs.obs_data_get_bool(settings, "enabled") is True:
        enabled = True
        obs.timer_remove(save_replay)
        obs.timer_add(save_replay, timer_minutes * timer_minutes_to_millisec)
    else:
        enabled = False
        obs.timer_remove(save_replay)

def save_replay():
    global debug_mode
    if debug_mode: print("[ASR] save_replay.")
    
    if obs.obs_frontend_replay_buffer_active() is True:
        if len(scenes) > 0:
            currentScene = obs.obs_frontend_get_current_scene()
            sceneName = obs.obs_source_get_name(currentScene)
            if sceneName not in scenes:
                obs.obs_frontend_replay_buffer_save()
                if debug_mode: print("[ASR] saved Replay.")
        else:
            obs.obs_frontend_replay_buffer_save()
            if debug_mode: print("[ASR] saved Replay without scene restriction.")
            