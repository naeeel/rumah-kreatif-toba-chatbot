from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import database_models as models

# Dependency to check if a product exists
def get_produk_or_404(produk_id: int, db: Session = Depends(get_db)):
    produk = db.query(models.Produk).filter(models.Produk.id == produk_id).first()
    if not produk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produk dengan ID {produk_id} tidak ditemukan"
        )
    return produk

# Dependency to check if a customer exists
def get_pelanggan_or_404(pelanggan_id: int, db: Session = Depends(get_db)):
    pelanggan = db.query(models.Pelanggan).filter(models.Pelanggan.id == pelanggan_id).first()
    if not pelanggan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pelanggan dengan ID {pelanggan_id} tidak ditemukan"
        )
    return pelanggan

# Dependency to check if an order exists
def get_pesanan_or_404(pesanan_id: int, db: Session = Depends(get_db)):
    pesanan = db.query(models.Pesanan).filter(models.Pesanan.id == pesanan_id).first()
    if not pesanan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pesanan dengan ID {pesanan_id} tidak ditemukan"
        )
    return pesanan