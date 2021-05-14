class Constant:
    audio_book_upload_audio_metadata = {
        "type": "object",
        "properties": {
            "filetypeCode": {"type": "number"},
            "name": {"type": "string", "maximum": 100, "minimum": 1},
            "duration": {"type": "number", "minimum": 0},
            "uploadedTime": {
                             "type": "string",
                             "pattern": "^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(([+-]\d\d:\d\d)|Z)?$"},
            "audioBookTitleAuthor": {"type": "string", "maximum": 100},
            "audioBookNarrator": {"type": "string", "maximum": 100}
        },
        "required": [
            "fileTypeCode", "name", "duration", "uploadedTime", "audioBookTitleAuthor", "audioBookNarrator"
        ]
    }
    podcast_book_upload_audio_metadata = {
        "type": "object",
        "properties": {
            "filetypeCode": {"type": "number"},
            "name": {"type": "string", "maximum": 100, "minimum": 1},
            "duration": {"type": "number", "minimum": 0},
            "uploadedTime": {
                             "type": "string",
                             "pattern": "^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(([+-]\d\d:\d\d)|Z)?$"},
            "podcastHost": {"type": "string", "minimum": 1, "maximum": 100},
            "podcastParticipants": {"type": "array", "items": {"type": "string"}, "maxItems": 10, "minItems": 0}
        },
        "required": [
            "fileTypeCode", "name", "duration", "uploadedTime", "podcastHost"
        ]
    }
    song_file_upload_audio_metadata = {
        "type": "object",
        "properties": {
            "filetypeCode": {"type": "number"},
            "name": {"type": "string", "maximum": 100, "minimum": 1},
            "duration": {"type": "number", "minimum": 0},
            "uploadedTime": {
                             "type": "string",
                             "pattern": "^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(([+-]\d\d:\d\d)|Z)?$"}
        },
        "required": [
            "fileTypeCode", "name", "duration", "uploadedTime"
        ]
    }
    upload_api_param_validation = {
        1: song_file_upload_audio_metadata,
        2: audio_book_upload_audio_metadata,
        3: podcast_book_upload_audio_metadata
    }
