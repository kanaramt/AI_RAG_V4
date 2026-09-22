"""
===========================================================
Connector Constants

Purpose
-------
This file contains constants shared by every connector.

Why?

Instead of every connector maintaining its own list of
supported extensions, everything is defined once here.

Every connector should import from this file.
===========================================================
"""

# ---------------------------------------------------------
# Supported document formats
# ---------------------------------------------------------

SUPPORTED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".csv",
    ".txt",
}

# ---------------------------------------------------------
# Supported image formats
# ---------------------------------------------------------

SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".webp",
}

# ---------------------------------------------------------
# Complete list of supported knowledge files
# ---------------------------------------------------------

SUPPORTED_FILE_EXTENSIONS = (
    SUPPORTED_DOCUMENT_EXTENSIONS
    | SUPPORTED_IMAGE_EXTENSIONS
)

# ---------------------------------------------------------
# Future Expansion
#
# Add new extensions here instead of modifying connectors.
#
# Example:
#
# SUPPORTED_AUDIO_EXTENSIONS
# SUPPORTED_VIDEO_EXTENSIONS
# SUPPORTED_CAD_EXTENSIONS
# ---------------------------------------------------------
