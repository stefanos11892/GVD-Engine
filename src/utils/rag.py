"""
RAG (Retrieval-Augmented Generation) Module
=============================================
Implements semantic search over document chunks to reduce LLM context size.
Uses FAISS for vector similarity search with sentence-transformers embeddings.

ARCHITECTURE:
1. Chunker: Splits markdown by section headers
2. Embedder: Converts chunks to vectors (all-MiniLM-L6-v2)
3. Store: FAISS index for fast similarity search
4. Retriever: Gets top-K relevant chunks for a query
"""
import re
import logging
from typing import List, Dict, Any, Optional
import hashlib

logger = logging.getLogger("RAG")

# ======================================
# LAZY IMPORTS FOR OPTIONAL DEPENDENCIES
# ======================================
# FAISS and sentence-transformers are optional - fallback to full context if missing
_faiss = None
_SentenceTransformer = None


def _load_dependencies():
    """Lazy-load heavy ML dependencies."""
    global _faiss, _SentenceTransformer
    if _faiss is None:
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            _faiss = faiss
            _SentenceTransformer = SentenceTransformer
            logger.info("RAG dependencies loaded successfully.")
        except ImportError as e:
            logger.warning(f"RAG dependencies not available: {e}. Using full context fallback.")
            return False
    return True


# ======================================
# DOCUMENT CHUNKING
# ======================================
def chunk_by_sections(markdown: str, max_chunk_size: int = 4000) -> List[Dict[str, Any]]:
    """
    Split markdown into chunks by section headers.
    
    Financial documents typically have sections like:
    - "## Income Statement"
    - "## Risk Factors"
    - "## Management Discussion"
    
    Returns list of {text, section_title, index}
    """
    if not markdown:
        return []
    
    # Split by markdown headers (## or ###)
    section_pattern = r'(^#{2,3}\s+.+$)'
    parts = re.split(section_pattern, markdown, flags=re.MULTILINE)
    
    chunks = []
    current_section = "Document Start"
    current_text = ""
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Check if this is a header
        if re.match(r'^#{2,3}\s+', part):
            # Save previous section if it has content
            if current_text.strip():
                # Split large sections into sub-chunks
                for sub_chunk in _split_large_chunk(current_text, max_chunk_size):
                    chunks.append({
                        "text": sub_chunk,
                        "section_title": current_section,
                        "index": len(chunks)
                    })
            current_section = part.replace("#", "").strip()
            current_text = ""
        else:
            current_text += "\n" + part
    
    # Don't forget the last section
    if current_text.strip():
        for sub_chunk in _split_large_chunk(current_text, max_chunk_size):
            chunks.append({
                "text": sub_chunk,
                "section_title": current_section,
                "index": len(chunks)
            })
    
    logger.info(f"Chunked document into {len(chunks)} sections")
    return chunks


def _split_large_chunk(text: str, max_size: int) -> List[str]:
    """Split a chunk that exceeds max_size into smaller pieces."""
    if len(text) <= max_size:
        return [text]
    
    # Split by paragraphs
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    
    for para in paragraphs:
        if len(current) + len(para) > max_size:
            if current:
                chunks.append(current)
            current = para
        else:
            current += "\n\n" + para if current else para
    
    if current:
        chunks.append(current)
    
    return chunks


# ======================================
# VECTOR STORE (FAISS-based)
# ======================================
class DocumentIndex:
    """
    In-memory FAISS index for semantic search over document chunks.
    
    Usage:
        index = DocumentIndex()
        index.build(chunks)
        relevant = index.retrieve("revenue figures", top_k=5)
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.index = None
        self.chunks = []
        self._doc_hash = None
    
    def build(self, chunks: List[Dict[str, Any]]) -> bool:
        """Build FAISS index from chunks. Returns False if dependencies missing."""
        if not _load_dependencies():
            return False
        
        if not chunks:
            logger.warning("No chunks to index")
            return False
        
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        
        # Compute hash to detect if we need to rebuild
        doc_hash = hashlib.md5("".join(texts).encode()).hexdigest()
        if doc_hash == self._doc_hash and self.index is not None:
            logger.info("Index already built for this document")
            return True
        
        # Load model (lazy, cached)
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = _SentenceTransformer(self.model_name)
        
        # Generate embeddings
        logger.info(f"Embedding {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = _faiss.IndexFlatIP(dimension)  # Inner product (cosine after normalization)
        
        # Normalize for cosine similarity
        _faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        self._doc_hash = doc_hash
        logger.info(f"FAISS index built with {self.index.ntotal} vectors")
        return True
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve top-K most relevant chunks for a query."""
        if not self.index or not self.model:
            logger.warning("Index not built, returning empty")
            return []
        
        # Embed query
        query_vec = self.model.encode([query], show_progress_bar=False)
        _faiss.normalize_L2(query_vec)
        
        # Search
        scores, indices = self.index.search(query_vec, min(top_k, len(self.chunks)))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["relevance_score"] = float(score)
                results.append(chunk)
        
        return results


# ======================================
# HIGH-LEVEL RETRIEVAL API
# ======================================
_document_index: Optional[DocumentIndex] = None


def index_document(markdown: str) -> bool:
    """
    Index a markdown document for RAG retrieval.
    Call this once when loading a new document.
    """
    global _document_index
    
    chunks = chunk_by_sections(markdown)
    if not chunks:
        return False
    
    _document_index = DocumentIndex()
    return _document_index.build(chunks)


def retrieve_context(query: str, top_k: int = 8, max_chars: int = 20000) -> str:
    """
    Retrieve relevant context for a query.
    
    Args:
        query: The metric or question to search for
        top_k: Number of chunks to retrieve
        max_chars: Maximum total characters to return
    
    Returns:
        Concatenated relevant chunks as context string
    """
    global _document_index
    
    if _document_index is None:
        logger.warning("No document indexed, cannot retrieve")
        return ""
    
    results = _document_index.retrieve(query, top_k=top_k)
    
    # Build context string with section headers
    context_parts = []
    total_chars = 0
    
    for chunk in results:
        section = chunk.get("section_title", "Unknown")
        text = chunk.get("text", "")
        score = chunk.get("relevance_score", 0)
        
        formatted = f"\n[Section: {section}] (Relevance: {score:.2f})\n{text}\n"
        
        if total_chars + len(formatted) > max_chars:
            break
        
        context_parts.append(formatted)
        total_chars += len(formatted)
    
    return "\n---\n".join(context_parts)


def get_context_for_metrics(metrics: List[str], markdown: str, max_chars: int = 25000) -> str:
    """
    Get relevant context for extracting specific metrics.
    
    This is the main API for QuantAgent to use instead of full document.
    
    Args:
        metrics: List of metric names to search for (e.g., ["Revenue", "Net Income"])
        markdown: Full document markdown
        max_chars: Maximum context size
    
    Returns:
        Relevant document excerpts optimized for the metric extraction task
    """
    # Index document if needed
    if not index_document(markdown):
        # Fallback to truncated full context
        logger.warning("RAG indexing failed, using truncated context")
        return markdown[:max_chars]
    
    # Build composite query from metrics
    query = f"Financial data for: {', '.join(metrics)}. Income statement, revenue, expenses, cash flow."
    
    return retrieve_context(query, top_k=10, max_chars=max_chars)
