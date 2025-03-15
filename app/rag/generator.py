import logging
import json
from typing import Dict, Any, List, Optional
import requests

from app.core.config import settings
from app.rag.retriever import RAGRetriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseGenerator:
    def __init__(self):
        self.retriever = RAGRetriever()
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
    
    def _call_ollama_api(self, prompt: str, context: Optional[str] = None) -> str:
        """Call Ollama API to generate response"""
        url = f"{self.base_url}/api/generate"
        
        # Prepare payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        # Add context if provided
        if context:
            system_prompt = f"Anda adalah chatbot layanan pelanggan untuk Rumah Kreatif Toba. Gunakan informasi ini untuk menjawab pertanyaan pengguna: {context}"
            payload["system"] = system_prompt
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            result = response.json()
            return result.get("response", "Maaf, saya tidak dapat menghasilkan respons saat ini.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            return "Maaf, terjadi kesalahan saat berkomunikasi dengan model bahasa."
    
    def _extract_intent(self, query: str) -> Dict[str, Any]:
        """Extract intent from user query"""
        # Use Ollama to extract intent
        prompt = f"""
        Analisis pertanyaan berikut dan ekstrak intent dan entitas. 
        Format output sebagai JSON dengan kunci 'intent' dan 'entities'.
        
        Pertanyaan: {query}
        
        Pilihan intent:
        - produk_info (informasi produk)
        - stok_check (cek stok barang)
        - order_status (status pesanan)
        - customer_orders (daftar pesanan pelanggan)
        - faq (pertanyaan umum)
        - general (pertanyaan umum tidak spesifik)
        
        Format entitas bisa produk_id, produk_nama, pesanan_id, pelanggan_id, kategori, dll
        
        Output JSON:
        """
        
        try:
            response = self._call_ollama_api(prompt)
            # Parse JSON from response
            # Find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                intent_data = json.loads(json_str)
                return intent_data
            else:
                # Fallback with simple heuristics
                return self._fallback_intent_extraction(query)
        except Exception as e:
            logger.error(f"Error extracting intent: {str(e)}")
            return self._fallback_intent_extraction(query)
    
    def _fallback_intent_extraction(self, query: str) -> Dict[str, Any]:
        """Fallback method for intent extraction using simple rules"""
        query_lower = query.lower()
        
        # Simple rule-based intent detection
        if any(keyword in query_lower for keyword in ["produk", "barang", "item", "harga"]):
            if "stok" in query_lower:
                return {"intent": "stok_check", "entities": {}}
            else:
                return {"intent": "produk_info", "entities": {}}
        elif any(keyword in query_lower for keyword in ["status", "pesanan", "order"]):
            return {"intent": "order_status", "entities": {}}
        elif any(keyword in query_lower for keyword in ["pelanggan", "customer", "saya", "pesanan saya"]):
            return {"intent": "customer_orders", "entities": {}}
        elif any(keyword in query_lower for keyword in ["faq", "pertanyaan", "tanya", "informasi"]):
            return {"intent": "faq", "entities": {}}
        else:
            return {"intent": "general", "entities": {}}
    
    def _retrieve_context(self, intent_data: Dict[str, Any]) -> str:
        """Retrieve relevant context based on intent"""
        intent = intent_data.get("intent", "general")
        entities = intent_data.get("entities", {})
        
        context_parts = []
        
        if intent == "produk_info":
            product_id = entities.get("produk_id")
            product_name = entities.get("produk_nama")
            
            if product_id or product_name:
                product_info = self.retriever.retrieve_product_info(
                    product_name=product_name,
                    product_id=product_id
                )
                
                if product_info:
                    context_parts.append(f"Informasi Produk: {json.dumps(product_info, indent=2, ensure_ascii=False)}")
        
        elif intent == "stok_check":
            product_id = entities.get("produk_id")
            product_name = entities.get("produk_nama")
            
            if product_id or product_name:
                product_info = self.retriever.retrieve_product_info(
                    product_name=product_name,
                    product_id=product_id
                )
                
                if product_info:
                    context_parts.append(f"Informasi Stok: Produk '{product_info['nama']}' memiliki stok sebanyak {product_info['stok']} unit.")
        
        elif intent == "order_status":
            order_id = entities.get("pesanan_id")
            
            if order_id:
                order_info = self.retriever.retrieve_order_info(order_id)
                
                if order_info:
                    context_parts.append(f"Informasi Pesanan: {json.dumps(order_info, indent=2, ensure_ascii=False)}")
        
        elif intent == "customer_orders":
            customer_id = entities.get("pelanggan_id")
            
            if customer_id:
                orders = self.retriever.retrieve_customer_orders(customer_id)
                
                if orders:
                    context_parts.append(f"Daftar Pesanan Pelanggan: {json.dumps(orders, indent=2, ensure_ascii=False)}")
        
        elif intent == "faq":
            category = entities.get("kategori")
            query_text = entities.get("query", "")
            
            faqs = self.retriever.retrieve_faq(query=query_text, category=category)
            
            if faqs:
                faq_text = "\n\n".join([f"Q: {faq['pertanyaan']}\nA: {faq['jawaban']}" for faq in faqs])
                context_parts.append(f"Informasi FAQ yang relevan:\n{faq_text}")
        
        # Always add relevant document chunks from vector store
        doc_chunks = self.retriever.retrieve_documents(query=intent_data.get("query", ""))
        
        if doc_chunks:
            context_parts.append("Informasi dari dokumen:")
            for i, chunk in enumerate(doc_chunks, 1):
                context_parts.append(f"Dokumen {i}: {chunk}")
        
        return "\n\n".join(context_parts)
    
    def generate_response(self, query: str) -> str:
        """Generate response based on user query"""
        try:
            # Extract intent
            intent_data = self._extract_intent(query)
            intent_data["query"] = query  # Add original query
            
            logger.info(f"Extracted intent: {intent_data['intent']}")
            
            # Retrieve relevant context
            context = self._retrieve_context(intent_data)
            
            # Generate response using LLM
            prompt = f"""
            Pengguna: {query}
            
            Berdasarkan informasi berikut, berikan respons yang tepat:
            """
            
            response = self._call_ollama_api(prompt, context=context)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Maaf, saya mengalami kesalahan saat memproses permintaan Anda. Mohon coba lagi nanti."