"""
Example usage of the RAG pipeline for InsightForge AI.

This demonstrates how to:
1. Ingest business context documents (PDF, TXT, MD)
2. Build the vector index
3. Query for relevant context during anomaly analysis
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag import RAGPipeline


def main():
    """Run example workflow."""

    # 1. Create pipeline (with persistent index)
    pipeline = RAGPipeline(
        index_path="data/rag_index",
        org_id="org_demo",
        config={
            "chunk_size": 500,
            "chunk_overlap": 50
        }
    )

    # 2. Ingest business context documents
    print("Ingesting documents...")
    stats = pipeline.ingest_and_index(
        sources=[
            "docs/business/metric_definitions.md",
            "docs/business/process_docs/",
            "docs/incidents/"
        ]
    )
    print(f"Stats: {stats}")

    # 3. Query for context during anomaly analysis
    print("\nQuerying for context...")

    # Example: anomaly detected in revenue
    query = "Why did revenue drop in US-East region? What business processes affect revenue?"
    results = pipeline.query(
        query=query,
        top_k=5,
        min_score=0.3,
        filters={"document_type": ["metric_def", "incident"]}
    )

    print(f"Query: '{query}'")
    print(f"Found {len(results)} relevant snippets:\n")

    for i, result in enumerate(results, 1):
        print(f"[{i}] Score: {result['score']:.3f} | Doc: {result['document_id']}")
        print(f"Text: {result['text'][:200]}...\n")

    # 4. Print stats
    print("Vector store stats:", pipeline.get_stats())


def quick_example():
    """Minimal example for quick testing."""

    from src.rag import create_pipeline

    # Create in-memory pipeline (no persistence)
    pipeline = create_pipeline(org_id="test_org")

    # Ingest a single markdown file
    pipeline.ingest_and_index(["example_business_context.md"])

    # Query
    results = pipeline.query("What is the definition of revenue?", top_k=3)
    return results


def root_cause_integration_example():
    """
    Example: How Root Cause Analysis Service uses RAG.

    This shows the integration pattern for the anomaly analysis workflow.
    """
    from src.rag import create_pipeline

    # RAG system initialization (could be singleton in the service)
    rag = create_pipeline(
        index_path="data/rag_index",
        org_id="org_123"
    )

    # Simulate: Anomaly detected - root cause service needs context
    anomaly_context = {
        "org_id": "org_123",
        "metric": "revenue",
        "anomaly_type": "drop",
        "dimensions": {
            "region": "US-East",
            "product": "Enterprise"
        },
        "timestamp": "2026-03-15T14:00:00Z"
    }

    # Query RAG for relevant business context
    context = rag.retriever.get_relevant_context(
        anomaly_context=anomaly_context,
        top_k=5
    )

    # Use this context in the explanation prompt to Claude
    print("Anomaly Context:")
    print(f"  Metric: {anomaly_context['metric']}")
    print(f"  Type: {anomaly_context['anomaly_type']}")
    print(f"  Region: {anomaly_context['dimensions']['region']}")
    print(f"\nRelevant Business Context ({len(context)} items):")

    for i, item in enumerate(context, 1):
        print(f"\n{i}. [{item['metadata'].get('document_type', 'unknown')}] Score: {item['score']:.3f}")
        print(f"   {item['text'][:300]}...")

    return context


if __name__ == "__main__":
    # This would require actual document files to run
    # Uncomment to test with your own files:
    # main()

    # Or use quick example with sample data
    pass
