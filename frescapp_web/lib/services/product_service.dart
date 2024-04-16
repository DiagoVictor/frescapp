import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';

class ProductService {
  //FirebaseApp secondaryApp = Firebase.app('frescapp');
  //FirebaseFirestore firestore = FirebaseFirestore.instanceFor(app: secondaryApp);
  //FirebaseFirestore firestore = FirebaseFirestore.instance;
  //final productsCollection = await db.collection('products').get();

  Future<List<Product>> getProducts() async {
    List<Map<String, dynamic>> productData = [
  {
    "name": "Tomate Chonto Maduración Mixta Parejo Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00001",
    "price_sale": 4320,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Limón Tahití Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00001",
    "price_sale": 6360,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Cebolla Cabezona Blanca Sin Pelar Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00002",
    "price_sale": 2520,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Tomate Chonto Maduro Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00003",
    "price_sale": 4800,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Zanahoria Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00004",
    "price_sale": 3840,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Pimentón Maduración Mixta Estándar (4 cascos) Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00005",
    "price_sale": 4800,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Piña Golden Calibre 7 Unidad",
    "unit": "Unidad",
    "category": "Frutas",
    "sku": "BOG-CAT002-00002",
    "price_sale": 6960,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Papa Criolla Lavada Semi (Mediana) Kg",
    "unit": "KG",
    "category": "Tubérculos",
    "sku": "BOG-CAT003-00001",
    "price_sale": 5520,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Cilantro Atado  (450g - 500g)",
    "unit": "unidad",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00001",
    "price_sale": 3360,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Lechuga Crespa Verde Unidad (200G)",
    "unit": "Unidad",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00002",
    "price_sale": 1800,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Ajo sin pelar Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00006",
    "price_sale": 14400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Papa Pastusa sin lavar seleccionada Kg",
    "unit": "KG",
    "category": "Tubérculos",
    "sku": "BOG-CAT003-00002",
    "price_sale": 3600,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Lechuga Batavia Unidad (500g - 800g)",
    "unit": "Unidad",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00003",
    "price_sale": 4800,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Pepino Cohombro Estándar Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00007",
    "price_sale": 2400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Cebolla Larga Junca Pony Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00008",
    "price_sale": 2160,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Naranja Valencia Kg ",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00003",
    "price_sale": 3840,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Arracacha Kg",
    "unit": "KG",
    "category": "Tubérculos",
    "sku": "BOG-CAT003-00003",
    "price_sale": 6600,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Habichuela Kg ",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00009",
    "price_sale": 4200,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Plátano Verde Hartón Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00004",
    "price_sale": 5400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Maracuyá Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00005",
    "price_sale": 12000,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Ahuyama Unidad (3500g - 4000g)",
    "unit": "Unidad",
    "category": "Verduras",
    "sku": "BOG-CAT001-00010",
    "price_sale": 5160,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Tomate Cherry Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00011",
    "price_sale": 5400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Mazorca con Amero Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00012",
    "price_sale": 7800,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Mango Tommy Mixto Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00006",
    "price_sale": 10800,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Guayaba Maduracion Mixta Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00007",
    "price_sale": 7800,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Cebolla Cabezona Roja Sin Pelar Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00013",
    "price_sale": 5760,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Zuquini Verde Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00014",
    "price_sale": 2400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Maracuyá Pequeña Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00008",
    "price_sale": 9600,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Espinaca Atado (450g - 500g)",
    "unit": "Unidad",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00004",
    "price_sale": 4200,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Zuquini Amarillo Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00015",
    "price_sale": 2400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Lulo Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00009",
    "price_sale": 7200,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Papaya Tainung maduración mixta Unidad (1200g - 1600g)",
    "unit": "Unidad",
    "category": "Frutas",
    "sku": "BOG-CAT002-00010",
    "price_sale": 4080,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Berenjena Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00016",
    "price_sale": 7200,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Brócoli Unidad (250g - 350g)",
    "unit": "UNIDAD",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00005",
    "price_sale": 3000,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Fresa Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00011",
    "price_sale": 11760,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Cebolla Larga Junca Malla Unidad (500g)",
    "unit": "UNIDAD",
    "category": "Verduras",
    "sku": "BOG-CAT001-00017",
    "price_sale": 2400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Lulo Pequeño Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00012",
    "price_sale": 6600,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Perejil Crespo Atado (250g)",
    "unit": "UNIDAD",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00006",
    "price_sale": 2880,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Papa Criolla Sin Lavar Kg",
    "unit": "KG",
    "category": "Tubérculos",
    "sku": "BOG-CAT003-00004",
    "price_sale": 4200,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Pepino de Guiso Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00018",
    "price_sale": 5640,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Acelga Atado (500g)",
    "unit": "UNIDAD",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00007",
    "price_sale": 1020,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Yuca Tamaño Mixto Kg",
    "unit": "KG",
    "category": "Tubérculos",
    "sku": "BOG-CAT003-00005",
    "price_sale": 4320,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Cebolla Cabezona Blanca Limpia Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00019",
    "price_sale": 3600,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Remolacha Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00020",
    "price_sale": 3240,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Repollo Blanco Unidad (1500g - 2000g)",
    "unit": "UNIDAD",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00008",
    "price_sale": 6000,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Perejil Liso Atado (250g)",
    "unit": "UNIDAD",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00009",
    "price_sale": 2880,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Maíz Desgranado",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00021",
    "price_sale": 10200,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Lechuga Crespa Morada Unidad (200g)",
    "unit": "UNIDAD",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00010",
    "price_sale": 2400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Papa Sabanera Kg",
    "unit": "KG",
    "category": "Tubérculos",
    "sku": "BOG-CAT003-00006",
    "price_sale": 5640,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Tomate Larga Vida Maduracion Mixta Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00022",
    "price_sale": 6600,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Apio Atado (500g - 800g)",
    "unit": "UNIDAD",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00011",
    "price_sale": 2400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Manzana Verde Kg",
    "unit": "KG",
    "category": "Frutas",
    "sku": "BOG-CAT002-00013",
    "price_sale": 20400,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Plátano Colicero Verde Kg",
    "unit": "KG",
    "category": "Verduras",
    "sku": "BOG-CAT001-00023",
    "price_sale": 3240,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Calabacín Unidad (400g - 600g)",
    "unit": "UNIDAD",
    "category": "Verduras",
    "sku": "BOG-CAT001-00024",
    "price_sale": 3000,
    "iva": false,
    "iva_value": 0
  },
  {
    "name": "Lechuga Rúgula Unidad (500g)",
    "unit": "UNIDAD",
    "category": "Hortalizas",
    "sku": "BOG-CAT004-00012",
    "price_sale": 4200,
    "iva": false,
    "iva_value": 0
  }
    ];

    // Crear una lista de productos a partir de los datos simulados
    List<Product> products = productData.map((data) => Product.fromMap(data)).toList();

    return products;
  }
}


class Product {
  final String name;
  final String category;
  final double price_sale;
  final bool iva;
  final double iva_value;
  final String sku;
  final String unit;

  Product({
    required this.name,
    required this.category,
    required this.price_sale,
    required this.iva,
    required this.iva_value,
    required this.sku,
    required this.unit
  });

  factory Product.fromDocument(DocumentSnapshot doc) {
    return Product(
      name: doc['name'],
      category: doc['category'],
      price_sale: doc['price_sale'],
      iva: doc['iva'],
      iva_value: doc['iva_value'],
      sku: doc['sku'],
      unit: doc['unit']
    );
  }
   factory Product.fromMap(Map<String, dynamic> map) {
    return Product(
      name: map['name'],
      unit: map['unit'],
      category: map['category'],
      sku: map['sku'],
      price_sale: map['price_sale'].toDouble(), 
      iva:  map['iva'],
      iva_value: map['iva_value']
    );
  }
}