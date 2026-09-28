import 'package:frescapp/models/product.dart';

class CartService {
  static final CartService _instance = CartService._internal();
  factory CartService() => _instance;
  CartService._internal();

  // =========================
  // FUENTE DE VERDAD
  // =========================
  final Map<String, int> _quantities = {};          // sku -> qty
  final Map<String, Product> _snapshots = {};       // sku -> product snapshot

  // =========================
  // INTERNAL HELPERS
  // =========================
  String _safeSku(Product p) {
    final sku = p.sku;
    if (sku == null || sku.isEmpty) {
      throw Exception('CartService: producto sin SKU válido');
    }
    return sku;
  }

  void _ensureSnapshot(Product p) {
    final sku = _safeSku(p);
    final existing = _snapshots[sku];

    if (existing == null) {
      // Copia defensiva (evita aliasing con UI)
      _snapshots[sku] = Product.fromJson(p.toJson());
    } else {
      // Actualiza solo campos relevantes
      existing.name = p.name ?? existing.name;
      existing.image = p.image ?? existing.image;
      existing.category = p.category ?? existing.category;
      existing.priceSale = p.priceSale ?? existing.priceSale;
      existing.finalPrice = p.finalPrice ?? existing.finalPrice;
      existing.hasDiscount = p.hasDiscount || existing.hasDiscount;
      existing.savingsPct = p.savingsPct ?? existing.savingsPct;
    }
  }

  // =========================
  // GETTERS (los “juguerers” 😄)
  // =========================

  /// Lista de productos del carrito (con quantity aplicada)
  List<Product> get items {
    return _quantities.entries.map((e) {
      final sku = e.key;
      final qty = e.value;
      final snap = _snapshots[sku];

      if (snap != null) {
        final p = Product.fromJson(snap.toJson());
        p.quantity = qty;
        return p;
      }
      return Product(sku: sku, quantity: qty);
    }).toList();
  }

  /// Total de unidades (contador del badge)
  int get totalItems =>
      _quantities.values.fold<int>(0, (s, q) => s + q);

  /// Total monetario del carrito
  double get total {
    double sum = 0;
    for (final e in _quantities.entries) {
      final p = _snapshots[e.key];
      final unit = p?.finalPrice ?? p?.priceSale ?? 0;
      sum += unit * e.value;
    }
    return sum;
  }

  /// Ahorro total por descuentos
  double get savings {
    double sum = 0;
    for (final e in _quantities.entries) {
      final p = _snapshots[e.key];
      if (p == null || p.hasDiscount != true) continue;
      final original = p.priceSale ?? 0;
      final finalP = p.finalPrice ?? original;
      sum += (original - finalP) * e.value;
    }
    return sum;
  }

  /// Saber si está vacío
  bool get isEmpty => _quantities.isEmpty;

  /// Cantidad por SKU
  int qtyForSku(String sku) => _quantities[sku] ?? 0;

  // =========================
  // MUTATIONS (perezosas)
  // =========================
  void addProduct(Product p) {
    final sku = _safeSku(p);
    _ensureSnapshot(p);
    _quantities[sku] = (_quantities[sku] ?? 0) + 1;
  }

  void removeProduct(Product p) {
    final sku = _safeSku(p);
    final cur = _quantities[sku] ?? 0;
    if (cur <= 1) {
      _quantities.remove(sku);
      _snapshots.remove(sku);
    } else {
      _quantities[sku] = cur - 1;
    }
  }

  void setQuantity(Product p, int qty) {
    final sku = _safeSku(p);
    if (qty <= 0) {
      _quantities.remove(sku);
      _snapshots.remove(sku);
    } else {
      _ensureSnapshot(p);
      _quantities[sku] = qty;
    }
  }

  /// Refresca snapshot cuando recargas catálogo
  void updateSnapshotFromProduct(Product p) {
    _ensureSnapshot(p);
  }

  /// 🔥 El botón nuclear (lo que te faltaba)
  void clear() {
    _quantities.clear();
    _snapshots.clear();
  }
}
