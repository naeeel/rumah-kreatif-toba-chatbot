import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import database_models as models
from app.rag.embedder import initialize_vector_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGRetriever:
    def __init__(self):
        self.vector_db = initialize_vector_db()
    
    def retrieve_documents(self, query: str, k: int = 3) -> List[str]:
        """Retrieve relevant document chunks from vector database"""
        if not self.vector_db:
            logger.warning("Vector database not initialized")
            return []
        
        try:
            # Search for similar documents
            docs = self.vector_db.similarity_search(query, k=k)
            
            # Extract content from documents
            content = [doc.page_content for doc in docs]
            logger.info(f"Retrieved {len(content)} document chunks for query: {query}")
            return content
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def retrieve_product_info(self, product_name: str = None, product_id: int = None) -> Optional[Dict[str, Any]]:
        """Retrieve product information from database"""
        db = SessionLocal()
        try:
            query = db.query(models.Produk)
            
            if product_id:
                produk = query.filter(models.Produk.id == product_id).first()
            elif product_name:
                produk = query.filter(models.Produk.nama.ilike(f"%{product_name}%")).first()
            else:
                logger.warning("No product name or ID provided")
                return None
            
            if produk:
                return {
                    "id": produk.id,
                    "nama": produk.nama,
                    "deskripsi": produk.deskripsi,
                    "kategori": produk.kategori,
                    "harga": produk.harga,
                    "stok": produk.stok
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving product info: {str(e)}")
            return None
        finally:
            db.close()
    
    def retrieve_order_info(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve order information from database"""
        db = SessionLocal()
        try:
            pesanan = db.query(models.Pesanan).filter(models.Pesanan.id == order_id).first()
            
            if pesanan:
                # Get order items
                items = db.query(models.PesananItem).filter(models.PesananItem.pesanan_id == order_id).all()
                item_list = []
                
                for item in items:
                    produk = db.query(models.Produk).filter(models.Produk.id == item.produk_id).first()
                    item_list.append({
                        "produk_nama": produk.nama if produk else "Unknown",
                        "jumlah": item.jumlah,
                        "harga_satuan": item.harga_satuan,
                        "subtotal": item.subtotal
                    })
                
                return {
                    "id": pesanan.id,
                    "pelanggan_id": pesanan.pelanggan_id,
                    "tanggal_pesanan": pesanan.tanggal_pesanan,
                    "status": pesanan.status,
                    "total_harga": pesanan.total_harga,
                    "items": item_list
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving order info: {str(e)}")
            return None
        finally:
            db.close()
    
    def retrieve_customer_orders(self, customer_id: int) -> List[Dict[str, Any]]:
        """Retrieve all orders for a specific customer"""
        db = SessionLocal()
        try:
            orders = db.query(models.Pesanan).filter(models.Pesanan.pelanggan_id == customer_id).all()
            
            result = []
            for order in orders:
                result.append({
                    "id": order.id,
                    "tanggal_pesanan": order.tanggal_pesanan,
                    "status": order.status,
                    "total_harga": order.total_harga
                })
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving customer orders: {str(e)}")
            return []
        finally:
            db.close()
    
    def retrieve_faq(self, query: str = None, category: str = None) -> List[Dict[str, Any]]:
        """Retrieve FAQs from database"""
        db = SessionLocal()
        try:
            db_query = db.query(models.FAQ).filter(models.FAQ.aktif == True)
            
            if category:
                db_query = db_query.filter(models.FAQ.kategori == category)
            
            faqs = db_query.all()
            
            # If query is provided, filter FAQs by relevance to query
            if query and faqs:
                # Use vector search to find most relevant FAQs
                # This is a simplified approach - in a real system, you'd want to embed the FAQs
                faq_texts = [f"Pertanyaan: {faq.pertanyaan}\nJawaban: {faq.jawaban}" for faq in faqs]
                relevant_indices = []
                
                if self.vector_db:
                    # Use vector search for relevance
                    documents = self.vector_db.similarity_search(query, k=min(5, len(faqs)))
                    
                    # Extract FAQ indices from document metadata (simplified)
                    # In a real implementation, you'd store FAQ IDs in document metadata
                    relevant_indices = list(range(min(5, len(faqs))))
                else:
                    # Fallback to simple keyword matching
                    relevant_indices = [i for i, text in enumerate(faq_texts) 
                                       if query.lower() in text.lower()]
                
                # Get the relevant FAQs
                relevant_faqs = [faqs[i] for i in relevant_indices if i < len(faqs)]
                faqs = relevant_faqs if relevant_faqs else faqs[:5]
            
            return [{
                "id": faq.id,
                "pertanyaan": faq.pertanyaan,
                "jawaban": faq.jawaban,
                "kategori": faq.kategori
            } for faq in faqs]
        except Exception as e:
            logger.error(f"Error retrieving FAQs: {str(e)}")
            return []
        finally:
            db.close()