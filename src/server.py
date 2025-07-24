

import reapy
import asyncio
import os 

from model import EQSettings, CompressorSettings, ReverbSettings, DelaySettings
from typing import Any
from mcp.server.fastmcp import FastMCP
from langchain_chroma import Chroma
from model.qdrant import QdrantVectorStore
from langchain_community.embeddings import FastEmbedEmbeddings

embedding = FastEmbedEmbeddings()

reapy.connect()
project = reapy.Project() 

mcp = FastMCP("Track Management Server")

ATTR_TRACK = ["D_VOL", "D_PAN", "D_WIDTH"]

DB_PATH = os.getenv("DB_PATH")

@mcp.tool()
async def set_track_volume(track_name: str, current_volume: float, db_change: float) -> str:
    """
    Adjust the track's volume by a given amount in decibels (dB).

    The volume is stored in linear format internally, but this function allows you
    to increase or decrease it using intuitive dB values.

    Args:
        track_name (str): Name of the track to modify.
        current_volume (float): Current track volume in linear scale (e.g., 1.0 = 0 dB).
        db_change (float): Desired volume change in decibels. 
                           Positive values increase the volume, negative reduce it.

    Returns:
        str: A message summarizing the volume adjustment in dB.
    """
    import math

    multiplier = math.pow(10, db_change / 20)
    new_volume = current_volume * multiplier

    # Clamp between 0.0 and 4.0 to prevent clipping
    new_volume = min(max(new_volume, 0.0), 4.0)

    track = project._get_track_by_name(track_name)
    track.set_info_value("D_VOL", new_volume)
    return f"Volume changed by {db_change:+.2f} dB"


@mcp.tool()
async def set_track_pan(track_name: str, current_pan: float, pan_change: float) -> str:
    """
    Adjusts the stereo pan of a specific track in the project.

    Panning determines the position of a track in the stereo field:
    - A value of -1.0 is fully left.
    - A value of  0.0 is center.
    - A value of +1.0 is fully right.

    This function modifies the pan by a specified change (`pan_change`), which is a float value:
    - Positive values pan the track more to the right.
    - Negative values pan the track more to the left.

    The final pan value is clamped to stay within the range [-1.0, 1.0].

    Args:
        track_name (str): The name of the track to update.
        current_pan (float): The current pan value of the track (between -1.0 and 1.0).
        pan_change (float): The desired change to apply to the pan value 
                            (positive for right, negative for left).

    Returns:
        str: A message summarizing the pan adjustment in percentage terms.
    """

    # Clamp the new pan value to stay within valid range
    new_pan = max(-1.0, min(1.0, current_pan + pan_change))

    track = project._get_track_by_name(track_name)
    track.set_info_value("D_PAN", new_pan)

    return f"Pan adjusted by {pan_change * 100:+.2f}%. New pan: {new_pan:.2f}"


@mcp.tool()
async def set_track_FX(track_name: str, new_settings: EQSettings | CompressorSettings | ReverbSettings | DelaySettings  , fx_name: str) -> str :
    """
    Set parameters of a specific audio FX on a given track. If the FX is not already present on the track, it will be added.

    The `new_settings` argument must correspond to the type of FX specified by `fx_name`:

    - For `fx_name="ReaEQ"`: use an `EQSettings` object with fields like:
        - `gain_low_shelf`, `gain_band_2`, `gain_band_3`, `gain_high_shelf_4`
        - `freq_high_pass_5`
        These control the gain and frequency of various EQ bands in a parametric equalizer.

    - For `fx_name="ReaComp"`: use a `CompressorSettings` object with fields such as:
        - `threshold`, `ratio`, `attack`, `release`, `dry`, `wet`
        These are standard parameters for a dynamic compressor.

    - For `fx_name="ReaVerbate"`: pass a dictionary or dedicated model (if defined) with keys like:
        - `wet`, `dry`, `pre_verb`, `width`, `pan`, `bypass`, etc.
        These control the amount and behavior of reverb applied to the track.
     - For `fx_name="ReaDealay"`: pass a dictionary or dedicated model (if defined) with keys like:
        - `wet`, `dry`, `pre_verb`, `width`, `pan`, `bypass`, etc.
        These control the amount and behavior of reverb applied to the track.

    - For `fx_name="ReaDelay"`: pass a dictionary or dedicated model (if defined) with keys like:
        - `wet`, `dry`, `enabled`, `length_time`, `length_musical`, `feedback`, `lowpass`, `hipass`, 
        `resolution`, `stereo_width`, `volume`, `pan`, `bypass`, `delta`, etc.
        These control the amount, timing, filtering, and spatial characteristics of the delay effect on the track.

    Args:
        track_name (str): Name of the track to modify.
        new_settings (EQSettings | CompressorSettings): The settings to apply, depending on the FX type.
        fx_name (str): The name of the effect plugin (e.g., "ReaEQ", "ReaComp", "ReaVerb").

    Returns:
        str: A summary of the parameters that were updated, or an error message if something went wrong.
    """
  
    track = project._get_track_by_name(track_name)
    messages = []
    fx_found = False
    fx = None
    
    
    for fx_candidate in track.fxs:
        if fx_name in fx_candidate.name:
            fx = fx_candidate
            fx_found = True
            break

    if not fx_found:
        
        fx = track.add_fx(fx_name)
        messages.append(f"FX '{fx_name}' added to track '{track.name}'")

        
    mapping_params_indx = {param.name: idx for idx, param in enumerate(fx.params)}
    
    
    new_settings_dict = new_settings._to_dict()

    for name, val in new_settings_dict.items():
        if name in mapping_params_indx:
            idx = mapping_params_indx[name]
            fx.params[idx] = val
            messages.append(f"{name} is set to {val:.4f}")
        else:
            messages.append(f"Parameter '{name}' not found in FX '{fx.name}'")

    return '/n'.join(messages)

@mcp.tool()
async def get_track_info(track_name: str):
        """
        Retrieve volume, pan, width and FX parameters for the current track.

        Returns:
            dict: Dictionary containing track-level attributes and FX parameters.
        """
        track = project._get_track_by_name(track_name)
        infos = {attr: track.get_info_value(attr) for attr in ATTR_TRACK}

        if track.fxs:
            fxs_dict = {}  
            for fx in track.fxs:
            
                fxs_dict[fx.name] = {param.name : f"{param:.4f} | "
                    f"formatted: {param.formatted} | "
                    f"normalized: {param.normalized:.2f} | "
                    f"range: {param.range}" for param in fx.params}
                
            infos.update(fxs_dict)

        return f"infos on  track {track.name}: {infos}"



@mcp.tool()
async def get_project_info():
        """
        Retrieve volume, pan, width and FX parameters for the current track.

        Returns:
            dict: Dictionary containing track-level attributes and FX parameters.
        """
    
             
        infos = {track.name: await get_track_info(track.name) for track in project.tracks}


        return f"informations on project {project.name}: {infos}"

@mcp.tool()
async def get_information_query_chroma( query:str):
    """
    Retrieve best practices for mixing (EQ, compression, reverb, etc.) from a custom knowledge base.

    This function performs a semantic search in the ChromaDB vector database using a natural language query.
    It is intended to help the agent find relevant advice and techniques for improving audio mixes,
    such as how to apply EQ to vocals, when to use compression, or how to set up reverb.

    Args:
        
        query (str): A natural language question about mixing techniques (e.g. "How to EQ vocals?").

    Returns:
        str: A message indicating how many relevant documents were found in the database.

    Example:
        "What are good EQ settings for vocals?"
        "How to use compression on drums?"
        "Tips for adding reverb to a lead synth"
    """
   
    vector_store = QdrantVectorStore()
    results = vector_store.search_embeddings(query, limit=3)

    return "Advices \n".join([doc.page_content for  doc in results])



if __name__ == "__main__":
    mcp.run()