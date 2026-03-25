"""
Configuration Management
Loads configuration from .env file in project root directory
"""

import os
from dotenv import load_dotenv

# Load .env file from project root
# Path: MiroFish/.env (relative to backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    # If no .env in root, try to load environment variables (for production)
    load_dotenv(override=True)


class Config:
    """Flask configuration class"""

    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # JSON configuration - disable ASCII escaping to display Chinese directly (not as \uXXXX)
    JSON_AS_ASCII = False

    # LLM configuration (unified OpenAI format)
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'http://localhost:11434/v1')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'qwen2.5:32b')

    # Neo4j configuration
    NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.environ.get('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'mirofish')

    # Embedding configuration
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text')
    EMBEDDING_BASE_URL = os.environ.get('EMBEDDING_BASE_URL', 'http://localhost:11434')

    # File upload configuration
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}

    # Text processing configuration
    DEFAULT_CHUNK_SIZE = 500  # Default chunk size
    DEFAULT_CHUNK_OVERLAP = 50  # Default overlap size
    _default_graph_batch_size_str = os.environ.get('DEFAULT_GRAPH_BATCH_SIZE', '3')
    try:
        DEFAULT_GRAPH_BATCH_SIZE = int(_default_graph_batch_size_str.strip())
    except (ValueError, AttributeError):
        DEFAULT_GRAPH_BATCH_SIZE = 3

    # Number of parallel threads for chunk ingestion (NER+embed are I/O-bound).
    # Keep at 1 to disable parallelism; increase cautiously relative to Ollama capacity.
    _graph_build_workers_str = os.environ.get('GRAPH_BUILD_WORKERS', '2')
    try:
        GRAPH_BUILD_WORKERS = max(1, int(_graph_build_workers_str.strip()))
    except (ValueError, AttributeError):
        GRAPH_BUILD_WORKERS = 2

    # Hard server-side ceiling on client-supplied max_workers to prevent
    # thread exhaustion.  Override via GRAPH_BUILD_WORKERS_MAX env var.
    _graph_build_workers_max_str = os.environ.get('GRAPH_BUILD_WORKERS_MAX', '8')
    try:
        GRAPH_BUILD_WORKERS_MAX = max(1, int(_graph_build_workers_max_str.strip()))
    except (ValueError, AttributeError):
        GRAPH_BUILD_WORKERS_MAX = 8

    # Maximum tokens the NER/RE LLM call may produce per chunk.  A lower value
    # reduces latency and reduces context use when chunks are small.  The
    # extractor will scale this down proportionally for short chunks.
    _ner_max_tokens_str = os.environ.get('NER_MAX_TOKENS', '1024')
    try:
        NER_MAX_TOKENS = max(256, int(_ner_max_tokens_str.strip()))
    except (ValueError, AttributeError):
        NER_MAX_TOKENS = 1024

    # Extra token allowance added on top of the proportional JSON budget to
    # cover the <think> reasoning block emitted by reasoning models (e.g.
    # qwen3, deepseek-r1, qwq).  These tokens count against max_tokens but
    # are stripped before JSON parsing, so without this headroom the model
    # exhausts its budget on thinking and returns an empty JSON response.
    # Set to 0 for non-reasoning models.  Default 1024 covers typical NER
    # reasoning traces without significantly increasing latency.
    _ner_think_overhead_str = os.environ.get('NER_THINK_OVERHEAD', '1024')
    try:
        NER_THINK_OVERHEAD = max(0, int(_ner_think_overhead_str.strip()))
    except (ValueError, AttributeError):
        NER_THINK_OVERHEAD = 1024

    # When True, relation (edge) embeddings are stored as empty vectors during
    # the graph build and can be computed later via embed_pending_relations().
    # Set to False (default) for full embeddings on every chunk.
    DEFER_RELATION_EMBEDDINGS = os.environ.get('DEFER_RELATION_EMBEDDINGS', 'false').strip().lower() == 'true'

    # OASIS simulation configuration
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')

    # OASIS platform available actions configuration
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]

    # Report Agent configuration
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY not configured (set to any non-empty value, e.g. 'ollama')")
        if not cls.NEO4J_URI:
            errors.append("NEO4J_URI not configured")
        if not cls.NEO4J_PASSWORD:
            errors.append("NEO4J_PASSWORD not configured")
        return errors
