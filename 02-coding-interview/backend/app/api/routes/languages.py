"""
Languages API Routes

Endpoints for getting information about supported programming languages.
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status

from app.schemas.session import LanguageInfo, LanguageListResponse
from app.models.domain import Language


# Create a router for language endpoints
router = APIRouter(
    prefix="/api/v1/languages",
    tags=["Languages"]
)


# Load language configuration from JSON file
def load_languages():
    """
    Load language configuration from JSON file.
    
    Returns:
        List of Language objects
    """
    languages_file = Path(__file__).parent.parent.parent / "data" / "languages.json"
    
    try:
        with open(languages_file, "r") as f:
            data = json.load(f)
            
        languages = []
        for lang_data in data["languages"]:
            language = Language(
                id=lang_data["id"],
                name=lang_data["name"],
                version=lang_data["version"],
                file_extension=lang_data["file_extension"],
                monaco_language=lang_data["monaco_language"],
                can_run_in_browser=lang_data["can_run_in_browser"],
                default_code=lang_data["default_code"]
            )
            languages.append(language)
        
        return languages
        
    except Exception as e:
        # If file doesn't exist or is invalid, return default languages
        return get_default_languages()


def get_default_languages():
    """
    Get default language configuration.
    
    Returns:
        List of default Language objects
    """
    return [
        Language(
            id="javascript",
            name="JavaScript",
            version="ES2022",
            file_extension=".js",
            monaco_language="javascript",
            can_run_in_browser=True,
            default_code="// Start coding here\nconsole.log('Hello, World!');"
        ),
        Language(
            id="python",
            name="Python",
            version="3.11",
            file_extension=".py",
            monaco_language="python",
            can_run_in_browser=False,
            default_code="# Start coding here\nprint('Hello, World!')"
        ),
    ]


# Cache loaded languages
_languages_cache = None


def get_languages():
    """Get cached language list"""
    global _languages_cache
    if _languages_cache is None:
        _languages_cache = load_languages()
    return _languages_cache


@router.get(
    "",
    response_model=LanguageListResponse,
    summary="List supported languages",
    description="Returns a list of all programming languages supported by the platform"
)
async def list_languages():
    """
    Get list of supported programming languages.
    
    Each language includes metadata like default code template,
    file extension, and whether it can run in the browser.
    
    Returns:
        List of supported languages with metadata
    """
    languages = get_languages()
    
    # Convert to response format
    language_infos = [
        LanguageInfo(
            id=lang.id,
            name=lang.name,
            version=lang.version,
            file_extension=lang.file_extension,
            monaco_language=lang.monaco_language,
            can_run_in_browser=lang.can_run_in_browser,
            default_code=lang.default_code
        )
        for lang in languages
    ]
    
    return LanguageListResponse(languages=language_infos)


@router.get(
    "/{language_id}/template",
    summary="Get language template",
    description="Returns the default code template for a specific language"
)
async def get_language_template(language_id: str):
    """
    Get the default code template for a language.
    
    Useful when switching languages to provide appropriate starter code.
    
    Args:
        language_id: Language identifier (e.g., "javascript", "python")
        
    Returns:
        Default code template
        
    Raises:
        404: If language is not supported
    """
    languages = get_languages()
    
    # Find the language
    for lang in languages:
        if lang.id == language_id:
            return {
                "language_id": lang.id,
                "template": lang.default_code
            }
    
    # Language not found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Language '{language_id}' is not supported"
    )
