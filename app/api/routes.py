from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models import database_models as models
from app.api import dependencies as deps

router = APIRouter()

@router.get("/produk", tags=["Produk"])
def get_produk_list(
    skip: int = 0, 
    limit: int = 100, 
    kategori: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Mengambil daftar produk dengan opsi filter berdasarkan kategori"""
    query = db.query(models.Produk)
    
    if kategori:
        query = query.filter(models.Produk.kategori == kategori)
    
    return query.offset(skip).limit(limit).all()

@router.get("/produk/{produk_id}", tags=["Produk"])
def get_produk_detail(produk_id: int, db: Session = Depends(get_db)):
    """Mengambil detail produk berdasarkan ID"""
    produk = db.query(models.Produk).filter(models.Produk.id == produk_id).first()
    if not produk:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return produk

@router.get("/produk/{produk_id}/stok", tags=["Produk"])
def get_produk_stok(produk_id: int, db: Session = Depends(get_db)):
    """Mengecek stok produk berdasarkan ID"""
    produk = db.query(models.Produk).filter(models.Produk.id == produk_id).first()
    if not produk:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return {"produk_id": produk_id, "nama": produk.nama, "stok": produk.stok}

@router.get("/pesanan/{pesanan_id}", tags=["Pesanan"])
def get_pesanan_detail(pesanan_id: int, db: Session = Depends(get_db)):
    """Mengambil detail pesanan berdasarkan ID"""
    pesanan = db.query(models.Pesanan).filter(models.Pesanan.id == pesanan_id).first()
    if not pesanan:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
    return pesanan

@router.get("/pelanggan/{pelanggan_id}/pesanan", tags=["Pelanggan"])
def get_pelanggan_pesanan(
    pelanggan_id: int, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Mengambil daftar pesanan milik pelanggan"""
    # Check if customer exists
    pelanggan = db.query(models.Pelanggan).filter(models.Pelanggan.id == pelanggan_id).first()
    if not pelanggan:
        raise HTTPException(status_code=404, detail="Pelanggan tidak ditemukan")
    
    # Query orders
    query = db.query(models.Pesanan).filter(models.Pesanan.pelanggan_id == pelanggan_id)
    
    if status:
        query = query.filter(models.Pesanan.status == status)
    
    return query.all()

@router.get("/faq", tags=["FAQ"])
def get_faq_list(
    skip: int = 0, 
    limit: int = 100, 
    kategori: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Mengambil daftar FAQ dengan opsi filter berdasarkan kategori"""
    query = db.query(models.FAQ).filter(models.FAQ.aktif == True)
    
    if kategori:
        query = query.filter(models.FAQ.kategori == kategori)
    
    return query.offset(skip).limit(limit).all()