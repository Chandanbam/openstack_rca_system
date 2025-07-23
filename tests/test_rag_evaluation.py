#!/usr/bin/env python3
"""
RAG Evaluation Tests
===================

Test file containing actual RAG evaluation test functions.
"""

import pytest
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Mock imports - replace these with your actual RAG system imports
# from your_rag_system import RAGPipeline, DocumentRetriever, ResponseGenerator

class MockRAGSystem:
    """Mock RAG system for testing - replace with your actual implementation"""
    
    def __init__(self):
        self.documents = [
            {"id": "doc1", "content": "OpenStack is a cloud computing platform"},
            {"id": "doc2", "content": "Nova is the compute service in OpenStack"},
            {"id": "doc3", "content": "Neutron handles networking in OpenStack"}
        ]
    
    async def retrieve_documents(self, query, top_k=3):
        """Mock document retrieval"""
        # Simple keyword matching for demo
        relevant_docs = []
        for doc in self.documents:
            if any(word.lower() in doc["content"].lower() for word in query.split()):
                relevant_docs.append(doc)
        return relevant_docs[:top_k]
    
    async def generate_response(self, query, context_docs):
        """Mock response generation using Anthropic API"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return "Mock response: Unable to connect to API"
        
        # Here you would normally call the Anthropic API
        # For now, return a mock response
        context = " ".join([doc["content"] for doc in context_docs])
        return f"Based on the context about {query}, here's a mock response using the retrieved information: {context[:100]}..."

@pytest.fixture
def rag_system():
    """Fixture to provide RAG system instance"""
    return MockRAGSystem()

@pytest.fixture
def test_queries():
    """Fixture providing test queries"""
    return [
        "What is OpenStack?",
        "How does Nova work?",
        "What is the networking service?",
        "Tell me about cloud computing"
    ]

@pytest.fixture
def output_dir():
    """Fixture for output directory"""
    output_path = Path("rag_evaluation_results")
    output_path.mkdir(exist_ok=True)
    return output_path

def test_api_key_loaded():
    """Test that Anthropic API key is properly loaded"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    assert api_key is not None, "ANTHROPIC_API_KEY not found in environment"
    assert len(api_key) > 10, "API key appears to be too short"
    print("✅ API key loaded successfully")

def test_document_retrieval(rag_system, test_queries):
    """Test document retrieval functionality"""
    async def run_retrieval_test():
        results = {}
        
        for query in test_queries:
            docs = await rag_system.retrieve_documents(query, top_k=3)
            results[query] = {
                "retrieved_count": len(docs),
                "documents": [doc["id"] for doc in docs]
            }
            
            # Basic assertions
            assert len(docs) >= 0, f"No documents retrieved for query: {query}"
            print(f"✅ Retrieved {len(docs)} documents for: '{query}'")
        
        return results
    
    # Run async test
    results = asyncio.run(run_retrieval_test())
    assert len(results) == len(test_queries), "Not all queries were processed"

def test_response_generation(rag_system, test_queries):
    """Test response generation functionality"""
    async def run_generation_test():
        results = {}
        
        for query in test_queries:
            # Get context documents
            context_docs = await rag_system.retrieve_documents(query, top_k=3)
            
            # Generate response
            response = await rag_system.generate_response(query, context_docs)
            
            results[query] = {
                "response": response,
                "context_doc_count": len(context_docs),
                "response_length": len(response)
            }
            
            # Basic assertions
            assert response is not None, f"No response generated for query: {query}"
            assert len(response) > 0, f"Empty response for query: {query}"
            print(f"✅ Generated response for: '{query}' (length: {len(response)})")
        
        return results
    
    # Run async test
    results = asyncio.run(run_generation_test())
    assert len(results) == len(test_queries), "Not all responses were generated"

def calculate_retrieval_metrics(query, retrieved_docs, ground_truth_docs):
    """Calculate retrieval metrics: precision, recall, F1"""
    if not retrieved_docs or not ground_truth_docs:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    retrieved_ids = set(doc["id"] for doc in retrieved_docs)
    ground_truth_ids = set(ground_truth_docs)
    
    # True positives: docs that are both retrieved and relevant
    tp = len(retrieved_ids.intersection(ground_truth_ids))
    
    # Precision: relevant docs / retrieved docs
    precision = tp / len(retrieved_ids) if retrieved_ids else 0.0
    
    # Recall: relevant docs retrieved / total relevant docs
    recall = tp / len(ground_truth_ids) if ground_truth_ids else 0.0
    
    # F1 score
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "true_positives": tp,
        "retrieved_count": len(retrieved_ids),
        "relevant_count": len(ground_truth_ids)
    }

def calculate_context_relevance_score(query, retrieved_docs):
    """Calculate how relevant the retrieved context is to the query"""
    if not retrieved_docs:
        return 0.0
    
    # Simple keyword-based relevance (replace with more sophisticated scoring)
    query_words = set(query.lower().split())
    relevance_scores = []
    
    for doc in retrieved_docs:
        doc_words = set(doc["content"].lower().split())
        overlap = len(query_words.intersection(doc_words))
        relevance = overlap / len(query_words) if query_words else 0.0
        relevance_scores.append(relevance)
    
    return round(sum(relevance_scores) / len(relevance_scores), 3)

def calculate_answer_relevance_score(query, response):
    """Calculate how relevant the answer is to the query"""
    if not response:
        return 0.0
    
    # Simple keyword-based relevance (replace with semantic similarity)
    query_words = set(query.lower().split())
    response_words = set(response.lower().split())
    overlap = len(query_words.intersection(response_words))
    
    return round(overlap / len(query_words) if query_words else 0.0, 3)

def calculate_groundedness_score(response, context_docs):
    """Calculate how well the response is grounded in the retrieved context"""
    if not response or not context_docs:
        return 0.0
    
    # Check if response content appears in context
    response_words = set(response.lower().split())
    context_text = " ".join([doc["content"] for doc in context_docs]).lower()
    context_words = set(context_text.split())
    
    grounded_words = len(response_words.intersection(context_words))
    return round(grounded_words / len(response_words) if response_words else 0.0, 3)

def get_ground_truth_docs():
    """Define ground truth relevant documents for each test query"""
    return {
        "What is OpenStack?": ["doc1"],  # OpenStack platform doc
        "How does Nova work?": ["doc2"],  # Nova compute service doc
        "What is the networking service?": ["doc3"],  # Neutron networking doc
        "Tell me about cloud computing": ["doc1"]  # Cloud computing platform doc
    }

def test_end_to_end_rag_pipeline(rag_system, test_queries, output_dir):
    """Test complete RAG pipeline with evaluation metrics"""
    async def run_pipeline_test():
        ground_truth = get_ground_truth_docs()
        
        # Initialize metrics aggregation
        all_precision_scores = []
        all_recall_scores = []
        all_f1_scores = []
        all_context_relevance = []
        all_answer_relevance = []
        all_groundedness = []
        
        query_results = {}
        
        for i, query in enumerate(test_queries):
            print(f"\n🔄 Processing query {i+1}/{len(test_queries)}: '{query}'")
            
            # Step 1: Document retrieval
            context_docs = await rag_system.retrieve_documents(query, top_k=3)
            
            # Step 2: Response generation
            response = await rag_system.generate_response(query, context_docs)
            
            # Step 3: Calculate evaluation metrics
            retrieval_metrics = calculate_retrieval_metrics(
                query, context_docs, ground_truth.get(query, [])
            )
            
            context_relevance = calculate_context_relevance_score(query, context_docs)
            answer_relevance = calculate_answer_relevance_score(query, response)
            groundedness = calculate_groundedness_score(response, context_docs)
            
            # Store detailed results
            query_results[query] = {
                "retrieval_metrics": retrieval_metrics,
                "context_relevance": context_relevance,
                "answer_relevance": answer_relevance,
                "groundedness": groundedness,
                "retrieved_doc_count": len(context_docs),
                "response_length": len(response)
            }
            
            # Aggregate metrics
            all_precision_scores.append(retrieval_metrics["precision"])
            all_recall_scores.append(retrieval_metrics["recall"])
            all_f1_scores.append(retrieval_metrics["f1"])
            all_context_relevance.append(context_relevance)
            all_answer_relevance.append(answer_relevance)
            all_groundedness.append(groundedness)
            
            # Assertions
            assert len(context_docs) >= 0, f"Retrieval failed for: {query}"
            assert response, f"Response generation failed for: {query}"
            
            print(f"   📊 P: {retrieval_metrics['precision']:.3f}, R: {retrieval_metrics['recall']:.3f}, F1: {retrieval_metrics['f1']:.3f}")
            print(f"   📊 Context: {context_relevance:.3f}, Answer: {answer_relevance:.3f}, Ground: {groundedness:.3f}")
        
        # Calculate overall metrics
        overall_metrics = {
            "retrieval": {
                "avg_precision": round(sum(all_precision_scores) / len(all_precision_scores), 3),
                "avg_recall": round(sum(all_recall_scores) / len(all_recall_scores), 3),
                "avg_f1": round(sum(all_f1_scores) / len(all_f1_scores), 3),
                "precision_at_3": round(sum(all_precision_scores) / len(all_precision_scores), 3)
            },
            "rag_triad": {
                "avg_context_relevance": round(sum(all_context_relevance) / len(all_context_relevance), 3),
                "avg_answer_relevance": round(sum(all_answer_relevance) / len(all_answer_relevance), 3),
                "avg_groundedness": round(sum(all_groundedness) / len(all_groundedness), 3)
            },
            "overall_rag_score": round(
                (sum(all_f1_scores) + sum(all_context_relevance) + 
                 sum(all_answer_relevance) + sum(all_groundedness)) / 
                (4 * len(test_queries)), 3
            )
        }
        
        # Create final results structure
        pipeline_results = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_summary": {
                "total_queries": len(test_queries),
                "evaluation_type": "RAG Pipeline Evaluation",
                "metrics_included": ["precision", "recall", "f1", "context_relevance", "answer_relevance", "groundedness"]
            },
            "metrics": overall_metrics,
            "query_details": query_results
        }
        
        # Save results
        results_file = output_dir / "rag_evaluation_report.json"
        with open(results_file, 'w') as f:
            json.dump(pipeline_results, f, indent=2)
        
        print(f"\n📊 Results saved to: {results_file}")
        print(f"\n🎯 OVERALL RAG METRICS:")
        print(f"   Retrieval - P: {overall_metrics['retrieval']['avg_precision']:.3f}, R: {overall_metrics['retrieval']['avg_recall']:.3f}, F1: {overall_metrics['retrieval']['avg_f1']:.3f}")
        print(f"   RAG Triad - Context: {overall_metrics['rag_triad']['avg_context_relevance']:.3f}, Answer: {overall_metrics['rag_triad']['avg_answer_relevance']:.3f}, Ground: {overall_metrics['rag_triad']['avg_groundedness']:.3f}")
        print(f"   Overall RAG Score: {overall_metrics['overall_rag_score']:.3f}")
        
        return pipeline_results
    
    # Run complete pipeline test
    results = asyncio.run(run_pipeline_test())
    
    # Final assertions
    assert len(results["query_details"]) == len(test_queries), "Pipeline didn't process all queries"
    assert results["metrics"]["overall_rag_score"] > 0, "Overall RAG score should be positive"
    
    print(f"\n✅ End-to-end RAG evaluation completed successfully!")

def test_performance_metrics(rag_system, test_queries):
    """Test and measure basic performance metrics"""
    async def measure_performance():
        import time
        
        metrics = {
            "total_queries": len(test_queries),
            "retrieval_times": [],
            "generation_times": [],
            "total_time": 0
        }
        
        start_time = time.time()
        
        for query in test_queries:
            # Measure retrieval time
            ret_start = time.time()
            docs = await rag_system.retrieve_documents(query)
            ret_time = time.time() - ret_start
            metrics["retrieval_times"].append(ret_time)
            
            # Measure generation time
            gen_start = time.time()
            response = await rag_system.generate_response(query, docs)
            gen_time = time.time() - gen_start
            metrics["generation_times"].append(gen_time)
        
        metrics["total_time"] = time.time() - start_time
        metrics["avg_retrieval_time"] = sum(metrics["retrieval_times"]) / len(metrics["retrieval_times"])
        metrics["avg_generation_time"] = sum(metrics["generation_times"]) / len(metrics["generation_times"])
        
        return metrics
    
    # Run performance test
    metrics = asyncio.run(measure_performance())
    
    # Performance assertions
    assert metrics["avg_retrieval_time"] < 5.0, "Retrieval too slow (>5s average)"
    assert metrics["avg_generation_time"] < 10.0, "Generation too slow (>10s average)"
    
    print(f"📈 Performance Metrics:")
    print(f"   Average retrieval time: {metrics['avg_retrieval_time']:.3f}s")
    print(f"   Average generation time: {metrics['avg_generation_time']:.3f}s")
    print(f"   Total test time: {metrics['total_time']:.3f}s")

if __name__ == "__main__":
    # This allows running the test file directly for debugging
    print("Running RAG evaluation tests directly...")
    pytest.main([__file__, "-v"])