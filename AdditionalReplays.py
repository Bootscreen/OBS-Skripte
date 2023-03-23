
#!/usr/bin/env python
# title             : AdditionalReplays.py
# description       : Adds 3 \"additional\" ReplayBuffer.
# author            : Bootscreen
# date              : 2019 05 11
# version           : 0.2.1
# dependencies      : - Python 3.6 (https://www.python.org/ or https://www.python.org/ftp/python/3.6.0/python-3.6.0-amd64-webinstall.exe)
# notes             : Follow this step for this script to work:
#                   : Python:
#                   :   1. Install python (v3.6 and 64 bits, this is important)
#                   :   2. Install moviepy (pip install moviepy)
#                   : OBS:
#                   :   1. Go to Tools › Scripts
#                   :   2. Click the "Python Settings" tab
#                   :   3. Select your python install path
#                   :   4. Click the "Scripts" tab
#                   :   5. Click the "+" button and add this script
#                   :   6. Set the seconds and where it should be saved
#                   :   7. Set Hotkeys in OBS Settings
#                   :   8. Check "Enable"
#                   :
# python_version    : 3.6+
# ==============================================================================

import obspython as obs
import os, sys, subprocess, time
from time import sleep
from shutil import copyfile 
from importlib import util 
from datetime import datetime

enabled = True
debug_mode = False
replay1_hotkey = obs.OBS_INVALID_HOTKEY_ID
replay1_seconds = 5
replay1_path = ""
replay1_remove = True
replay1_from_end = False
replay2_hotkey = obs.OBS_INVALID_HOTKEY_ID
replay2_seconds = 10
replay2_path = ""
replay2_remove = True
replay2_from_end = False
replay3_hotkey = obs.OBS_INVALID_HOTKEY_ID
replay3_seconds = 15
replay3_path = ""
replay3_remove = True
replay3_from_end = False

def file_in_use(fpath):
    if os.path.exists(fpath):
        try:
            os.rename(fpath, fpath)
            return False
        except:
            return True
    
def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    if "get_setting" not in sys.modules:
        from moviepy.config import get_setting
    if "get_setting" not in sys.modules:
        from moviepy.tools import subprocess_call
    """ Makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name, ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000*t) for t in [t1, t2]]
        targetname = "%sSUB%d_%d.%s" % (name, T1, T2, ext)
    
    cmd = [get_setting("FFMPEG_BINARY"),"-y",
           "-ss", "%0.2f"%t1,
           "-i", filename,
           "-t", "%0.2f"%(t2-t1),
           "-vcodec", "copy", "-acodec", "copy", targetname]
    
    if debug_mode:
        subprocess_call(cmd)
    else:
        subprocess_call(cmd, None)
    
def check_and_install_package(package):
    if not check_package(package):
        install_package(package)
        
def check_package(package):
    if util.find_spec(package) is None:
        return False
    else:
        return True
        
def install_package(package):
    global debug_mode
    if debug_mode: 
        print("[AR] install_package: " + package)
    python_path = os.path.join(sys.prefix ,"python.exe")
    subprocess.call([python_path , "-m", "pip", "install", package])
    
def upgrade_package(package):
    global debug_mode
    if debug_mode: 
        print("[AR] upgrade_package: " + package)
    python_path = os.path.join(sys.prefix ,"python.exe")
    subprocess.call([python_path , "-m", "pip", "install", "-U", package])
    
def install_needed(prop, props):
    global debug_mode
    if debug_mode: 
        print("[AR] install_needed")
    install_package("moviepy")
    upgrade_package("imageio")
    upgrade_package("numpy")
    from moviepy.config import get_setting
    from moviepy.tools import subprocess_call
    from moviepy.editor import VideoFileClip

def save_and_get_last_replay():
    timestamp = time.time()
    obs.obs_frontend_replay_buffer_save()

    # Try to get the file timestamp 20 times, only then give up, interval 1 sec
    for i in range(20):
        path = get_last_replay()
        if path and os.path.isfile(path):
            file_timestamp = os.path.getctime(path)
            if file_timestamp < timestamp:
                path = None
            else:
                break
        sleep(1)

    return path

def get_last_replay():
    replay_buffer = obs.obs_frontend_get_replay_buffer_output()
    cd = obs.calldata_create()
    ph = obs.obs_output_get_proc_handler(replay_buffer)
    obs.proc_handler_call(ph, "get_last_replay", cd)
    path = obs.calldata_string(cd, "path")
    obs.calldata_destroy(cd)
    obs.obs_output_release(replay_buffer)
    return path
    
def save_replay1(pressed):
    if pressed and enabled:
        save_replay(replay1_seconds, replay1_path, replay1_remove, replay1_from_end)
    
def save_replay2(pressed):
    if pressed and enabled:
        save_replay(replay2_seconds, replay2_path, replay2_remove, replay2_from_end)
    
def save_replay3(pressed):
    if pressed and enabled:
        save_replay(replay3_seconds, replay3_path, replay3_remove, replay3_from_end)
    
def save_replay(seconds, new_path, remove, from_end):
    global debug_mode
    if debug_mode: 
        print("[AR] save_replay")
        print("[AR] seconds=" + str(seconds) )
        print("[AR] path=" + new_path)
        print("[AR] remove=%s" %(remove))
        print("[AR] from_end=%s" %(from_end))
        
    if not enabled:
        return
        
    if obs.obs_frontend_replay_buffer_active() is False:
        if debug_mode: print("[AR] replaybuffer not active")
        return
    
    if seconds > 0:
        if "VideoFileClip" not in sys.modules:
            from moviepy.config import get_setting
            from moviepy.tools import subprocess_call
            from moviepy.editor import VideoFileClip
        
        last_replay = save_and_get_last_replay()
        if last_replay is not None and len(last_replay) > 0:
            if debug_mode: 
                print("[AR] last_replay=" + last_replay)
                
            last_replay_folder = os.path.dirname(os.path.abspath(last_replay))
            last_replay_name, last_replay_type = os.path.splitext(os.path.basename(last_replay))
            
            if len(new_path) <= 0 or not os.path.exists(new_path):
                new_path = last_replay_folder
            
            if debug_mode: 
                print("[AR] last_replay_folder=" + last_replay_folder)
                print("[AR] last_replay_name=" + last_replay_name)
                print("[AR] last_replay_type=" + last_replay_type)
                print("[AR] new_path=" + new_path)
                
            if last_replay_folder == new_path:
                new_replay = os.path.join(new_path, last_replay_name + "_" + seconds + "s" + last_replay_type)
            else:
                new_replay = os.path.join(new_path, last_replay_name + last_replay_type)
               
            if debug_mode: 
                print("[AR] last_replay=" + last_replay)
                print("[AR] new_replay=" + new_replay)
            
            clip = VideoFileClip(last_replay)
            duration = clip.duration
            
            if duration > seconds:
                if from_end:
                    if debug_mode: print("[AR] from_end")
                    ffmpeg_extract_subclip(last_replay, duration - seconds, duration, targetname=new_replay)
                else:
                    if debug_mode: print("[AR] from_begin")
                    ffmpeg_extract_subclip(last_replay, 0, seconds, targetname=new_replay)
            else:
                copyfile(last_replay, new_replay)
                
            clip.reader.close()
            if clip.audio and clip.audio.reader:
                clip.audio.reader.close_proc()
            del clip.reader
            del clip
            
            if remove and os.path.exists(new_replay):
                try:
                    if debug_mode: print("[AR] try remove")
                    for x in range(10):
                        if not file_in_use(last_replay):
                            break
                        if debug_mode: print("[AR] file not writeable, wait 0.5 seconds")
                        sleep(0.5)
                    if debug_mode: print("[AR] delete file:" + last_replay)
                    os.remove(last_replay)
                except:
                    print("[AR] error ", sys.exc_info()[0], " on remove : ", last_replay)
                    
def script_defaults(settings):
    global global_settings
    global debug_mode
    if debug_mode: print("[AR] Loaded defaults.")
    
    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_bool(settings, "debug_mode", debug_mode)
    obs.obs_data_set_default_int(settings, "replay1_seconds", replay1_seconds)
    obs.obs_data_set_default_int(settings, "replay2_seconds", replay2_seconds)
    obs.obs_data_set_default_int(settings, "replay3_seconds", replay3_seconds)
    obs.obs_data_set_default_bool(settings, "replay1_remove", replay1_remove)
    obs.obs_data_set_default_bool(settings, "replay2_remove", replay2_remove)
    obs.obs_data_set_default_bool(settings, "replay3_remove", replay3_remove)
    obs.obs_data_set_default_bool(settings, "replay1_from_end", replay1_from_end)
    obs.obs_data_set_default_bool(settings, "replay2_from_end", replay2_from_end)
    obs.obs_data_set_default_bool(settings, "replay3_from_end", replay3_from_end)
    
def script_description():
    return "Adds 3 \"additional\" ReplayBuffer. In reality, it saves the normal replaybuffer and clip the seconds from begin or end.<br/>" +\
    "The seconds should be lesser then the whole replay buffer from obs, otherwise the replay is only copied.<br/>" +\
    "When you leave the Path empty, the path of the orginial replay is used and the seconds were attached at the end." + \
    "<hr/>"
    
def script_properties():
    global debug_mode
    if debug_mode: print("[AR] Loaded properties.")
    
    props = obs.obs_properties_create()
    if not check_package("moviepy"):
        obs.obs_properties_add_button(props, "install_libs", "installs moviepy with pip", install_needed)
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    obs.obs_properties_add_bool(props, "debug_mode", "Debug Mode")
    obs.obs_properties_add_int(props, "replay1_seconds", "Replay 1 seconds", 1, 600, 1 )
    obs.obs_properties_add_path(props, "replay1_path", "Path where the Replays should be saved", obs.OBS_PATH_DIRECTORY, "", None )
    obs.obs_properties_add_bool(props, "replay1_remove", "Remove original Replay?")
    obs.obs_properties_add_bool(props, "replay1_from_end", "From End instead of Begin?")
    obs.obs_properties_add_int(props, "replay2_seconds", "Replay 2 seconds", 1, 600, 1 )
    obs.obs_properties_add_path(props, "replay2_path", "Path where the Replays should be saved", obs.OBS_PATH_DIRECTORY, "", None )
    obs.obs_properties_add_bool(props, "replay2_remove", "Remove original Replay?")
    obs.obs_properties_add_bool(props, "replay2_from_end", "From End instead of Begin?")
    obs.obs_properties_add_int(props, "replay3_seconds", "Replay 3 seconds", 1, 600, 1 )
    obs.obs_properties_add_path(props, "replay3_path", "Path where the Replays should be saved", obs.OBS_PATH_DIRECTORY, "", None )
    obs.obs_properties_add_bool(props, "replay3_remove", "Remove original Replay?")
    obs.obs_properties_add_bool(props, "replay3_from_end", "From End instead of Begin?")

    return props

def script_save(settings):
    global debug_mode
    if debug_mode: print("[AR] Saved properties.")
    
    script_update(settings)

def script_load(settings):
    global debug_mode
    global replay1_hotkey
    global replay2_hotkey
    global replay3_hotkey
    
    if debug_mode: 
        print("[AR] Loaded script .")
        print("[AR] moviepy version: " + moviepy.__version__)
        print("[AR] imageio version: " + imageio.__version__)
        print("[AR] numpy version: " + numpy.__version__)
    
    replay1_hotkey = obs.obs_hotkey_register_frontend("additional_replays.replay1", "Replay 1", save_replay1)
    hotkey_save_array = obs.obs_data_get_array(settings, "additional_replays.replay1")
    obs.obs_hotkey_load(replay1_hotkey, hotkey_save_array)
    obs.obs_data_array_release(hotkey_save_array)
    
    replay2_hotkey = obs.obs_hotkey_register_frontend("additional_replays.replay2", "Replay 2", save_replay2)
    hotkey_save_array = obs.obs_data_get_array(settings, "additional_replays.replay2")
    obs.obs_hotkey_load(replay2_hotkey, hotkey_save_array)
    obs.obs_data_array_release(hotkey_save_array)
    
    replay3_hotkey = obs.obs_hotkey_register_frontend("additional_replays.replay3", "Replay 3", save_replay3)
    hotkey_save_array = obs.obs_data_get_array(settings, "additional_replays.replay3")
    obs.obs_hotkey_load(replay3_hotkey, hotkey_save_array)
    obs.obs_data_array_release(hotkey_save_array)
    
    script_update(settings)
    
def script_unload():
    global debug_mode
    if debug_mode: print("[AR] Unloaded script.")
    
    obs.obs_hotkey_unregister(save_replay1)

def script_update(settings):
    global debug_mode
    if debug_mode: print("[AR] Updated properties.")
    
    global enabled
    global replay1_path
    global replay1_remove
    global replay1_from_end
    global replay1_seconds
    global replay2_path
    global replay2_remove
    global replay2_from_end
    global replay2_seconds
    global replay3_path
    global replay3_remove
    global replay3_from_end
    global replay3_seconds
            
    debug_mode = obs.obs_data_get_bool(settings, "debug_mode")
    enabled = obs.obs_data_get_bool(settings, "enabled")
    
    replay1_path = obs.obs_data_get_string(settings, "replay1_path")
    replay1_remove = obs.obs_data_get_bool(settings, "replay1_remove")
    replay1_from_end = obs.obs_data_get_bool(settings, "replay1_from_end")
    replay1_seconds = obs.obs_data_get_int(settings, "replay1_seconds")
    hotkey_save_array = obs.obs_hotkey_save(replay1_hotkey)
    obs.obs_data_set_array(settings, "additional_replays.replay1", hotkey_save_array)
    obs.obs_data_array_release(hotkey_save_array)
    
    replay2_path = obs.obs_data_get_string(settings, "replay2_path")
    replay2_remove = obs.obs_data_get_bool(settings, "replay2_remove")
    replay2_from_end = obs.obs_data_get_bool(settings, "replay2_from_end")
    replay2_seconds = obs.obs_data_get_int(settings, "replay2_seconds")
    hotkey_save_array = obs.obs_hotkey_save(replay2_hotkey)
    obs.obs_data_set_array(settings, "additional_replays.replay2", hotkey_save_array)
    obs.obs_data_array_release(hotkey_save_array)
    
    replay3_path = obs.obs_data_get_string(settings, "replay3_path")
    replay3_remove = obs.obs_data_get_bool(settings, "replay3_remove")
    replay3_from_end = obs.obs_data_get_bool(settings, "replay3_from_end")
    replay3_seconds = obs.obs_data_get_int(settings, "replay3_seconds")
    hotkey_save_array = obs.obs_hotkey_save(replay3_hotkey)
    obs.obs_data_set_array(settings, "additional_replays.replay3", hotkey_save_array)
    obs.obs_data_array_release(hotkey_save_array)

