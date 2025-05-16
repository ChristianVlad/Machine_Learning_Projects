import { fireBaseDB } from '../config/firebaseConfig';
import { Product } from '../types/types';
import { ref, get } from 'firebase/database';

const fetchProducts = async (): Promise<Product[]> => {
  const snapshot = await get(ref(fireBaseDB, 'products'));
  const data = snapshot.val();

  const products: Product[] = [];

  if (data) {
    for (const key in data) {
      if (Object.prototype.hasOwnProperty.call(data, key)) {
        products.push({
          ...data[key],
          id: key, // Asegúrate de agregar el 'id' del producto
        });
      }
    }
  }

  return products;
};

export { fetchProducts };
