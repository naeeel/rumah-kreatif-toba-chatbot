import pandas as pd
import logging
from typing import List, Dict, Any
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.metrics.critique import harmfulness
from ragas import evaluate

from app.rag.generator import ResponseGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEvaluator:
    def __init__(self):
        self.generator = ResponseGenerator()
        self.test_questions = [
            "Apa saja produk yang dijual oleh Rumah Kreatif Toba?",
            "Berapa stok produk kain tenun yang tersedia?",
            "Bagaimana cara memesan produk dari Rumah Kreatif Toba?",
            "Berapa lama waktu pengiriman untuk wilayah Jakarta?",
            "Bisakah saya melacak pesanan saya?",
            "Apakah ada diskon untuk pembelian dalam jumlah besar?",
            "Apa bahan dasar kerajinan tangan yang dijual?"
        ]
    
    def generate_responses(self) -> List[Dict[str, Any]]:
        """Generate responses for test questions"""
        results = []
        
        for question in self.test_questions:
            logger.info(f"Generating response for: {question}")
            
            # Get intent and context
            intent_data = self.generator._extract_intent(question)
            intent_data["query"] = question
            context = self.generator._retrieve_context(intent_data)
            
            # Generate response
            response = self.generator.generate_response(question)
            
            results.append({
                "question": question,
                "answer": response,
                "contexts": [context],
                "ground_truths": []  # In a real scenario, you'd have ground truth answers
            })
        
        return results
    
    def evaluate(self) -> pd.DataFrame:
        """Evaluate RAG responses using RAGAS metrics"""
        # Generate responses
        eval_data = self.generate_responses()
        
        # Convert to DataFrame
        df = pd.DataFrame(eval_data)
        
        # Calculate metrics
        try:
            # Context precision - measures precision of retrieved contexts
            context_precision_score = context_precision.score(df)
            
            # Faithfulness - measures how factually consistent the answer is with the contexts
            faithfulness_score = faithfulness.score(df)
            
            # Answer relevancy - measures how relevant the answer is to the question
            answer_relevancy_score = answer_relevancy.score(df)
            
            # Harmfulness - measures potential for harmful content
            harmfulness_score = harmfulness.score(df)
            
            # Create results DataFrame
            results = pd.DataFrame({
                'question': df['question'],
                'context_precision': context_precision_score,
                'faithfulness': faithfulness_score,
                'answer_relevancy': answer_relevancy_score,
                'harmfulness': harmfulness_score
            })
            
            # Calculate average scores
            averages = {
                'context_precision': context_precision_score.mean(),
                'faithfulness': faithfulness_score.mean(),
                'answer_relevancy': answer_relevancy_score.mean(),
                'harmfulness': harmfulness_score.mean()
            }
            
            logger.info(f"Average scores: {averages}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error evaluating RAG: {str(e)}")
            return pd.DataFrame()

def run_evaluation():
    """Run RAG evaluation"""
    evaluator = RAGEvaluator()
    results = evaluator.evaluate()
    
    if not results.empty:
        # Save results to CSV
        results.to_csv("rag_evaluation_results.csv", index=False)
        logger.info("Evaluation results saved to rag_evaluation_results.csv")
    
    return results

if __name__ == "__main__":
    run_evaluation()