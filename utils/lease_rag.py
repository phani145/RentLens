"""
RentLens AI - Lease Document RAG Engine.
Extracts text from PDF leases with PyMuPDF, chunks with LangChain,
indexes into ChromaDB, and performs grounded retrieval.
"""

import os
import re
import math
from typing import List, Dict, Any, Tuple, Optional
import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")


class LeaseRAGEngine:
    """Manages lease document ingestion, indexing, and semantic retrieval."""

    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        
        # We attempt to use Chroma's standard embedding function; fallback to custom if needed
        try:
            self.emb_fn = embedding_functions.DefaultEmbeddingFunction()
        except Exception:
            self.emb_fn = None

    def extract_text_from_pdf(self, pdf_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        Extracts clean text and page metadata from PDF bytes using PyMuPDF.
        Returns list of dicts: [{"page": 1, "text": "...", "word_count": 120}]
        """
        pages_data = []
        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text").strip()
                if text:
                    # Clean repeated whitespace
                    clean_text = re.sub(r"\s+", " ", text)
                    pages_data.append({
                        "page": page_num + 1,
                        "text": clean_text,
                        "raw_text": text,
                        "word_count": len(clean_text.split()),
                        "filename": filename
                    })
            doc.close()
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF '{filename}': {str(e)}")

        if not pages_data:
            raise ValueError(f"No readable text found in PDF '{filename}'. Document may contain scanned images without OCR.")

        return pages_data

    def chunk_document(
        self,
        pages_data: List[Dict[str, Any]],
        chunk_size: int = 650,
        chunk_overlap: int = 120
    ) -> List[Dict[str, Any]]:
        """
        Splits extracted pages into overlapping semantic chunks with page provenance.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\nSection", "\n\n", "\n", ". ", " ", ""]
        )

        all_chunks = []
        global_chunk_idx = 0

        for page_info in pages_data:
            page_text = page_info["raw_text"]
            chunks = splitter.split_text(page_text)
            for sub_idx, chunk in enumerate(chunks):
                clean_chunk = chunk.strip()
                if len(clean_chunk) > 30:  # Ignore tiny headers/footers
                    all_chunks.append({
                        "id": f"doc_p{page_info['page']}_c{sub_idx}_{global_chunk_idx}",
                        "text": clean_chunk,
                        "metadata": {
                            "page": page_info["page"],
                            "filename": page_info["filename"],
                            "chunk_index": global_chunk_idx
                        }
                    })
                    global_chunk_idx += 1

        return all_chunks

    def index_lease(self, collection_name: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Indexes chunks into ChromaDB collection. Sanitizes collection name.
        """
        # Ensure collection name is alphanumeric with underscores/hyphens
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", collection_name).strip("_")[:60]
        if not safe_name:
            safe_name = "lease_collection"

        # Delete existing collection if re-indexing same document
        try:
            self.client.delete_collection(name=safe_name)
        except Exception:
            pass

        try:
            if self.emb_fn:
                collection = self.client.create_collection(
                    name=safe_name,
                    embedding_function=self.emb_fn,
                    metadata={"hnsw:space": "cosine"}
                )
            else:
                collection = self.client.create_collection(name=safe_name)
        except Exception:
            # Fallback without embedding_function override
            collection = self.client.get_or_create_collection(name=safe_name)

        # Batch insert into Chroma
        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Chroma supports batch inserts up to 500
        batch_size = 200
        for i in range(0, len(chunks), batch_size):
            collection.add(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size]
            )

        return safe_name

    def retrieve_relevant_chunks(
        self,
        collection_name: str,
        query: str,
        top_k: int = 4,
        all_chunks_fallback: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant clauses matching the query.
        Includes graceful keyword/TF similarity fallback if vector collection is unavailable.
        """
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", collection_name).strip("_")[:60]
        
        try:
            collection = self.client.get_collection(name=safe_name)
            results = collection.query(
                query_texts=[query],
                n_results=min(top_k, collection.count())
            )

            retrieved = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                docs = results["documents"][0]
                metas = results.get("metadatas", [[]])[0]
                ids = results.get("ids", [[]])[0]

                for doc_text, meta, doc_id in zip(docs, metas, ids):
                    retrieved.append({
                        "id": doc_id,
                        "text": doc_text,
                        "metadata": meta
                    })

            if retrieved:
                return retrieved

        except Exception as e:
            # Fall back to lexical keyword matching
            pass

        if all_chunks_fallback:
            return self._lexical_keyword_search(query, all_chunks_fallback, top_k)

        return []

    def _lexical_keyword_search(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """BM25/TF-IDF inspired keyword scoring fallback."""
        query_words = set(re.findall(r"\w+", query.lower()))
        # Remove common stop words
        stops = {"what", "is", "the", "in", "to", "of", "and", "a", "an", "does", "can", "are", "for", "with", "or"}
        keywords = query_words - stops
        if not keywords:
            keywords = query_words

        scored = []
        for c in chunks:
            text_lower = c["text"].lower()
            score = sum(text_lower.count(k) * (2 if len(k) > 4 else 1) for k in keywords)
            if score > 0:
                scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for score, c in scored[:top_k]]


# Common pre-built lease query templates for renters
SAMPLE_LEASE_QUESTIONS = [
    "What are the rules regarding security deposit return and potential deductions?",
    "Can the landlord enter the property without advance notice? What is required?",
    "Who is responsible for routine repairs, mold remediation, and plumbing maintenance?",
    "What is the policy, penalty, or procedure for early termination of the lease?",
    "Are pets allowed, and what are the associated pet deposits, rents, or restrictions?",
    "What late fees apply if rent is delayed, and is there any grace period?",
    "What are the tenant obligations regarding property alterations or painting?"
]
