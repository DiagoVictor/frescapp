import { Component, OnInit } from '@angular/core';
import { ProductService } from '../services/product.service';
import { Router } from '@angular/router';
import * as XLSX from 'xlsx';
import * as FileSaver from 'file-saver';
@Component({
  selector: 'app-products',
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent implements OnInit {
  products: any[] = [];
  filteredProducts: any[] = [];
  searchText: string = '';
  product: any = {};
  actionTipo: any = '';
  successMessage: string = '';
  errorMessage: string = '';

  constructor(private productService: ProductService, private router: Router) { }

  ngOnInit(): void {
    // Verificar si el usuario está autenticado
    const isLoggedIn = this.checkIfLoggedIn();

    if (!isLoggedIn) {
      // Si no está autenticado, redirigir al usuario a la página de inicio de sesión
      this.router.navigate(['/login']);
    } else {
      // Si está autenticado, cargar los productos
      this.getProducts();
    }
  }

  // Función para verificar si el usuario está autenticado (puedes implementar tu propia lógica aquí)
  checkIfLoggedIn(): boolean {
    // Por ejemplo, podrías verificar si existe un token de autenticación en el almacenamiento local
    const token = localStorage.getItem('token');
    return !!token; // Devuelve true si hay un token, de lo contrario false
  }

  getProducts(): void {
    this.productService.getProducts()
      .subscribe(products => {
        this.products = products;
        this.filteredProducts = products; // Inicializa la lista de productos filtrados con todos los productos al principio
        this.filterProducts(); // Filtra los productos basados en el texto de búsqueda inicial
      });
  }

  filterProducts(): void {
    if (this.searchText.trim() !== '') {
      this.filteredProducts = this.products.filter(product => {
        // Filtra los productos cuyo nombre contiene el texto de búsqueda
        return product.name.toLowerCase().includes(this.searchText.toLowerCase());
      });
    } else {
      // Si no hay texto de búsqueda, muestra todos los productos
      this.filteredProducts = this.products;
    }
  }

  openEditModal(product: any, tipo: any): void {
    this.product = product;
    this.actionTipo = tipo;
  }

  updated_product(): void {
    // Convierte los campos price_sale, price_purchase, margen, discount y iva_value a tipo decimal
    this.product.price_sale = parseFloat(this.product.price_sale);
    this.product.price_purchase = parseFloat(this.product.price_purchase);
    this.product.margen = parseFloat(this.product.margen);
    this.product.discount = parseFloat(this.product.discount);
    this.product.iva_value = parseFloat(this.product.iva_value);

    // Convierte el campo iva a tipo boolean
    this.product.iva = this.product.iva === 'true' ? true : false;

    // Llama al servicio para actualizar el producto
    this.productService.updateProduct(this.product.id, this.product).subscribe((data: any) => {
      // Lógica después de actualizar el producto, si es necesario
      this.successMessage = '¡Producto actualizado correctamente!';
      this.getProducts();
      setTimeout(() => {
        this.successMessage = ''; // Reiniciar el mensaje después de unos segundos
      }, 3000); // Mostrar el mensaje durante 3 segundos
    });

  }

  created_product(): void {
    // Convierte los campos price_sale y price_purchase a tipo number
    this.product.price_sale = +this.product.price_sale;
    this.product.price_purchase = +this.product.price_purchase;

    // Convierte el campo iva a tipo boolean
    this.product.iva = this.product.iva === 'true' ? true : false;
    this.productService.createProduct(this.product).subscribe((data: any) => {
    });
    this.getProducts(); // Actualiza la lista de productos después de crear uno
  }
  camposCompletos(): boolean {
    const { name, unit, category, sku, price_sale, price_purchase, discount, margen, iva, iva_value, description, image, status } = this.product;
    return !!name && !!unit && !!category && !!sku && !!price_sale && !!image && !!status;
  }
  syncSheet(): void {
    this.productService.syncSheet().subscribe((res:any) => {
        if (res.status === 200 || res.status === undefined) {
          this.successMessage = '¡Sincronización exitosa!';
          this.getProducts();
          setTimeout(() => {
            this.successMessage = ''; // Reiniciar el mensaje después de unos segundos
          }, 3000); // Mostrar el mensaje durante 3 segundos
        } else {
          this.errorMessage = 'Error en la sincronización.';
          setTimeout(() => {
            this.errorMessage = ''; // Reiniciar el mensaje después de unos segundos
          }, 3000); // Mostrar el mensaje durante 3 segundos
        }
      })
    }
    downloadProductFormat() {
      const EXCEL_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
      const EXCEL_EXTENSION = '.xlsx';
      
      // Estructura de datos para las columnas requeridas
      const worksheetData = this.products.map((product: { 
        sku: any; 
        name: any; 
        category: string[]; 
        unit: string[]; 
        image: string[]; 
        price_sale: number;
      }) => ({
        SKU: product.sku,
        Nombre: product.name,
        Precio_normal: product.price_sale,
        Categorías: product.category,
        Etiquetas: product.unit,
        Imágenes: product.image
      }));
    
      // Crear hoja de cálculo a partir del JSON
      const worksheet = XLSX.utils.json_to_sheet(worksheetData);
      const workbook = { Sheets: { 'Productos': worksheet }, SheetNames: ['Productos'] };
    
      // Convertir el workbook en un array binario para descargar
      const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    
      // Crear archivo Blob y descargar
      const data: Blob = new Blob([excelBuffer], { type: EXCEL_TYPE });
      const fileName = 'Productos_Format.xlsx';
      FileSaver.saveAs(data, fileName);
    }
}
