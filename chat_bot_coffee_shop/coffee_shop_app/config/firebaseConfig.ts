import { initializeApp } from 'firebase/app';
import { getDatabase } from 'firebase/database';
import { getStorage } from 'firebase/storage';

// Configuración Firebase desde .env
const firebaseConfig = {
  apiKey: process.env.EXPO_PUBLIC_FIREBASE_API_KEY as string,
  authDomain: process.env.EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN as string,
  databaseURL: process.env.EXPO_PUBLIC_FIREBASE_DATABASE_URL as string,
  projectId: process.env.EXPO_PUBLIC_FIREBASE_PROJECT_ID as string, // Corregido
  storageBucket: process.env.EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET as string,
  appId: process.env.EXPO_PUBLIC_FIREBASE_APP_ID as string,
  measurementId: process.env.EXPO_PUBLIC_FIREBASE_MEASUREMENT_ID as string,
};

const app = initializeApp(firebaseConfig);

// Exporta servicios que estás usando
export const fireBaseDB = getDatabase(app);
export const storage = getStorage(app);
