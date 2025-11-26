"""Export utilities for generating CSV and Markdown outputs.

Handles formatting of moment data for download by editors.
"""

import csv
import io
from typing import List, Dict, Any


def to_csv(moments_with_cuts: List[Dict[str, Any]]) -> str:
    """Convert moments with cut sheets to CSV format.

    Args:
        moments_with_cuts: List of moment dictionaries with editor_cut_sheet data

    Returns:
        CSV string ready for download
    """
    if not moments_with_cuts:
        return ""

    # Build CSV in memory
    output = io.StringIO()

    # Define CSV columns
    fieldnames = [
        # Basic moment data
        "clip_id",
        "clip_label",
        "timestamps",
        "quote",
        "clip_duration_seconds",
        "viral_trigger",
        "why_it_hits",
        "energy_tag",
        "flags",

        # Persona captions (6 columns)
        "historian_caption",
        "thomist_caption",
        "ex_protestant_caption",
        "meme_catholic_caption",
        "old_world_catholic_caption",
        "catholic_caption",

        # Editor cut sheet fields
        "in_point",
        "out_point",
        "aspect_ratio",
        "crop_note",
        "opening_hook_subtitle",
        "emphasis_words_caps",
        "pacing_note",
        "b_roll_ideas",
        "text_on_screen_idea",
        "silence_handling",
        "thumbnail_text",
        "thumbnail_face_cue",
        "platform_priority",
        "use_persona_caption"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    # Write each moment as a row
    for moment in moments_with_cuts:
        cut_sheet = moment.get("editor_cut_sheet", {})
        personas = moment.get("persona_captions", {})

        row = {
            # Basic data
            "clip_id": moment.get("id", ""),
            "clip_label": cut_sheet.get("clip_label", ""),
            "timestamps": moment.get("timestamps", ""),
            "quote": moment.get("quote", ""),
            "clip_duration_seconds": moment.get("clip_duration_seconds", ""),
            "viral_trigger": moment.get("viral_trigger", ""),
            "why_it_hits": moment.get("why_it_hits", ""),
            "energy_tag": moment.get("energy_tag", ""),
            "flags": "; ".join(moment.get("flags", [])),

            # Persona captions
            "historian_caption": personas.get("historian", ""),
            "thomist_caption": personas.get("thomist", ""),
            "ex_protestant_caption": personas.get("ex_protestant", ""),
            "meme_catholic_caption": personas.get("meme_catholic", ""),
            "old_world_catholic_caption": personas.get("old_world_catholic", ""),
            "catholic_caption": personas.get("catholic", ""),

            # Cut sheet data
            "in_point": cut_sheet.get("in_point", ""),
            "out_point": cut_sheet.get("out_point", ""),
            "aspect_ratio": cut_sheet.get("aspect_ratio", ""),
            "crop_note": cut_sheet.get("crop_note", ""),
            "opening_hook_subtitle": cut_sheet.get("opening_hook_subtitle", ""),
            "emphasis_words_caps": "; ".join(cut_sheet.get("emphasis_words_caps", [])),
            "pacing_note": cut_sheet.get("pacing_note", ""),
            "b_roll_ideas": cut_sheet.get("b_roll_ideas", ""),
            "text_on_screen_idea": cut_sheet.get("text_on_screen_idea", ""),
            "silence_handling": cut_sheet.get("silence_handling", ""),
            "thumbnail_text": cut_sheet.get("thumbnail_text", ""),
            "thumbnail_face_cue": cut_sheet.get("thumbnail_face_cue", ""),
            "platform_priority": cut_sheet.get("platform_priority", ""),
            "use_persona_caption": cut_sheet.get("use_persona_caption", "")
        }

        writer.writerow(row)

    csv_content = output.getvalue()
    output.close()

    return csv_content


def to_markdown(moments_with_cuts: List[Dict[str, Any]]) -> str:
    """Convert moments with cut sheets to Markdown format.

    Args:
        moments_with_cuts: List of moment dictionaries with editor_cut_sheet data

    Returns:
        Markdown string ready for download
    """
    if not moments_with_cuts:
        return "# Viral Clips\n\nNo clips found."

    lines = []
    lines.append("# Viral Clips")
    lines.append("")
    lines.append(f"Generated {len(moments_with_cuts)} clips for editing.")
    lines.append("")

    for i, moment in enumerate(moments_with_cuts, 1):
        cut_sheet = moment.get("editor_cut_sheet", {})
        personas = moment.get("persona_captions", {})

        # Clip header
        clip_id = moment.get("id", f"clip_{i}")
        clip_label = cut_sheet.get("clip_label", "UNLABELED")
        lines.append(f"## Clip {i} – {clip_label}")
        lines.append("")

        # Basic info
        lines.append(f"- **Timestamps:** {moment.get('timestamps', 'N/A')}")
        lines.append(f"- **Duration:** {moment.get('clip_duration_seconds', 'N/A')} seconds")
        lines.append(f"- **Trigger:** {moment.get('viral_trigger', 'N/A')}")
        lines.append(f"- **Energy:** {moment.get('energy_tag', 'N/A')}")

        flags = moment.get('flags', [])
        if flags:
            lines.append(f"- **Flags:** {', '.join(flags)}")

        lines.append("")

        # Quote
        quote = moment.get("quote", "")
        if quote:
            lines.append("**Quote:**")
            lines.append(f"> {quote}")
            lines.append("")

        # Why it hits
        why_hits = moment.get("why_it_hits", "")
        if why_hits:
            lines.append(f"**Why it hits:** {why_hits}")
            lines.append("")

        # Persona captions
        lines.append("**Persona Captions:**")
        for persona_key, persona_name in [
            ("historian", "Historian"),
            ("thomist", "Thomist"),
            ("ex_protestant", "Ex-Protestant"),
            ("meme_catholic", "Meme Catholic"),
            ("old_world_catholic", "Old World Catholic"),
            ("catholic", "Catholic")
        ]:
            caption = personas.get(persona_key, "")
            lines.append(f"- {persona_name}: {caption}")
        lines.append("")

        # Editor cut sheet
        lines.append("**Editor Cut Sheet:**")
        lines.append(f"- **In Point:** {cut_sheet.get('in_point', 'N/A')}")
        lines.append(f"- **Out Point:** {cut_sheet.get('out_point', 'N/A')}")
        lines.append(f"- **Aspect Ratio:** {cut_sheet.get('aspect_ratio', '9:16')}")
        lines.append(f"- **Crop Note:** {cut_sheet.get('crop_note', 'N/A')}")
        lines.append(f"- **Opening Hook Subtitle:** {cut_sheet.get('opening_hook_subtitle', 'N/A')}")

        emphasis_words = cut_sheet.get('emphasis_words_caps', [])
        if emphasis_words:
            lines.append(f"- **Emphasis Words (ALL CAPS):** {', '.join(emphasis_words)}")
        else:
            lines.append(f"- **Emphasis Words (ALL CAPS):** None specified")

        lines.append(f"- **Pacing Note:** {cut_sheet.get('pacing_note', 'N/A')}")
        lines.append(f"- **B-Roll Ideas:** {cut_sheet.get('b_roll_ideas', 'none')}")
        lines.append(f"- **Text on Screen Idea:** {cut_sheet.get('text_on_screen_idea', 'none')}")
        lines.append(f"- **Silence Handling:** {cut_sheet.get('silence_handling', 'none')}")
        lines.append(f"- **Thumbnail Text:** {cut_sheet.get('thumbnail_text', 'N/A')}")
        lines.append(f"- **Thumbnail Face Cue:** {cut_sheet.get('thumbnail_face_cue', 'N/A')}")
        lines.append(f"- **Platform Priority:** {cut_sheet.get('platform_priority', 'All')}")
        lines.append(f"- **Use Persona Caption:** {cut_sheet.get('use_persona_caption', 'N/A')}")

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def format_clip_summary(moments_with_cuts: List[Dict[str, Any]]) -> str:
    """Generate a brief summary of clips for display.

    Args:
        moments_with_cuts: List of moment dictionaries

    Returns:
        Summary string
    """
    if not moments_with_cuts:
        return "No clips generated."

    total_clips = len(moments_with_cuts)

    # Count clips by trigger type
    triggers = {}
    for moment in moments_with_cuts:
        trigger = moment.get('viral_trigger', 'Unknown')
        triggers[trigger] = triggers.get(trigger, 0) + 1

    # Count flags
    flagged_clips = 0
    for moment in moments_with_cuts:
        if moment.get('flags'):
            flagged_clips += 1

    summary_parts = [
        f"Generated **{total_clips}** viral clips",
    ]

    if triggers:
        trigger_summary = ", ".join([f"{count} {trigger}" for trigger, count in triggers.items()])
        summary_parts.append(f"Triggers: {trigger_summary}")

    if flagged_clips > 0:
        summary_parts.append(f"{flagged_clips} clips have special flags")

    return " • ".join(summary_parts)