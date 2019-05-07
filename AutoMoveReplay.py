#!/usr/bin/env python
# title             : AutoMoveReplay.py
# description       : Moves Replays to another Folder when the Replay Buffer is stopped
# author            : Bootscreen
# date              : 2019 05 07
# version           : 0.1
# dependencies      : - Python 3.6 (https://www.python.org/)
#                   :   - shutil (https://github.com/mhammond/pywin32/releases)
# notes             : Follow this step for this script to work:
#                   : Python:
#                   :   1. Install python (v3.6 and 64 bits, this is important)
#                   : OBS:
#                   :   1. Go to Tools › Scripts
#                   :   2. Click the "Python Settings" tab
#                   :   3. Select your python install path
#                   :   4. Click the "Scripts" tab
#                   :   5. Click the "+" button and add this script
#                   :   6. Set the Destinationpath
#                   :   7. Check "Enable"
#                   :
# python_version    : 3.6+
# ==============================================================================

import obspython as obs
import os, time, datetime, codecs, win32gui, win32process, win32api, win32con
import shutil

enabled = True
debug_mode = False
location_to = ""
location_from = ""
file_type = ""
replay_status = False
check_frequency = 1000

def script_defaults(settings):
    global debug_mode
    if debug_mode: print("Calling defaults")
    
    global enabled
    global location_to

    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_bool(settings, "enabled", debug_mode)
    obs.obs_data_set_default_string(settings, "location_to", "")

def script_description():
    return "<b>Moves the Replays to an other location when the Replaybuffer is stopped<br/></b>" + \
        "<hr>"
    
def script_properties():
    global debug_mode
    if debug_mode: print("[AMR] Loaded properties.")
    
    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    obs.obs_properties_add_bool(props, "debug_mode", "Debug Mode")
    obs.obs_properties_add_text(props, "location_to", "Path where the Replays should be moved", obs.OBS_TEXT_DEFAULT )
    
    return props

def script_save(settings):
    global debug_mode
    if debug_mode: print("[AMR] Saved properties.")
    
    script_update(settings)

def script_load(settings):
    global replay_status
    global debug_mode
    if debug_mode: print("[AMR] Loaded script.")
    
    replay_status = obs.obs_frontend_replay_buffer_active()
    
def script_unload():
    global debug_mode
    if debug_mode: print("[AMR] Unloaded script.")

def script_update(settings):
    global debug_mode
    if debug_mode: print("[AMR] Updated properties.")
    
    global enabled
    global location_to
    global replay_status
            
            
    debug_mode = obs.obs_data_get_bool(settings, "debug_mode")
    location_to = obs.obs_data_get_string(settings, "location_to")
    
    if obs.obs_data_get_bool(settings, "enabled") is True:
        if (not enabled):
            if debug_mode: print("[AMR] Enabled replay status check timer.")

        enabled = True
        obs.timer_remove(check_replay_status)
        obs.timer_add(check_replay_status, check_frequency)
    else:
        if (enabled):
            if debug_mode: print("[AMR] Disabled replay status check timer.")

        enabled = False
        obs.timer_remove(check_replay_status)
        
    replay_status = obs.obs_frontend_replay_buffer_active()

def get_last_replay():
    replay_buffer = obs.obs_frontend_get_replay_buffer_output()
    cd = obs.calldata_create()
    ph = obs.obs_output_get_proc_handler(replay_buffer)
    obs.proc_handler_call(ph, "get_last_replay", cd)
    path = obs.calldata_string(cd, "path")
    obs.calldata_destroy(cd)

    obs.obs_output_release(replay_buffer)
    return path
    
def check_replay_status():
    if not enabled:
        return
        
    global replay_status
    global location_from
    global file_type
    
    global debug_mode
    if debug_mode: print("[AMR] check_replay_status.")
            
    current_status = obs.obs_frontend_replay_buffer_active()
    if current_status is False and replay_status is True:
        if debug_mode: print("[AMR] current_status is False and replay_status is True.")
        if len(location_from) <= 0 or len(file_type) <= 0:
            last_replay = get_last_replay()
            location_from = os.path.dirname(os.path.abspath(last_replay))
            filename, file_type = os.path.splitext(last_replay)
            
        if len(location_from) > 0 and os.path.exists(location_from) and len(location_to) > 0 and os.path.exists(location_to) :
            if debug_mode: print("[AMR] move replays.")
            sourcefiles = os.listdir(location_from)
            destinationpath = 'C:/Users/kevinconnell/Desktop/Test_Folder/Archive'
            for file in sourcefiles:
                if file.endswith(file_type):
                    if debug_mode: print("[AMR] move ." + file)
                    shutil.move(os.path.join(location_from,file), os.path.join(location_to,file))
    
    replay_status = current_status