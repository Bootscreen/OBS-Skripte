#!/usr/bin/env python
# title             : AutoSaveReplay.py
# description       : Saves continously Replays
# author            : Bootscreen
# date              : 2019 05 11
# version           : 0.1
# dependencies      : - Python 3.6 (https://www.python.org/)
# notes             : Follow this step for this script to work:
#                   : Python:
#                   :   1. Install python (v3.6 and 64 bits, this is important)
#                   :   2. Install python-twitch-client (python -m pip install python-twitch-client)
#                   : OBS:
#                   :   1. Go to Tools › Scripts
#                   :   2. Click the "Python Settings" tab
#                   :   3. Select your python install path
#                   :   4. Click the "Scripts" tab
#                   :   5. Click the "+" button and add this script
#                   :   6. Set the Timespan between Scene Checks
#                   :   7. Modify Scene List
#                   :   8. Check "Enable"
#                   :
# python_version    : 3.6+
# ==============================================================================

import obspython as obs
import os, sys, importlib

def check_and_install_package(package):
    if not check_package(package):
        install_package(package)
        
def check_package(package):
    if importlib.util.find_spec(package) is None:
        return False
    else:
        return True
        
def install_package(package):
    python_path = os.path.join(sys.prefix ,"python.exe")
    subprocess.call([python_path , "-m", "pip", "install", package])
    
def install_needed(prop, props):
    install_package("twitch")
    from twitch import TwitchClient

enabled = True
live = True
debug_mode = False
check_frequency = 1
check_frequency_to_millisec = 1000
twitch_settings = None
client_id = ''
oauth_token = ''
last_scene = ''
t_client = None


def script_defaults(settings):
    global debug_mode
    if debug_mode: print("[TS] Loaded defaults.")
    
    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_bool(settings, "debug_mode", debug_mode)
    obs.obs_data_set_default_bool(settings, "live", live)
    obs.obs_data_set_default_int(settings, "check_frequency", check_frequency)
    obs.obs_data_set_default_string(settings, "oauth_token", oauth_token)
    obs.obs_data_set_default_string(settings, "client_id", client_id)
    
    obs_twitch = obs.obs_data_get_array(settings, "twitch")
    if obs.obs_data_array_count(obs_twitch) <= 0:
        push_scenes_to_list(settings)
    obs.obs_data_array_release(obs_twitch)
    
def script_description():
    return "<b>Change Twitch Game and Title on active Scene</b>" + \
    "<hr/>" + \
    "Create your Client-ID here:<br/><a href=\"https://dev.twitch.tv/console/apps/create\">Twitch Dev</a>" + \
    "<br/>" + \
    "Create yout Oauth-Token here (you need channel_read and channel_editor permission):<br/><a href=\"https://twitchtokengenerator.com/quick/8hkFXMYaO0\">twitchtokengenerator.com</a>" + \
    "<hr/>"
    
def script_properties():
    global debug_mode
    if debug_mode: print("[TS] Loaded properties.")
    
    props = obs.obs_properties_create()
    if not check_package("twitch"):
        obs.obs_properties_add_button(props, "install_libs", "installs twitch python client with pip", install_needed)
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    obs.obs_properties_add_bool(props, "debug_mode", "Debug Mode")
    obs.obs_properties_add_bool(props, "live", "Only Live")
    obs.obs_properties_add_int(props, "check_frequency", "Check Frequence (Secounds)", 1, 600, 1 )
    obs.obs_properties_add_text(props, "client_id", "Client ID", obs.OBS_TEXT_DEFAULT )
    obs.obs_properties_add_text(props, "oauth_token", "Oauth Token", obs.OBS_TEXT_DEFAULT )
    obs.obs_properties_add_editable_list(props, "twitch", "List of Scenes;Games;Title which should set", obs.OBS_EDITABLE_LIST_TYPE_STRINGS, "", "")

    return props

def script_save(settings):
    global debug_mode
    if debug_mode: print("[TS] Saved properties.")
    
    script_update(settings)

def script_load(settings):
    global debug_mode
    global twitch_settings
    global check_frequency
    
    if debug_mode: print("[TS] Loaded script.")
    
    check_frequency = obs.obs_data_get_int(settings, "check_frequency")
    obs.timer_remove(set_twitch)
    if len(oauth_token) > 0 and len(client_id) > 0:
        obs.timer_add(set_twitch, check_frequency * check_frequency_to_millisec)
        
    twitch_settings = obs.obs_frontend_get_scene_names()
    
def script_unload():
    global debug_mode
    if debug_mode: print("[TS] Unloaded script.")
    
    obs.timer_remove(set_twitch)

def script_update(settings):
    global debug_mode
    if debug_mode: print("[TS] Updated properties.")
    
    global enabled
    global scenes
    global check_frequency
    global client_id
    global oauth_token
    global twitch_settings
    global live
            
    live = obs.obs_data_get_bool(settings, "live")
    debug_mode = obs.obs_data_get_bool(settings, "debug_mode")
    check_frequency = obs.obs_data_get_int(settings, "check_frequency")
    client_id = obs.obs_data_get_string(settings, "client_id")
    oauth_token = obs.obs_data_get_string(settings, "oauth_token")
    
    obs_twitch = obs.obs_data_get_array(settings, "twitch")
    num_twitch = obs.obs_data_array_count(obs_twitch)
    twitch_settings = []
    for i in range(num_twitch):  # Convert C array to Python list
        message_object = obs.obs_data_array_item(obs_twitch, i)
        twitch_settings.append(obs.obs_data_get_string(message_object, "value"))
    obs.obs_data_array_release(obs_twitch)
    
    if obs.obs_data_get_bool(settings, "enabled") is True:
        enabled = True
        obs.timer_remove(set_twitch)
        if len(oauth_token) > 0 and len(client_id) > 0:
            obs.timer_add(set_twitch, check_frequency * check_frequency_to_millisec)
    else:
        enabled = False
        obs.timer_remove(set_twitch)

def get_current_scene():    
    currentScene = obs.obs_frontend_get_current_scene()
    return obs.obs_source_get_name(currentScene)

def push_scenes_to_list(settings):
    scenes = obs.obs_frontend_get_scene_names()
    obs_array = obs.obs_data_array_create()
    for scene in scenes:
        item = obs.obs_data_create()
        obs.obs_data_set_string(item, "value", scene)
        obs.obs_data_array_push_back(obs_array, item)    
        obs.obs_data_release(item)
        
    obs.obs_data_set_array(settings, "twitch", obs_array)
    obs.obs_data_array_release(obs_array)
    
def set_twitch():
    global debug_mode
    global t_client
    global last_scene
    
    if debug_mode: print("[TS] set_twitch.")
    
    current_scene = get_current_scene()
    
    if live is True and obs.obs_frontend_streaming_active() is False:
        if debug_mode: print("[TS] must be live(",live,"), but is not live (",obs.obs_frontend_streaming_active(),")")
        last_scene = current_scene
        return
                
    if current_scene is not None and current_scene != last_scene:
        scene_settings = [i for i in twitch_settings if i.startswith(current_scene)]
        if len(scene_settings) > 0 and scene_settings[0].count(";") >= 2:
            scene, game, title = scene_settings[0].split(";",2)
            
                
            if len(oauth_token) <= 0 or len(client_id) <= 0:
                print("[TS]  len(oauth_token): " +  len(oauth_token))
                print("[TS]  len(client_id): " +  len(client_id))
                last_scene = current_scene
                return
                
            if t_client is None:
                if "TwitchClient" not in sys.modules:
                    from twitch import TwitchClient
                t_client = TwitchClient(client_id,oauth_token)
                
            channel = t_client.channels.get()
            if channel.game != game or channel.status != title:
                t_client.channels.update(channel.id, title, game, 0, False)
                if debug_mode: 
                    print("[TS] Title: " + title)
                    print("[TS] Game: " + game)
                    print("[TS] Twitch was updated")

            
    last_scene = current_scene