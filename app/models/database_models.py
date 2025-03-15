from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class Produk(Base):
    __tablename__ = "produk"
    
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255), nullable=False)
    deskripsi = Column(Text, nullable=True)
    kategori = Column(String(100), nullable=False)
    harga = Column(Float, nullable=False)
    stok = Column(Integer, default=0)
    gambar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    pesanan_items = relationship("PesananItem", back_populates="produk")

class Pelanggan(Base):
    __tablename__ = "pelanggan"
    
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    telepon = Column(String(20), nullable=True)
    alamat = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    pesanan = relationship("Pesanan", back_populates="pelanggan")

class Pesanan(Base):
    __tablename__ = "pesanan"
    
    id = Column(Integer, primary_key=True, index=True)
    pelanggan_id = Column(Integer, ForeignKey("pelanggan.id"), nullable=False)
    tanggal_pesanan = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")
    total_harga = Column(Float, default=0.0)
    alamat_pengiriman = Column(Text, nullable=True)
    catatan = Column(Text, nullable=True)
    
    # Relationships
    pelanggan = relationship("Pelanggan", back_populates="pesanan")
    pesanan_items = relationship("PesananItem", back_populates="pesanan")

class PesananItem(Base):
    __tablename__ = "pesanan_item"
    
    id = Column(Integer, primary_key=True, index=True)
    pesanan_id = Column(Integer, ForeignKey("pesanan.id"), nullable=False)
    produk_id = Column(Integer, ForeignKey("produk.id"), nullable=False)
    jumlah = Column(Integer, default=1)
    harga_satuan = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    # Relationships
    pesanan = relationship("Pesanan", back_populates="pesanan_items")
    produk = relationship("Produk", back_populates="pesanan_items")

class FAQ(Base):
    __tablename__ = "faq"
    
    id = Column(Integer, primary_key=True, index=True)
    pertanyaan = Column(Text, nullable=False)
    jawaban = Column(Text, nullable=False)
    kategori = Column(String(100), nullable=True)
    aktif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)